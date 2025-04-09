from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
import datetime

# ---------- Shared ----------
class SourcedStr(BaseModel):
    value: str
    source_url: str

# ---------- Stance ----------
class StanceInput(BaseModel):
    issue: str
    position: str
    source_url: Optional[str] = None

class StanceResponse(StanceInput):
    created_at: datetime.datetime

# ---------- Candidate ----------
class CandidateCreate(BaseModel):
    name: str
    office: str
    party: Optional[SourcedStr]
    bio_text: Optional[SourcedStr]
    past_positions: Optional[List[SourcedStr]] = None
    district: Optional[str] = None
    state: Optional[str] = None
    is_incumbent: Optional[bool] = False
    photo_url: Optional[str] = None
    social_links: Optional[List[str]] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    race: Optional[str] = None
    marital_status: Optional[str] = None
    stance_summary: List[StanceInput]

class CandidateResponse(BaseModel):
    id: UUID
    name: str
    office: str
    party: Optional[SourcedStr]
    bio_text: Optional[SourcedStr]
    past_positions: Optional[List[SourcedStr]]
    district: Optional[str]
    state: Optional[str]
    is_incumbent: Optional[bool]
    photo_url: Optional[str]
    social_links: Optional[List[str]]
    age: Optional[int]
    gender: Optional[str]
    race: Optional[str]
    marital_status: Optional[str]
    stance_summary: List[StanceResponse]
    created_at: datetime.datetime
    last_updated: datetime.datetime
