from fastapi import WebSocket
from typing import List, Dict, Any
import json
import asyncio
from app.core.redis import redis_client

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.experiment_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, experiment_id: str = None):
        await websocket.accept()
        if experiment_id:
            if experiment_id not in self.experiment_connections:
                self.experiment_connections[experiment_id] = []
            self.experiment_connections[experiment_id].append(websocket)
        else:
            self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket, experiment_id: str = None):
        if experiment_id and experiment_id in self.experiment_connections:
            if websocket in self.experiment_connections[experiment_id]:
                self.experiment_connections[experiment_id].remove(websocket)
        elif websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_to_experiment(self, experiment_id: str, message: Dict[str, Any]):
        """Send command to a specific training experiment"""
        if experiment_id in self.experiment_connections:
            for connection in self.experiment_connections[experiment_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast cognition updates to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Handle stale connections
                pass

    async def stream_from_redis(self):
        """Background task to stream from Redis alerts to WebSockets"""
        from app.services.event_stream import event_stream
        print("DEBUG: WebSocket Stream Worker started...")
        if not redis_client.redis:
            await redis_client.connect()
            
        last_id = "$" # Start from the latest at the time of connection
        
        while True:
            try:
                # XREAD [COUNT count] [BLOCK milliseconds] STREAMS key [key ...] id [id ...]
                streams = await redis_client.redis.xread(
                    {event_stream.STREAM_KEY_ALERTS: last_id}, 
                    count=5, 
                    block=5000
                )
                
                for stream_name, messages in streams:
                    for msg_id, data in messages:
                        last_id = msg_id
                        alert_json = data.get(b"alert") or data.get("alert")
                        if alert_json:
                            print(f"DEBUG: Broadcasting live alert: {msg_id}")
                            await self.broadcast({
                                "channel": "live_cognition",
                                "data": json.loads(alert_json)
                            })
            except Exception as e:
                print(f"DEBUG: WebSocket Stream Error: {e}")
                await asyncio.sleep(1)

ws_manager = ConnectionManager()
