# Real-time WebSocket Endpoint
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.schemas.metadata import FrameMetadataPayload
from app.services.alert_engine import alert_engine
import json

router = APIRouter()

@router.websocket("/ws/analytics/{session_id}")
async def analytics_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            # 1. Receive JSON text from Frontend every 300ms
            data_text = await websocket.receive_text()
            data_json = json.loads(data_text)
            data_json["session_id"] = session_id
            
            # 2. Validate Payload with Pydantic Schema
            payload = FrameMetadataPayload(**data_json)
            
            # 3. Process Payload via Alert Engine
            alerts = await alert_engine.process_metadata(payload)
            
            # 4. If any alert was triggered, send it back instantly
            for alert in alerts:
                await websocket.send_json(alert.model_dump())

    except WebSocketDisconnect:
        print(f"Client disconnected from WebSocket session: {session_id}")
    except Exception as e:
        print(f"WebSocket Error on session {session_id}: {str(e)}")
        await websocket.close()