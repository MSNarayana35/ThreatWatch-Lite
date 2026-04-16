from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from .models import Severity

class IncidentBase(BaseModel):
    title: str
    description: str
    source: str
    date: datetime
    category: str
    severity: Severity

class IncidentCreate(IncidentBase):
    source: str

class Incident(IncidentBase):
    id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_admin: Optional[bool] = None

    class Config:
        from_attributes = True

class LeaderboardBase(BaseModel):
    user_id: int
    username: str
    points: int

class Leaderboard(LeaderboardBase):
    id: int

    class Config:
        from_attributes = True

class LeaderboardEntry(BaseModel):
    username: str
    score: int

    class Config:
        from_attributes = True


class CTFChallengeBase(BaseModel):
    title: str
    description: str
    points: int
    hint: Optional[str] = None
    resources: Optional[str] = None


class CTFChallengeCreate(CTFChallengeBase):
    flag: str


class CTFChallenge(CTFChallengeBase):
    id: int

    class Config:
        from_attributes = True


class CTFSubmission(BaseModel):
    flag: str


class CTFSubmissionResponse(BaseModel):
    message: str
    correct: bool
    points_awarded: int = 0
    total_points: Optional[int] = None


class CTFReportCreate(BaseModel):
    challenge_id: Optional[int] = None
    category: str
    description: str


class ContributionCreate(BaseModel):
    title: str
    description: str
    category: str
    severity: Severity
    resources: Optional[str] = None
