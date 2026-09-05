# Real-time WebSocket Endpoint
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.schemas.metadata import FrameMetadataPayload
from app.services.alert_engine import alert_engine
from app.core.security import decode_user_id

router = APIRouter()


@router.websocket("/ws/analytics/{session_id}")
async def analytics_websocket(websocket: WebSocket, session_id: str, token: str = Query(...)):
    # Browsers/Flutter can't easily attach custom Authorization headers to
    # a raw WebSocket handshake, so the token travels as a query param
    # instead — validated with the same JWT logic used everywhere else.
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