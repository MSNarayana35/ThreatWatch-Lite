from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas

def get_incident(db: Session, incident_id: int):
    return db.query(models.Incident).filter(models.Incident.id == incident_id).first()

from datetime import datetime

def get_incidents(db: Session, category: str = None, severity: models.Severity = None, start_date: str = None, end_date: str = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Incident).order_by(models.Incident.date.desc())
    if category:
        query = query.filter(models.Incident.category == category)
    if severity:
        query = query.filter(models.Incident.severity == severity)
    if start_date:
        query = query.filter(models.Incident.date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(models.Incident.date <= datetime.fromisoformat(end_date))
    return query.offset(skip).limit(limit).all()

def create_incident(db: Session, incident: schemas.IncidentCreate):
    db_incident = models.Incident(**incident.model_dump())
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident

def get_leaderboard(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Leaderboard).order_by(models.Leaderboard.points.desc()).offset(skip).limit(limit).all()

def create_ctf_challenge(db: Session, challenge: schemas.CTFChallengeCreate):
    db_challenge = models.CTFChallenge(**challenge.model_dump())
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

def get_ctf_challenges(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.CTFChallenge).offset(skip).limit(limit).all()

def get_ctf_challenge(db: Session, challenge_id: int):
    return db.query(models.CTFChallenge).filter(models.CTFChallenge.id == challenge_id).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not user.hashed_password == password + "notreallyhashed":
        return False
    return user


def create_ctf_report(db: Session, report: schemas.CTFReportCreate, user_id: int):
    db_report = models.CTFReport(
        user_id=user_id,
        challenge_id=report.challenge_id,
        category=report.category,
        description=report.description,
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def create_contribution(db: Session, contribution: schemas.ContributionCreate, user_id: int):
    db_contribution = models.Contribution(
        user_id=user_id,
        title=contribution.title,
        description=contribution.description,
        category=contribution.category,
        severity=contribution.severity,
        resources=contribution.resources,
    )
    db.add(db_contribution)
    db.commit()
    db.refresh(db_contribution)
    return db_contribution


def get_contribution(db: Session, contribution_id: int):
    return db.query(models.Contribution).filter(models.Contribution.id == contribution_id).first()


def get_contributions_by_status(db: Session, status: str):
    return (
        db.query(models.Contribution)
        .filter(models.Contribution.status == status)
        .order_by(models.Contribution.created_at.desc())
        .all()
    )


def set_contribution_status(db: Session, contribution: models.Contribution, status: str):
    contribution.status = status
    db.add(contribution)
    db.commit()
    db.refresh(contribution)
    return contribution


def get_contribution_stats(db: Session):
    rows = (
        db.query(models.User.username, func.count(models.Contribution.id))
        .join(models.Contribution, models.Contribution.user_id == models.User.id)
        .filter(models.Contribution.status == "approved")
        .group_by(models.User.username)
        .order_by(func.count(models.Contribution.id).desc())
        .all()
    )
    return [{"username": username, "count": count} for username, count in rows]
