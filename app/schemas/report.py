# Pydantic Schemas for Reports
# app/schemas/report.py
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional, Any, Dict, List

class ReportBase(BaseModel):
    session_id: str
    overall_score: Optional[float] = None
    eye_contact_score: Optional[float] = None
    posture_score: Optional[float] = None
    speech_clarity_score: Optional[float] = None
    feedback_summary: Optional[str] = None
    detailed_metrics: Optional[Dict[str, Any]] = None  

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True  
    )


# create schema for creating a new report (used in backend or AI service)
class ReportCreate(ReportBase):
    id: str


# update schema for updating report data (used in backend or AI service)
class ReportUpdate(BaseModel):
    overall_score: Optional[float] = None
    eye_contact_score: Optional[float] = None
    posture_score: Optional[float] = None
    speech_clarity_score: Optional[float] = None
    feedback_summary: Optional[str] = None
    detailed_metrics: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )


# response schema for returning report data to the frontend
class ReportResponse(ReportBase):
    id: str