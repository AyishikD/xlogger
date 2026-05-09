from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.manager import ws_manager

router = APIRouter()

@router.websocket("/ws/cognition")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Maintain connection
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@router.websocket("/ws/intervention/{experiment_id}")
async def intervention_endpoint(websocket: WebSocket, experiment_id: str):
    await ws_manager.connect(websocket, experiment_id=experiment_id)
    try:
        while True:
            # SDK can also send heartbeat/status back
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, experiment_id=experiment_id)
