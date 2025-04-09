import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import argparse
import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

# Load .env from parent directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client = None
if os.getenv("LLAMA_BASE_URL") and os.getenv("LLAMA_API_KEY"):
    client = OpenAI(base_url=os.getenv("LLAMA_BASE_URL"), api_key=os.getenv("LLAMA_API_KEY"))

def scrape_bio_text(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 60]
        return "\n".join(lines[:20])
    except Exception as e:
        return f"Error scraping {url}: {e}"

def score_url(url, name, allow_fallback=False):
    if not url:
        return -1
    url = url.lower()
    name_parts = name.lower().split()
    score = 0

    if not allow_fallback:
        if ".com" not in url:
            return -1
        if any(bad in url for bad in ["ballotpedia", "pbs", "wikipedia", ".gov", "linkedin", "youtube", "facebook", "x.com"]):
            return -1
        if not any(part in url for part in name_parts):
            return -1

    if "for" in url or "elect" in url or "vote" in url:
        score += 2
    if "senate" in url or "house" in url or "justice" in url or "court" in url:
        score += 1
    if all(part in url for part in name_parts):
        score += 3

    return score

def search_duckduckgo(candidate_name, allow_fallback=False):
    queries = [
        f"{candidate_name} official campaign site",
        f"{candidate_name} official site",
        f"{candidate_name} for office",
        f"elect {candidate_name}",
        f"{candidate_name} campaign website"
    ]

    results = []
    with DDGS() as ddgs:
        for query in queries:
            search_results = ddgs.text(query, max_results=5)
            for res in search_results:
                url = res.get("href") or res.get("url")
                title = res.get("title")
                snippet = res.get("body")
                results.append({"title": title, "url": url, "snippet": snippet})

    return results[:5]

def ask_llama_for_best_url(results, candidate_name):
    prompt = f"Given these search results for {candidate_name}, identify which number is the official campaign website:\n\n"
    for idx, result in enumerate(results, start=1):
        prompt += f"{idx}. Title: {result['title']}\nURL: {result['url']}\nSnippet: {result['snippet']}\n\n"
    prompt += "Respond ONLY with the number of the best official campaign website. If unsure, respond with '0'."

    response = client.chat.completions.create(
        model="llama-3.3-instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1
    )

    choice = response.choices[0].message.content.strip()
    return int(choice) if choice.isdigit() else 0

def pick_best_url(results, candidate_name, use_llm, allow_fallback):
    if use_llm and client:
        choice = ask_llama_for_best_url(results, candidate_name)
        if choice > 0:
            return results[choice - 1]['url']
        return None
    else:
        best_score = -1
        best_url = None
        for r in results:
            score = score_url(r['url'], candidate_name, allow_fallback)
            if score > best_score:
                best_score = score
                best_url = r['url']
        return best_url

# ✅ NEW FUNCTION for importing
def scrape_candidate_website(name: str, use_llm: bool = False, allow_fallback: bool = False) -> tuple[str, str]:
    results = search_duckduckgo(name, allow_fallback=allow_fallback)
    best_url = pick_best_url(results, name, use_llm=use_llm, allow_fallback=allow_fallback)
    if best_url:
        bio = scrape_bio_text(best_url)
        return (best_url, bio)
    return (None, "")

# CLI still works
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Candidate name")
    parser.add_argument("--allow-fallback", action="store_true", help="Allow fallback to non-official sources")
    parser.add_argument("--use-llm", action="store_true", help="Use LLM to select best URL")
    args = parser.parse_args()

    candidate_name = args.name
    url, bio = scrape_candidate_website(candidate_name, use_llm=args.use_llm, allow_fallback=args.allow_fallback)

    print("\n🔎 Candidate Scrape Result:")
    print(f"Name: {candidate_name}")
    print(f"Chosen URL: {url or 'None'}")
    print(f"\n📄 Bio:\n{bio[:1000]}...")
