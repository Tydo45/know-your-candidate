from datetime import datetime
import us

class CandidateBuilder:
    def __init__(self, name, office, sources, summary):
        self.name = name
        self.office = office
        self.sources = sources
        self.summary = summary

    def build(self):
        now = datetime.utcnow().isoformat()
        official = self.sources.get("official") or {}

        return {
            "name": self.name,
            "office": self.office,
            "state": self.extract_state(),
            "is_incumbent": self.detect_incumbency(),
            "party": self.summary.get("party"),
            "bio_text": {
                "value": official.get("text", ""),
                "source_url": official.get("url", "")
            },
            "past_positions": self.summary.get("past_positions", []),
            "stance_summary": [
                {
                    "issue": s["value"]["issue"],
                    "position": s["value"]["position"],
                    "source_url": s.get("source_url")
                }
                for s in self.summary.get("stance_summary", [])
            ],
            "photo_url": None,
            "social_links": [],
            "district": None,
            "age": None,
            "gender": None,
            "race": None,
            "marital_status": None,
            "created_at": now,
            "last_updated": now
        }

    def extract_state(self):
        for state in us.states.STATES:
            if state.name.lower() in self.office.lower():
                return state.name
        return None

    def detect_incumbency(self):
        texts = []
        for source in [self.sources.get("official"), self.sources.get("ballotpedia")]:
            if source:
                texts.append(source.get("text", ""))
        texts += [item.get("text", "") for item in self.sources.get("news", [])]
        blob = " ".join(texts).lower()
        keywords = ["currently serves", "assumed office", "term ends", "incumbent", "seeking re-election"]
        return any(kw in blob for kw in keywords)
