import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

from .database import engine, SessionLocal
from . import models, crud, schemas
from .routers import incidents, auth, ctf, admin
from .core.tasks import update_threat_feed
from .core.sample_data import populate_incidents, populate_ctf_challenges

_logger.info("Creating all tables...")
models.Base.metadata.create_all(bind=engine)

inspector = inspect(engine)
user_columns = [col["name"] for col in inspector.get_columns("users")]
if "is_admin" not in user_columns:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
        conn.commit()

db = SessionLocal()
try:
    default_email = "admin@threatwatch.com"
    default_password = "Admin@1234"
    default_username = "twadmin"

    user = crud.get_user_by_email(db, default_email)
    if not user:
        user_in = schemas.UserCreate(
            username=default_username,
            email=default_email,
            password=default_password,
        )
        user = crud.create_user(db, user_in)
    else:
        user.username = default_username
        user.hashed_password = default_password + "notreallyhashed"
    user.is_admin = True
    db.add(user)
    db.commit()
finally:
    db.close()

_logger.info("Tables created.")

app = FastAPI(
    title="ThreatWatch Lite",
    description="A real-time cyber threat intelligence and CTF platform.",
    version="0.1.0",
)

@app.on_event("startup")
def on_startup():
    _logger.info("Running startup tasks...")
    db = SessionLocal()
    update_threat_feed(db)
    populate_incidents(db)
    populate_ctf_challenges(db)
    db.close()
    _logger.info("Startup tasks completed.")

app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["incidents"])
app.include_router(ctf.router)
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

from fastapi.responses import RedirectResponse
from fastapi import Depends
from fastapi.responses import HTMLResponse
from typing import List
from sqlalchemy.orm import Session
from .dependencies import get_db
from . import crud, schemas

@app.get("/")
async def root():
    return RedirectResponse(url="/index.html")

@app.get("/logout")
async def logout():
    return HTMLResponse(
        content="""
<!doctype html><html><head><meta charset="utf-8"><title>Logout</title></head>
<body>
<script>
try { localStorage.removeItem('accessToken'); } catch (e) {}
location.href = '/login.html';
</script>
</body></html>
        """,
        media_type="text/html",
    )

@app.get("/api/v1/leaderboard/", response_model=List[schemas.Leaderboard])
def read_leaderboard(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_leaderboard(db, skip=skip, limit=limit)

app.mount("/", StaticFiles(directory="static", html=True), name="static")
