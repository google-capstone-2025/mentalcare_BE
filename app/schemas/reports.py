from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date
from typing import Optional, Dict

class SessionReportList(BaseModel):
    report_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class WeeklyReportList(BaseModel):
    weekly_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class SessionReportDetail(BaseModel):
    report_id: UUID
    summary: Optional[Dict]
    highlights: Optional[Dict]
    mood_overview: Optional[Dict]
    routine_overview: Optional[Dict]
    usage_overview: Optional[Dict]
    created_at: datetime

    class Config:
        orm_mode = True


class WeeklyReportDetail(BaseModel):
    weekly_id: UUID
    week_start_date: date
    mood_overview: Optional[Dict]
    routine_overview: Optional[Dict]
    usage_overview: Optional[Dict]
    highlights: Optional[Dict]
    created_at: datetime

    class Config:
        orm_mode = True