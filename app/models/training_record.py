import datetime

import pydantic
from app.models.controller import Controller


class TrainingRecord(pydantic.BaseModel):
    student: Controller
    instructor: Controller
    session_date: datetime.datetime
    facility: str
    position: str
    duration: datetime.timedelta
    movements: int
    score: int
    notes: str
    is_ots_recommendation: bool
    solo_granted: bool
    created_at: datetime.datetime


class OTSExam(pydantic.BaseModel):
    student: Controller
    instructor: Controller
    facility: str
    position: str
    exam_date: datetime.datetime

