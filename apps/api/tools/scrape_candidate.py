import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import argparse
import os
import json
import random
import time
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
from slugify import slugify
from urllib.parse import urljoin, urlparse
from llm import call_llm

# Load .env from parent directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client = None
if os.getenv("LLAMA_BASE_URL") and os.getenv("LLAMA_API_KEY"):
    client = OpenAI(base_url=os.getenv("LLAMA_BASE_URL"), api_key=os.getenv("LLAMA_API_KEY"))

DEBUG_SCRAPER = True

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X)"
]

BANNED_DOMAINS = {"truthtopowerpac.com", "secure.actblue.com", "winred.com"}
ALWAYS_TRUST_DOMAINS = {"opensecrets.org", "ballotpedia.org", "en.wikipedia.org"}

def classify_source(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if "ballotpedia.org" in domain:
        return "BALLOTPEDIA"
    domain_main = domain.replace("www.", "").split(".")[0]
    return domain_main.upper()

def identify_true_official(sources: list[dict], candidate_name: str) -> int:
    numbered_list = "\n".join([f"{i+1}. {s['label']} - {s['url']}" for i, s in enumerate(sources)])
    prompt = f"""
Given the following list of websites about {candidate_name}, which one appears to be the candidate's official campaign website?

Return ONLY the number of the best match.

{numbered_list}
"""
    response = call_llm(prompt)
    try:
        return int(response.strip()) - 1
    except:
        return -1

def deduplicate_urls(results: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for res in results:
        parsed = urlparse(res["url"])
        norm_url = f"{parsed.netloc.lower()}{parsed.path.rstrip('/').lower()}"
        if norm_url not in seen:
            seen.add(norm_url)
            unique.append(res)
    return unique

def is_low_value_text(text: str, url: str) -> bool:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if any(blocked in domain for blocked in BANNED_DOMAINS):
        return True
    if domain in ALWAYS_TRUST_DOMAINS:
        return False
    if not text or len(text.split()) < 50:
        return True
    if len(text) < 1000:
        return True
    boilerplate = ["sign up", "unsubscribe", "message and data rates", "recurring donation", "join our team"]
    return sum(kw in text.lower() for kw in boilerplate) >= 3

def extract_clean_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 60]
    return "\n".join(lines[:20])

def is_internal_link(href: str, base_domain: str) -> bool:
    if href.startswith("/"):
        return True
    try:
        parsed = urlparse(href)
        return base_domain in parsed.netloc
    except:
        return False

def crawl_site(base_url: str, max_pages=10, max_depth=2):
    visited = set()
    queue = [(base_url, 0)]
    results = []

    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc

    while queue and len(results) < max_pages:
        url, depth = queue.pop(0)
        if url in visited or depth > max_depth:
            continue
        visited.add(url)

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except Exception as e:
            print(f"⚠️ Error fetching {url}: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        text = extract_clean_text(soup)
        if not text or len(text.split()) < 50:
            continue

        results.append({"url": url, "text": text})

        for tag in soup.find_all("a", href=True):
            href = tag['href']
            full_url = urljoin(url, href)
            if is_internal_link(full_url, base_domain):
                full_url = full_url.split("#")[0]
                if full_url not in visited:
                    queue.append((full_url, depth + 1))

    return results

def scrape_candidate_sources(name: str, use_llm: bool = False, allow_fallback: bool = False, force_refresh: bool = False) -> dict:
    raw_results = search_duckduckgo(name, allow_fallback=allow_fallback, force_refresh=force_refresh)

    labeled_results = []
    for res in raw_results:
        label = classify_source(res["url"])
        labeled_results.append({
            "label": label,
            "title": res["title"],
            "url": res["url"],
            "snippet": res["snippet"]
        })

    official_url = None
    if use_llm:
        idx = identify_true_official(labeled_results, name)
        if 0 <= idx < len(labeled_results):
            labeled_results[idx]["label"] = "OFFICIAL"
            official_url = labeled_results[idx]["url"]
            official_domain = urlparse(official_url).netloc.lower()
            for r in labeled_results:
                if urlparse(r["url"]).netloc.lower() == official_domain:
                    r["label"] = "OFFICIAL"

    labeled_results = deduplicate_urls(labeled_results)

    print("\n🔎 Classified Search Results:")
    for r in labeled_results:
        print(f"[{r['label']:<12}] {r['title']}\n→ {r['url']}\n")

    sources = {
        "official": None,
        "ballotpedia": None,
        "news": []
    }

    for result in labeled_results:
        url = result["url"]
        label = result["label"].lower()

        if label == "official" and sources["official"] is None:
            print(f"🌐 Crawling official domain: {url}")
            crawled = crawl_site(url, max_pages=8, max_depth=2)
            if crawled:
                sources["official"] = crawled[0]
                sources["news"].extend(crawled[1:])
            continue

        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            response = requests.get(url, timeout=10, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            text = extract_clean_text(soup)

            if DEBUG_SCRAPER:
                print(f"🔍 Text Preview ({url}):\n{text[:300].replace(chr(10), ' ')}\n")

            if is_low_value_text(text, url):
                if DEBUG_SCRAPER:
                    print(f"⚠️ Skipping low-value page: {url}")
                continue

            if label == "ballotpedia" and sources["ballotpedia"] is None:
                sources["ballotpedia"] = {"url": url, "text": text}
            else:
                sources["news"].append({"url": url, "text": text})
        except Exception as e:
            print(f"⚠️ Error processing {url}: {e}")

    return sources

def search_duckduckgo(candidate_name: str, allow_fallback=False, force_refresh=False):
    os.makedirs(".search_cache", exist_ok=True)
    cache_file = f".search_cache/{slugify(candidate_name)}.json"

    if not force_refresh and os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            print("💾 Loaded search results from cache.")
            return json.load(f)

    print("🌐 Performing live DuckDuckGo search...")
    queries = [
        f"{candidate_name} official campaign site",
        f"{candidate_name} official site",
        f"{candidate_name} for office",
        f"elect {candidate_name}",
        f"{candidate_name} campaign website"
    ]

    results = []
    headers = {"User-Agent": random.choice(USER_AGENTS)}

    with DDGS() as ddgs:
        for query in queries:
            search_results = ddgs.text(query, max_results=5)
            for res in search_results:
                url = res.get("href") or res.get("url")
                title = res.get("title", "")
                snippet = res.get("body", "")
                results.append({"title": title, "url": url, "snippet": snippet})
            time.sleep(random.uniform(1.5, 3.0))

    with open(cache_file, "w") as f:
        json.dump(results, f, indent=2)
        print(f"📁 Cached search results → {cache_file}")

    return results[:10]
