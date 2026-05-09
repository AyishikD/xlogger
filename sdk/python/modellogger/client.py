import httpx
import asyncio
import json
from typing import Dict, Any, Optional, List
import logging

class ModelLoggerClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"X-API-KEY": api_key} if api_key else {},
            timeout=10.0
        )

    async def close(self):
        await self.client.aclose()

    async def _post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = await self.client.post(path, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logging.error(f"ModelLogger API Error: {e}")
            return {"error": str(e)}

    async def create_experiment(self, name: str, description: str = "", metadata: Dict[str, Any] = {}) -> str:
        res = await self._post("/api/v1/experiments/", {
            "name": name,
            "description": description,
            "metadata_json": metadata
        })
        return res.get("id")

    async def log_event(self, experiment_id: str, event_type: str, summary: str, severity: str = "INFO", metadata: Dict[str, Any] = {}):
        return await self._post("/api/v1/memory/ingest", {
            "experiment_id": experiment_id,
            "event_type": event_type,
            "severity": severity,
            "summary": summary,
            "metadata_json": metadata
        })

    async def log_metrics(self, experiment_id: str, metrics: Dict[str, float]):
        return await self._post("/api/v1/monitor/stream_metrics", {
            "experiment_id": experiment_id,
            "metrics": metrics
        })

    async def extract_from_logs(self, text: str, experiment_id: Optional[str] = None):
        return await self._post("/api/v1/memory/extract_events", {
            "text": text,
            "experiment_id": experiment_id
        })

    async def get_intervention(self, experiment_id: str, failure_type: str, current_state: Dict[str, Any] = {}):
        return await self._post("/api/v1/monitor/recommend_intervention", {
            "experiment_id": experiment_id,
            "failure_type": failure_type,
            "current_state": current_state
        })

    async def log_recommendation_outcome(self, experiment_id: str, action: str, was_successful: bool, metrics_delta: Dict[str, Any] = {}):
        return await self._post("/api/v1/monitor/log_outcome", {
            "experiment_id": experiment_id,
            "action_taken": action,
            "was_successful": was_successful,
            "metrics_delta": metrics_delta
        })

    async def listen_for_commands(self, experiment_id: str, callback):
        import websockets
        ws_url = self.base_url.replace("http", "ws") + f"/ws/intervention/{experiment_id}"
        
        while True:
            try:
                async with websockets.connect(ws_url) as websocket:
                    logging.info(f"Connected to Intervention Channel: {experiment_id}")
                    async for message in websocket:
                        try:
                            command = json.loads(message)
                            await callback(command)
                        except Exception as e:
                            logging.error(f"Error processing command: {e}")
            except Exception as e:
                logging.warning(f"WebSocket connection lost, retrying in 5s: {e}")
                await asyncio.sleep(5)
