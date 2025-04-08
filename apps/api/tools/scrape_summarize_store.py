import requests
import argparse
import os
from dotenv import load_dotenv
from pathlib import Path
from scrape_candidate import search_duckduckgo, pick_best_url, scrape_bio_text

# Load .env from parent directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

API_BASE_URL = os.getenv("API_BASE_URL")

def generate_summary(name, office, bio_text):
    payload = {
        "name": name,
        "office": office,
        "bio_text": bio_text
    }
    response = requests.post(f"{API_BASE_URL}/generate-summary", json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Summary generation failed: {response.status_code}, {response.text}")

def save_candidate(summary):
    response = requests.post(f"{API_BASE_URL}/candidates/", json=summary)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Saving candidate failed: {response.status_code}, {response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Candidate name")
    parser.add_argument("--office", required=True, help="Office the candidate is running for")
    parser.add_argument("--allow-fallback", action="store_true", help="Allow fallback sources for scraping")
    parser.add_argument("--use-llm", action="store_true", help="Use LLM to verify official URL")
    args = parser.parse_args()

    print(f"🔍 Scraping official website for: {args.name}")

    results = search_duckduckgo(args.name, allow_fallback=args.allow_fallback)
    best_url = pick_best_url(results, args.name, args.use_llm, args.allow_fallback)

    if not best_url:
        print("❌ No suitable official website found.")
        exit(1)

    bio_text = scrape_bio_text(best_url)
    print(f"✅ Bio text scraped from {best_url[:50]}...")

    print("🧠 Generating summary via LLM...")
    summary = generate_summary(args.name, args.office, bio_text)

    print("💾 Saving candidate to database...")
    save_response = save_candidate(summary)

    print(f"🎉 Candidate '{args.name}' successfully saved.")
    print(f"Candidate ID: {save_response.get('id')}")