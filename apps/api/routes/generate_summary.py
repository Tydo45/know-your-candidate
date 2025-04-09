# apps/api/routes/generate_summary.py

import re
import json
import os
from fastapi import APIRouter, HTTPException
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
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that extracts political candidate information from sources. "
                f"Candidate: {req.name}, Office: {req.office}. "
                "Maintain a running JSON summary of:\n"
                "- Party affiliation (with source_url)\n"
                "- Past positions (list with source_url)\n"
                "- Issue stances (each with issue, position, source_url)\n"
                "Only use information explicitly found in the source. "
                "If no info is found, return the prior state unchanged. "
                "Each time, return ONLY valid JSON with this format:\n"
                "{\n"
                '  "party": {"value": "...", "source_url": "..."},\n'
                '  "past_positions": [{"value": "...", "source_url": "..."}],\n'
                '  "stance_summary": [{"value": {"issue": "...", "position": "..."}, "source_url": "..."}]\n'
                "}"
            )
        },
        {
            "role": "user",
            "content": "Start with an empty summary."
        },
        {
            "role": "assistant",
            "content": json.dumps({
                "party": {"value": "Unknown", "source_url": ""},
                "past_positions": [],
                "stance_summary": []
            })
        }
    ]

    # Flatten all sources into labeled blocks
    labeled_blocks = []
    for source_type, entries in req.sources.items():
        if isinstance(entries, dict):
            labeled_blocks.append((source_type.upper(), entries))
        elif isinstance(entries, list):
            for i, entry in enumerate(entries):
                labeled_blocks.append((f"{source_type.upper()} {i+1}", entry))

    # Feed each block incrementally
    for label, block in labeled_blocks:
        block_text = f"[{label}] ({block.url})\n{block.text}"
        messages.append({"role": "user", "content": block_text})

        response = client.chat.completions.create(
            model="meta/llama-3.3-70b-instruct",
            messages=messages,
            temperature=0.4
        )
        reply = response.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": reply})


    # Parse final response
    final_response = messages[-1]["content"]

    try:
        json_text = re.search(r"```(?:json)?\n(.*?)```", final_response, re.DOTALL)
        if json_text:
            parsed = json.loads(json_text.group(1))
        else:
            parsed = json.loads(final_response)
        return parsed
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Could not parse final model output",
                "raw": final_response,
                "exception": str(e)
            }
        )

