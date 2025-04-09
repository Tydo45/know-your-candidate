from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from db import get_db
import models
import schemas

router = APIRouter()

@router.post("/candidates/", response_model=schemas.CandidateResponse)
def create_candidate(candidate: schemas.CandidateCreate, db: Session = Depends(get_db)):
    db_candidate = models.Candidate(
        name=candidate.name,
        office=candidate.office,
        party=candidate.party.dict() if candidate.party else None,
        bio_text=candidate.bio_text.dict() if candidate.bio_text else None,
        past_positions=[p.dict() for p in candidate.past_positions] if candidate.past_positions else None,
        district=candidate.district,
        state=candidate.state,
        is_incumbent=candidate.is_incumbent,
        photo_url=candidate.photo_url,
        social_links=candidate.social_links,
        age=candidate.age,
        gender=candidate.gender,
        race=candidate.race,
        marital_status=candidate.marital_status,
    )
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)

    # Save stances
    for stance in candidate.stance_summary:
        db_stance = models.Stance(
            candidate_id=db_candidate.id,
            issue=stance.issue,
            position=stance.position,
            source_url=stance.source_url
        )
        db.add(db_stance)
    db.commit()

    db.refresh(db_candidate)
    return get_candidate_response(db_candidate, db)

@router.get("/candidates/", response_model=list[schemas.CandidateResponse])
def get_all_candidates(db: Session = Depends(get_db)):
    candidates = db.query(models.Candidate).options(joinedload(models.Candidate.stances)).all()
    return [get_candidate_response(c, db) for c in candidates]

@router.get("/candidates/{candidate_id}", response_model=schemas.CandidateResponse)
def get_candidate(candidate_id: UUID, db: Session = Depends(get_db)):
    candidate = (
        db.query(models.Candidate)
        .options(joinedload(models.Candidate.stances))
        .filter(models.Candidate.id == candidate_id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return get_candidate_response(candidate, db)

@router.delete("/candidates/{candidate_id}", response_model=dict)
def delete_candidate(candidate_id: UUID, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    db.query(models.Stance).filter(models.Stance.candidate_id == candidate_id).delete()
    db.delete(candidate)
    db.commit()
    return {"message": f"Candidate {candidate_id} deleted."}

@router.delete("/candidates/", response_model=dict)
def delete_all_candidates(db: Session = Depends(get_db)):
    db.query(models.Stance).delete()
    db.query(models.Candidate).delete()
    db.commit()
    return {"message": "All candidates deleted."}

# Helper function to build CandidateResponse from ORM
def get_candidate_response(candidate: models.Candidate, db: Session) -> schemas.CandidateResponse:
    return schemas.CandidateResponse(
        id=candidate.id,
        name=candidate.name,
        office=candidate.office,
        party=candidate.party,
        bio_text=candidate.bio_text,
        past_positions=candidate.past_positions,
        district=candidate.district,
        state=candidate.state,
        is_incumbent=candidate.is_incumbent,
        photo_url=candidate.photo_url,
        social_links=candidate.social_links,
        age=candidate.age,
        gender=candidate.gender,
        race=candidate.race,
        marital_status=candidate.marital_status,
        created_at=candidate.created_at,
        last_updated=candidate.last_updated,
        stance_summary=[
            schemas.StanceResponse(
                issue=s.issue,
                position=s.position,
                source_url=s.source_url,
                created_at=s.created_at
            )
            for s in candidate.stances
        ]
    )
