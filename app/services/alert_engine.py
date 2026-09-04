# Real-time Alert & Threshold Rules
from app.schemas.metadata import FrameMetadataPayload, AlertMessage
from app.services.redis_service import redis_service
import time

# Threshold Constants
EYE_CONTACT_THRESHOLD = 10  # 10 consecutive frames (~3 seconds)
POSTURE_THRESHOLD = 15      # 15 consecutive frames (~4.5 seconds)

class AlertEngine:
    async def process_metadata(self, payload: FrameMetadataPayload) -> list[AlertMessage]:
        alerts = []
        session_id = payload.session_id
        current_time = time.time()

        # 1. Process Eye Contact Threshold
        if not payload.eye_contact.is_looking_at_camera:
            eye_key = f"session:{session_id}:eye_lost_count"
            count = await redis_service.increment_counter(eye_key)
            if count >= EYE_CONTACT_THRESHOLD:
                alerts.append(
                    AlertMessage(
                        session_id=session_id,
                        alert_type="EYE_CONTACT_LOST",
                        message="Please maintain eye contact with the interviewer.",
                        timestamp=current_time
                    )
                )
        else:
            await redis_service.reset_counter(f"session:{session_id}:eye_lost_count")

        # 2. Process Posture Threshold
        if payload.posture.is_slouching:
            posture_key = f"session:{session_id}:slouch_count"
            count = await redis_service.increment_counter(posture_key)
            if count >= POSTURE_THRESHOLD:
                alerts.append(
                    AlertMessage(
                        session_id=session_id,
                        alert_type="BAD_POSTURE",
                        message="Try sitting up straight to improve your presence.",
                        timestamp=current_time
                    )
                )
        else:
            await redis_service.reset_counter(f"session:{session_id}:slouch_count")

        return alerts

alert_engine = AlertEngine()