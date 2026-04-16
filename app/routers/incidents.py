from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas
from ..dependencies import get_db
from .auth import get_current_user

router = APIRouter()


@router.post("/", response_model=schemas.Incident)
def create_incident(incident: schemas.IncidentCreate, db: Session = Depends(get_db)):
    return crud.create_incident(db=db, incident=incident)


@router.get("/", response_model=List[schemas.Incident])
def read_incidents(category: str = None, severity: models.Severity = None, start_date: str = None, end_date: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    incidents = crud.get_incidents(db, category=category, severity=severity, start_date=start_date, end_date=end_date, skip=skip, limit=limit)
    return incidents


@router.get("/{incident_id}", response_model=schemas.Incident)
def read_incident(incident_id: int, db: Session = Depends(get_db)):
    db_incident = crud.get_incident(db, incident_id=incident_id)
    if db_incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return db_incident


@router.post("/contributions/submit")
def submit_contribution(
    contribution: schemas.ContributionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    crud.create_contribution(db, contribution, current_user.id)
    return {"message": "Contribution submitted"}
