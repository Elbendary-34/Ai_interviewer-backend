# Pydantic Schemas for Metadata
from pydantic import BaseModel, Field
from typing import Optional

class EyeContactData(BaseModel):
    is_looking_at_camera: bool
    confidence: float = Field(ge=0.0, le=1.0)

class PostureData(BaseModel):
    is_slouching: bool
    is_centered: bool

class AudioMetricsData(BaseModel):
    volume_level: float
    is_speaking: bool

class FrameMetadataPayload(BaseModel):
    session_id: str
    timestamp: float
    eye_contact: EyeContactData
    posture: PostureData
    audio: Optional[AudioMetricsData] = None

class AlertMessage(BaseModel):
    session_id: str
    alert_type: str  # e.g., "EYE_CONTACT_LOST", "BAD_POSTURE"
    message: str
    timestamp: float