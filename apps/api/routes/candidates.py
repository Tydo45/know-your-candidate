# apps/api/routes/candidates.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from db import SessionLocal
import models
import schemas
import datetime

router = APIRouter()

def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

@router.post("/candidates/", response_model=dict)
def create_candidate(data: schemas.CandidateCreate, db: Session = Depends(get_db)):
    candidate = models.Candidate(
        name=data.name,
        office=data.office,
        party=data.party,
        district=data.district,
        state=data.state,
        is_incumbent=data.is_incumbent,
        age=data.age,
        gender=data.gender,
        race=data.race,
        marital_status=data.marital_status,
        past_positions=data.past_positions,
        photo_url=data.photo_url,
        social_links=data.social_links,
        bio_text=data.bio_text,
        created_at=datetime.datetime.utcnow(),
        last_updated=datetime.datetime.utcnow()
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    for stance_data in data.stance_summary:
        stance = models.Stance(
            candidate_id=candidate.id,
            issue=stance_data.issue,
            position=stance_data.position,
            source_url=stance_data.source_url,
            created_at=datetime.datetime.utcnow()
        )
        db.add(stance)

    db.commit()
    return {"id": candidate.id, "message": "Candidate created"}

@router.get("/candidates/", response_model=list[schemas.CandidateResponse])
def get_all_candidates(db: Session = Depends(get_db)):
    candidates = db.query(models.Candidate).all()
    result = []
    for c in candidates:
        stances = db.query(models.Stance).filter(models.Stance.candidate_id == c.id).all()
        result.append({
            "id": str(c.id),
            "name": c.name,
            "office": c.office,
            "party": c.party,
            "district": c.district,
            "state": c.state,
            "is_incumbent": c.is_incumbent,
            "age": c.age,
            "gender": c.gender,
            "race": c.race,
            "marital_status": c.marital_status,
            "past_positions": c.past_positions,
            "photo_url": c.photo_url,
            "social_links": c.social_links,
            "bio_text": c.bio_text,
            "created_at": c.created_at,
            "last_updated": c.last_updated,
            "stance_summary": [
                {
                    "issue": s.issue,
                    "position": s.position,
                    "source_url": s.source_url,
                    "created_at": s.created_at
                } for s in stances
            ]
        })
    return result

@router.get("/candidates/{candidate_id}", response_model=schemas.CandidateResponse)
def get_candidate(candidate_id: UUID, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    stances = db.query(models.Stance).filter(models.Stance.candidate_id == candidate.id).all()
    return {
        "id": str(candidate.id),
        "name": candidate.name,
        "office": candidate.office,
        "party": candidate.party,
        "district": candidate.district,
        "state": candidate.state,
        "is_incumbent": candidate.is_incumbent,
        "age": candidate.age,
        "gender": candidate.gender,
        "race": candidate.race,
        "marital_status": candidate.marital_status,
        "past_positions": candidate.past_positions,
        "photo_url": candidate.photo_url,
        "social_links": candidate.social_links,
        "bio_text": candidate.bio_text,
        "created_at": candidate.created_at,
        "last_updated": candidate.last_updated,
        "stance_summary": [
            {
                "issue": s.issue,
                "position": s.position,
                "source_url": s.source_url,
                "created_at": s.created_at
            } for s in stances
        ]
    }
