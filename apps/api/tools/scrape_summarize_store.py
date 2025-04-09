import argparse
import requests
import json
from candidate_scraper import scrape_candidate_sources
from candidate_builder import CandidateBuilder

def call_llm_generate_summary(name: str, office: str, sources: dict) -> dict:
    print("🔁 Sending text to LLM for summarization...")
    clean_sources = {k: v for k, v in sources.items() if v is not None}
    res = requests.post(
        "http://localhost:8000/generate-summary",
        json={
            "name": name,
            "office": office,
            "sources": clean_sources
        }
    )
    res.raise_for_status()
    return res.json()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Candidate name")
    parser.add_argument("--office", required=True, help="Office they're running for")
    parser.add_argument("--use-llm", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    name = args.name
    office = args.office

    sources = scrape_candidate_sources(name, use_llm=args.use_llm, force_refresh=args.force_refresh)
    print("🧾 Payload Sent to LLM API:")
    print(json.dumps({"name": name, "office": office, "sources": sources}, indent=2))

    summary = call_llm_generate_summary(name, office, sources)
    print("✅ LLM Summary Result:")
    print(json.dumps(summary, indent=2))

    candidate = CandidateBuilder(name, office, sources, summary).build()

    print("Debug Dump:")
    print(json.dumps(candidate, indent=2))

    if args.dry_run:
        print("🧪 [Dry Run] Candidate payload:")
        print(json.dumps(candidate, indent=2))
    else:
        print("📤 Posting candidate to backend...")
        res = requests.post("http://localhost:8000/candidates/", json=candidate)
        res.raise_for_status()
        print("✅ Candidate created:", res.json())

if __name__ == "__main__":
    main()
