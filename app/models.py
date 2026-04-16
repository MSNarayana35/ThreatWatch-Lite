from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base
import enum

class Severity(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    severity = Column(Enum(Severity))
    date = Column(DateTime)
    source = Column(String)
    category = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="incidents")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    active_challenge_id = Column(Integer, nullable=True)
    challenge_start_time = Column(DateTime, nullable=True)
    
    incidents = relationship("Incident", back_populates="owner", cascade="all, delete-orphan")
    ctf_solves = relationship("CTFSolve", back_populates="user", cascade="all, delete-orphan")
    leaderboard_entry = relationship("Leaderboard", back_populates="user", uselist=False)
    ctf_reports = relationship("CTFReport", back_populates="user", cascade="all, delete-orphan")
    contributions = relationship("Contribution", back_populates="user", cascade="all, delete-orphan")

class Leaderboard(Base):
    __tablename__ = "leaderboard"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    username = Column(String, unique=True, index=True)
    points = Column(Integer, default=0)

    user = relationship("User", back_populates="leaderboard_entry")


class CTFChallenge(Base):
    __tablename__ = "ctf_challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    points = Column(Integer)
    flag = Column(String)
    hint = Column(String, nullable=True)
    resources = Column(String, nullable=True)

    solves = relationship("CTFSolve", back_populates="challenge", cascade="all, delete-orphan")


class CTFSolve(Base):
    __tablename__ = "ctf_solves"
    __table_args__ = (UniqueConstraint("user_id", "challenge_id", name="uq_ctf_solves_user_challenge"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    challenge_id = Column(Integer, ForeignKey("ctf_challenges.id"), index=True)
    solved_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="ctf_solves")
    challenge = relationship("CTFChallenge", back_populates="solves")


class CTFReport(Base):
    __tablename__ = "ctf_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    challenge_id = Column(Integer, ForeignKey("ctf_challenges.id"), nullable=True, index=True)
    category = Column(String)  # e.g. "challenge" or "page"
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="ctf_reports")
    challenge = relationship("CTFChallenge")


class Contribution(Base):
    __tablename__ = "contributions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    title = Column(String)
    description = Column(String)
    category = Column(String)
    severity = Column(Enum(Severity))
    resources = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="contributions")
