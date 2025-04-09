# apps/api/routes/generate_summary.py

import re
import json
import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
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

class CandidateRequest(BaseModel):
    name: str
    office: str
    bio_text: str

class SummaryResponse(BaseModel):
    party: str
    stance_summary: List[IssueStance]

@router.post("/generate-summary", response_model=SummaryResponse)
def generate_summary(req: CandidateRequest):
    prompt = f"""
    You are an assistant that extracts political information from a candidate's biography.

    BIO:
    \"\"\"
    {req.bio_text}
    \"\"\"

    Return ONLY valid JSON in the following format:
    {{
      "party": "PARTY_NAME",
      "stance_summary": [
        {{ "issue": "ISSUE_NAME", "position": "ISSUE_POSITION" }}
      ]
    }}

    Guidelines:
    - For "party", use standardized values like "Democratic", "Republican", "Green", "Independent", or return "Unknown".
    - Use only what is stated or clearly implied in the bio.
    - Do not make assumptions — return "Unknown" if it's not mentioned.
    - For "stance_summary", follow these rules:
        - Use only issues mentioned or implied in the bio.
        - Use standardized issue names (e.g. "Healthcare", "Education", "Climate").
        - Each stance should describe what the candidate *supports, opposes, or has done* in a complete sentence.
        - Avoid vague terms like "supportive" — be specific.

    Respond ONLY with valid JSON — no extra text or commentary.
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
