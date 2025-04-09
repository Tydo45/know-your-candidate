import argparse
import requests
import json
from scrape_candidate import scrape_candidate_sources
import us

def call_llm_generate_summary(name: str, office: str, sources: dict, use_chat_summary: bool = False) -> dict:
    print("🔁 Sending text to LLM for summarization...")
    
    clean_sources = {k: v for k, v in sources.items() if v is not None}
    
    url = "http://localhost:8000/generate-summary"
    if use_chat_summary:
        print("🧠 Using chat-style streaming summarizer...")
    else:
        print("📝 Using monolithic summarizer...")

    res = requests.post(
        url,
        json={
            "name": name,
            "office": office,
            "sources": clean_sources
        }
    )
    res.raise_for_status()
    return res.json()

def extract_state_from_office(office: str) -> str:
    for state in us.states.STATES:
        if state.name.lower() in office.lower():
            return state.name
    return "Unknown"

def detect_incumbency(texts: list[str]) -> bool:
    keywords = ["currently serves", "assumed office", "term ends", "incumbent", "seeking re-election"]
    text_blob = " ".join(texts).lower()
    return any(keyword in text_blob for keyword in keywords)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Candidate name")
    parser.add_argument("--office", required=True, help="Office they're running for")
    parser.add_argument("--use-llm", action="store_true", help="Use LLM to rank sites")
    parser.add_argument("--dry-run", action="store_true", help="Only print the final candidate payload (no POST)")
    parser.add_argument("--force-refresh", action="store_true", help="Force Refresh of Candidate Sources")
    parser.add_argument("--use-chat-summary", action="store_true", help="Use streaming/chat-based summary generation")
    args = parser.parse_args()

    name = args.name
    office = args.office
    use_llm = args.use_llm
    dry_run = args.dry_run
    force_refresh = args.force_refresh
    use_chat_summary = args.use_chat_summary

    # Step 1: Scrape sources
    scraped = scrape_candidate_sources(name, use_llm=use_llm, force_refresh=force_refresh)

    # Step 2: Reformat for summary call
    sources_payload = {
        "official": scraped.get("official", {}),
        "ballotpedia": scraped.get("ballotpedia", {}),
        "news": scraped.get("news", [])
    }
    
    print("🧾 Payload Sent to LLM API:")
    print(json.dumps({
        "name": name,
        "office": office,
        "sources": sources_payload
    }, indent=2))

    # Step 3: Generate summary
    summary = call_llm_generate_summary(name, office, sources_payload, use_chat_summary=use_chat_summary)

    print("✅ LLM Summary Result:")
    print(json.dumps(summary, indent=2))
    print()

    # Step 4: Add derived fields
    all_texts = [v["text"] for v in [scraped["official"], scraped["ballotpedia"]] if v]
    all_texts += [item["text"] for item in scraped.get("news", [])]
    state = extract_state_from_office(office)
    is_incumbent = detect_incumbency(all_texts)

    # Protect Against NoneType
    official_source = sources_payload.get("official") or {}
    # Step 5: Build payload with source URLs
    candidate_payload = {
        "name": name,
        "office": office,
        "state": state,
        "is_incumbent": is_incumbent,
        "bio_text": {
            "value":  official_source.get("text", ""),
            "source_url": official_source.get("url", "")
        },
        "party": summary.get("party", {}),
        "past_positions": summary.get("past_positions", []),
        "stance_summary": [
            {
                "issue": stance["value"]["issue"],
                "position": stance["value"]["position"],
                "source_url": stance["source_url"]
            }
            for stance in summary.get("stance_summary", [])
        ]
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
