from typing import List, Dict, Any, Optional
import json
from app.core.redis import redis_client

class EventStream:
    STREAM_KEY_ALERTS = "modellogger:stream:alerts"
    STREAM_KEY_METRICS = "modellogger:stream:metrics"
    STREAM_KEY_LEARNINGS = "modellogger:stream:learnings"

    async def publish_metric(self, experiment_id: str, metric_data: Dict[str, float]):
        """
        Publish metric to Redis stream.
        """
        data = {
            "experiment_id": experiment_id,
            "metrics": json.dumps(metric_data),
            "timestamp": "now"
        }
        if not redis_client.redis:
            await redis_client.connect()
        await redis_client.redis.xadd(self.STREAM_KEY_METRICS, data, maxlen=10000)

    async def publish_alert(self, alert_data: Dict[str, Any]):
        """
        Publish alert to Redis stream.
        """
        data = {
            "alert": json.dumps(alert_data),
            "severity": alert_data.get("severity", "info")
        }
        if not redis_client.redis:
            await redis_client.connect()
        await redis_client.redis.xadd(self.STREAM_KEY_ALERTS, data, maxlen=5000)
        print(f"DEBUG: Published alert to Redis stream: {alert_data.get('type')}")

    async def get_live_alerts(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch most recent alerts from the stream.
        """
        if not redis_client.redis:
            await redis_client.connect()
        
        # XREVRANGE key + - COUNT count
        results = await redis_client.redis.xrevrange(self.STREAM_KEY_ALERTS, max="+", min="-", count=count)
        
        alerts = []
        for _, data in results:
            if b"alert" in data:
                alerts.append(json.loads(data[b"alert"]))
            elif "alert" in data:
                alerts.append(json.loads(data["alert"]))
        return alerts

event_stream = EventStream()
