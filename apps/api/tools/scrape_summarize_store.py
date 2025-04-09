import argparse
import requests
import json
from scrape_candidate import scrape_candidate_website

def call_llm_generate_summary(name: str, office: str, bio_text: str) -> dict:
    print("🔁 Sending text to LLM for summarization...")
    res = requests.post(
        "http://localhost:8000/generate-summary",
        json={
            "name": name,
            "office": office,
            "bio_text": bio_text,
        }
    )
    res.raise_for_status()
    return res.json()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Candidate name")
    parser.add_argument("--office", required=True, help="Office they're running for")
    parser.add_argument("--use-llm", action="store_true", help="Use LLM to rank sites")
    parser.add_argument("--dry-run", action="store_true", help="Only print the final candidate payload (no POST)")

    args = parser.parse_args()
    name = args.name
    office = args.office
    use_llm = args.use_llm
    dry_run = args.dry_run

    # Step 1: Scrape website & extract bio
    site, bio_text = scrape_candidate_website(name, use_llm=use_llm)
    if not bio_text:
        print("⚠️ No bio text found — skipping.")
        return

    print("📝 Scraped Bio Text:")
    print(bio_text[:400] + ("..." if len(bio_text) > 400 else ""))
    print()

    # Step 2: Summarize with LLM
    summary_result = call_llm_generate_summary(name, office, bio_text)

    print("✅ LLM Summary Result:")
    print(json.dumps(summary_result, indent=2))
    print()

    # Step 3: Build full candidate payload
    candidate_payload = {
        "name": name,
        "office": office,
        "bio_text": bio_text,
        "party": summary_result.get("party", "Unknown"),
        "past_positions": [],  # optionally extracted later
        "stance_summary": summary_result.get("stance_summary", [])
    }

    if dry_run:
        print("🧪 [Dry Run] Candidate payload:")
        print(json.dumps(candidate_payload, indent=2))
    else:
        print("📤 Posting candidate to backend...")
        res = requests.post("http://localhost:8000/candidates/", json=candidate_payload)
        res.raise_for_status()
        print("✅ Candidate created:", res.json())

if __name__ == "__main__":
    main()
