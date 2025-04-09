# apps/api/schemas.py

from pydantic import BaseModel
from typing import Optional, List
import datetime

# ---------- Reusable ----------
class SourcedStr(BaseModel):
    value: str
    source_url: str

# ---------- Stances ----------
class StanceInput(BaseModel):
    issue: str
    position: str
    source_url: Optional[str] = None

class StanceResponse(StanceInput):
    created_at: datetime.datetime

# ---------- Candidates ----------
class CandidateCreate(BaseModel):
    name: str
    office: str
    party: Optional[SourcedStr] = SourcedStr(value="Unknown", source_url="")
    district: Optional[str] = None
    state: Optional[str] = None
    is_incumbent: Optional[bool] = False
    age: Optional[int] = None
    gender: Optional[str] = None
    race: Optional[str] = None
    marital_status: Optional[str] = None
    past_positions: Optional[List[SourcedStr]] = None
    photo_url: Optional[str] = None
    social_links: Optional[List[str]] = None
    bio_text: Optional[SourcedStr] = None
    stance_summary: List[StanceInput]

class CandidateResponse(BaseModel):
    id: str
    name: str
    office: str
    party: Optional[SourcedStr]
    district: Optional[str]
    state: Optional[str]
    is_incumbent: bool
    age: Optional[int]
    gender: Optional[str]
    race: Optional[str]
    marital_status: Optional[str]
    past_positions: Optional[List[SourcedStr]]
    photo_url: Optional[str]
    social_links: Optional[List[str]]
    bio_text: Optional[SourcedStr]
    created_at: datetime.datetime
    last_updated: datetime.datetime
    stance_summary: List[StanceResponse]
