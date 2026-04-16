import logging
from sqlalchemy.orm import Session
from datetime import datetime

from .. import crud, models, schemas
from .aggregator import fetch_thehackernews_articles
from .classifier import classify_incident, score_severity

_logger = logging.getLogger(__name__)

def update_threat_feed(db: Session):
    """
    Fetches, classifies, and stores new threat incidents.
    """
    _logger.info("Starting threat feed update...")
    articles = fetch_thehackernews_articles()
    if not articles:
        _logger.info("No articles fetched. Update process finished.")
        return

    new_incidents_count = 0
    for article in articles:
        existing_incident = db.query(models.Incident).filter(models.Incident.title == article['title']).first()
        if existing_incident:
            continue

        category = classify_incident(article['title'], article['description'])
        severity = score_severity(article['title'], article['description'])

        incident_data = schemas.IncidentCreate(
            title=article['title'],
            description=article['description'],
            source=article['source'],
            date=datetime.utcnow(),
            category=str(category),
            severity=severity
        )
        crud.create_incident(db=db, incident=incident_data)
        new_incidents_count += 1
    
    _logger.info("Threat feed update finished. Added %s new incidents.", new_incidents_count)
