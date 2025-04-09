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
from slugify import slugify  # pip install python-slugify

# Load .env from parent directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client = None
if os.getenv("LLAMA_BASE_URL") and os.getenv("LLAMA_API_KEY"):
    client = OpenAI(base_url=os.getenv("LLAMA_BASE_URL"), api_key=os.getenv("LLAMA_API_KEY"))

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X)"
]

def classify_source_type(url: str, title: str = "", snippet: str = "") -> str:
    url = url.lower()
    title = title.lower()
    snippet = snippet.lower()

    if "ballotpedia.org" in url:
        return "ballotpedia"
    if any(social in url for social in ["twitter.com", "facebook.com", "instagram.com", "linkedin.com"]):
        return "social"
    if any(news in url for news in ["npr.org", "apnews.com", "reuters.com", "politico.com", "nytimes.com"]):
        return "news"
    if "official" in title or "campaign" in title or "elect" in url or "vote" in url:
        return "official"
    if any(keyword in snippet for keyword in ["platform", "endorsement", "running for", "candidate"]):
        return "news"
    return "unknown"

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
    headers = { "User-Agent": random.choice(USER_AGENTS) }

    with DDGS() as ddgs:
        for query in queries:
            search_results = ddgs.text(query, max_results=5)
            for res in search_results:
                url = res.get("href") or res.get("url")
                title = res.get("title", "")
                snippet = res.get("body", "")
                source_type = classify_source_type(url, title, snippet)

                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "type": source_type
                })

            time.sleep(random.uniform(1.5, 3.0))  # Avoid rate limits

    with open(cache_file, "w") as f:
        json.dump(results, f, indent=2)
        print(f"📁 Cached search results → {cache_file}")

    return results[:10]

def scrape_bio_text(url):
    try:
        headers = { "User-Agent": random.choice(USER_AGENTS) }
        response = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 60]
        return "\n".join(lines[:20])
    except Exception as e:
        return f"Error scraping {url}: {e}"

def scrape_candidate_sources(name: str, use_llm: bool = False, allow_fallback: bool = False, force_refresh: bool = False) -> dict:
    results = search_duckduckgo(name, allow_fallback=allow_fallback, force_refresh=force_refresh)

    print("\n🔎 Classified Search Results:")
    for r in results:
        print(f"[{r['type'].upper():10}] {r['title']}\n→ {r['url']}\n")

    sources = {
        "official": None,
        "ballotpedia": None,
        "news": []
    }

    for result in results:
        url = result["url"]
        kind = result["type"]

        if kind == "official" and sources["official"] is None:
            text = scrape_bio_text(url)
            sources["official"] = { "url": url, "text": text }

        elif kind == "ballotpedia" and sources["ballotpedia"] is None:
            text = scrape_bio_text(url)
            sources["ballotpedia"] = { "url": url, "text": text }

        elif kind == "news":
            text = scrape_bio_text(url)
            sources["news"].append({ "url": url, "text": text })

    return sources

# CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Candidate name")
    parser.add_argument("--allow-fallback", action="store_true", help="Allow fallback to non-official sources")
    parser.add_argument("--use-llm", action="store_true", help="Use LLM to select best URL")
    parser.add_argument("--force-refresh", action="store_true", help="Force re-run search (ignore cache)")
    args = parser.parse_args()

    candidate_name = args.name
    sources = scrape_candidate_sources(
        candidate_name,
        use_llm=args.use_llm,
        allow_fallback=args.allow_fallback,
        force_refresh=args.force_refresh
    )

    print("\n📦 Final Scraped Sources Summary:")
    for key, val in sources.items():
        if val is None:
            print(f"{key.upper()}: ❌ Not Found")
        elif isinstance(val, list):
            print(f"{key.upper()}: {len(val)} item(s)")
        else:
            preview = val['text'][:300].replace("\n", " ") + "..."
            print(f"{key.upper()}: ✅ {val['url']}\n    → {preview}\n")
