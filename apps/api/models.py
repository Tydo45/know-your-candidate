# apps/api/models.py

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from db import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    office = Column(String, nullable=False)
    party = Column(String, default="Unknown")
    district = Column(String, nullable=True)
    state = Column(String, nullable=True)
    is_incumbent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)

    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    race = Column(String, nullable=True)
    marital_status = Column(String, nullable=True)
    past_positions = Column(ARRAY(String), nullable=True)

    photo_url = Column(String, nullable=True)
    social_links = Column(ARRAY(String), nullable=True)
    bio_text = Column(Text, nullable=True)

    stances = relationship("Stance", back_populates="candidate")
    versions = relationship("VersionSnapshot", back_populates="candidate")


class Stance(Base):
    __tablename__ = "stances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"))
    issue = Column(String, nullable=False)
    position = Column(Text, nullable=False)
    source_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="stances")


class VersionSnapshot(Base):
    __tablename__ = "versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"))
    stance_json = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="versions")
