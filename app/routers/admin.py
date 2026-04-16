from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, models, schemas
from ..dependencies import get_db
from .auth import get_current_admin


router = APIRouter()


@router.get("/ctf/reports")
def list_ctf_reports(
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    reports = (
        db.query(models.CTFReport)
        .order_by(models.CTFReport.created_at.desc())
        .all()
    )
    result = []
    for r in reports:
        result.append(
            {
                "id": r.id,
                "user_id": r.user_id,
                "username": r.user.username if r.user else None,
                "challenge_id": r.challenge_id,
                "challenge_title": r.challenge.title if r.challenge else None,
                "category": r.category,
                "description": r.description,
                "created_at": r.created_at,
            }
        )
    return result


@router.get("/contributions/pending")
def list_pending_contributions(
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    items = crud.get_contributions_by_status(db, "pending")
    result = []
    for c in items:
        result.append(
            {
                "id": c.id,
                "user_id": c.user_id,
                "username": c.user.username if c.user else None,
                "title": c.title,
                "description": c.description,
                "category": c.category,
                "severity": c.severity,
                "resources": c.resources,
                "status": c.status,
                "created_at": c.created_at,
            }
        )
    return result


@router.post("/contributions/{contribution_id}/approve")
def approve_contribution(
    contribution_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    contribution = crud.get_contribution(db, contribution_id)
    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")
    if contribution.status != "pending":
        raise HTTPException(status_code=400, detail="Contribution already processed")

    incident_data = {
        "title": contribution.title,
        "description": contribution.description,
        "source": "User Contribution",
        "date": contribution.created_at,
        "category": contribution.category,
        "severity": contribution.severity,
    }
    crud.create_incident(db, schemas.IncidentCreate(**incident_data))
    crud.set_contribution_status(db, contribution, "approved")
    return {"message": "Contribution approved"}


@router.post("/contributions/{contribution_id}/reject")
def reject_contribution(
    contribution_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    contribution = crud.get_contribution(db, contribution_id)
    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")
    if contribution.status != "pending":
        raise HTTPException(status_code=400, detail="Contribution already processed")

    crud.set_contribution_status(db, contribution, "rejected")
    return {"message": "Contribution rejected"}


@router.get("/contributions/stats")
def contribution_stats(
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    return crud.get_contribution_stats(db)
