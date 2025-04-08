import re
import json
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from routes import candidates

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(candidates.router)

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)

class IssueStance(BaseModel):
    issue: str
    position: str

class CandidateRequest(BaseModel):
    name: str
    office: str
    bio_text: str

class CandidateResponse(BaseModel):
    name: Optional[str]
    office: Optional[str]
    party: Optional[str]
    stance_summary: List[IssueStance]

@app.post("/generate-summary", response_model=CandidateResponse)
def generate_summary(req: CandidateRequest):
    prompt = f"""
    You are an assistant that extracts structured political issue positions from a candidate's bio.

    BIO:
    \"\"\"
    {req.bio_text}
    \"\"\"

    Use the following values for the candidate:
    - Name: {req.name}
    - Office: {req.office}

    Return ONLY valid JSON in the following format:
    {{
    "name": "{req.name}",
    "office": "{req.office}",
    "party": "Unknown",
    "stance_summary": [
        {{ "issue": "ISSUE_NAME", "position": "ISSUE_POSITION" }}
    ]
    }}

    Guidelines:
    - Use only the issues mentioned in the bio.
    - Keep "issue" names standardized (e.g. "Healthcare", "Education", "Climate", etc.).
    - Do NOT return extra text, markdown, or explanations.
    - All values must be JSON-serializable.
    - Each stance should describe what the candidate *supports, opposes, or has done* in a complete sentence.
    - Avoid vague words like "supportive" or "protective" — be specific about what they did or believe.
    """

    response = client.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    raw = response.choices[0].message.content.strip()

    # 🔥 Extract JSON from code block or raw string
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