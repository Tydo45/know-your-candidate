# apps/api/routes/generate_summary.py

import re
import json
import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict, Union
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)

router = APIRouter()

class IssueStance(BaseModel):
    issue: str
    position: str

class SourcedStance(BaseModel):
    value: IssueStance
    source_url: str

class SourcedStr(BaseModel):
    value: str
    source_url: str

class SourceBlock(BaseModel):
    url: str
    text: str

class CandidateRequest(BaseModel):
    name: str
    office: str
    sources: Dict[str, Union[SourceBlock, List[SourceBlock]]]

class SummaryResponse(BaseModel):
    party: SourcedStr
    past_positions: List[SourcedStr]
    stance_summary: List[SourcedStance]

@router.post("/generate-summary", response_model=SummaryResponse)
def generate_summary(req: CandidateRequest):
    # Reconstruct a combined LLM input
    combined_text = ""
    for source_type, data in req.sources.items():
        if isinstance(data, dict):
            url = data.get("url")
            text = data.get("text")
            if url and text:
                combined_text += f"\n\n[{source_type.upper()}] ({url})\n{text}"
        elif isinstance(data, list):
            for idx, entry in enumerate(data):
                if isinstance(entry, dict) and "url" in entry and "text" in entry:
                    combined_text += f"\n\n[NEWS {idx+1}] ({entry['url']})\n{entry['text']}"

    prompt = f"""
You are an assistant that extracts political candidate information from multiple sources, preserving source URLs.

Candidate: {req.name}
Office: {req.office}

Sources:
\"\"\"
{combined_text}
\"\"\"

Return valid JSON in this format:

{{
  "party": {{ "value": "Democratic", "source_url": "https://..." }},
  "past_positions": [
    {{ "value": "Deputy District Attorney", "source_url": "https://..." }}
  ],
  "stance_summary": [
    {{
      "value": {{
        "issue": "Public Schools",
        "position": "Believes in Wisconsin's history of great public schools."
      }},
      "source_url": "https://..."
    }}
  ]
}}

Guidelines:
- Only use information explicitly found in the sources.
- Always include the source_url for each data point.
- Return complete sentences for positions.
- Return "Unknown" or an empty list where appropriate.
- Do not include any explanation or commentary — just valid JSON.
"""

    response = client.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    raw = response.choices[0].message.content.strip()

    try:
        json_text = re.search(r"```(?:json)?\n(.*?)```", raw, re.DOTALL)
        if json_text:
            parsed = json.loads(json_text.group(1))
        else:
            parsed = json.loads(raw)
        return parsed
    except Exception as e:
        return {
            "error": "Could not parse response from model",
            "raw": raw,
            "exception": str(e)
        }
