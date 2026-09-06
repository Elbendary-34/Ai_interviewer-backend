# Real-time WebSocket Endpoint — now also owns the alert-threshold logic
# that used to live in the standalone services/alert_engine.py (see the
# merge rationale in section 2 above: single consumer, no reuse elsewhere).
import json
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status

from app.schemas.metadata import FrameMetadataPayload, AlertMessage
from app.services.redis_service import redis_service
from app.core.security import decode_user_id

router = APIRouter()

EYE_CONTACT_THRESHOLD = 10  # ~3 seconds of consecutive lost eye contact
POSTURE_THRESHOLD = 15      # ~4.5 seconds of consecutive slouching


class AlertEngine:

    async def process_metadata(self, payload: FrameMetadataPayload) -> list[AlertMessage]:
        alerts: list[AlertMessage] = []
        session_id = payload.session_id
        current_time = time.time()

        if not payload.eye_contact.is_looking_at_camera:
            count = await redis_service.increment_counter(f"session:{session_id}:eye_lost_count")
            if count >= EYE_CONTACT_THRESHOLD:
                alerts.append(
                    AlertMessage(
                        session_id=session_id,
                        alert_type="EYE_CONTACT_LOST",
                        message="Please maintain eye contact with the interviewer.",
                        timestamp=current_time,
                    )
                )
        else:
            await redis_service.reset_counter(f"session:{session_id}:eye_lost_count")

        if payload.posture.is_slouching:
            count = await redis_service.increment_counter(f"session:{session_id}:slouch_count")
            if count >= POSTURE_THRESHOLD:
                alerts.append(
                    AlertMessage(
                        session_id=session_id,
                        alert_type="BAD_POSTURE",
                        message="Try sitting up straight to improve your presence.",
                        timestamp=current_time,
                    )
                )
        else:
            await redis_service.reset_counter(f"session:{session_id}:slouch_count")

        return alerts


alert_engine = AlertEngine()


@router.websocket("/ws/analytics/{session_id}")
async def analytics_websocket(websocket: WebSocket, session_id: str, token: str = Query(...)):
    try:
        decode_user_id(token)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    try:
        while True:
            data_text = await websocket.receive_text()
            data_json = json.loads(data_text)
            data_json["session_id"] = session_id

            payload = FrameMetadataPayload(**data_json)
            alerts = await alert_engine.process_metadata(payload)

            for alert in alerts:
                await websocket.send_json(alert.model_dump(by_alias=True))

    except WebSocketDisconnect:
        print(f"Client disconnected from WebSocket session: {session_id}")
    except Exception as e:
        print(f"WebSocket Error on session {session_id}: {str(e)}")
        await websocket.close()