from typing import List, Dict, Any, Optional
from app.services.anomaly_engine import anomaly_engine
from app.services.event_stream import event_stream
from app.core.redis import redis_client

class LiveMonitor:
    def __init__(self):
        self.metric_buffer: Dict[str, Dict[str, List[float]]] = {} # experiment_id -> {metric_name: values}
        self.sent_alerts_cache: set = set()

    async def _has_sent_alert(self, experiment_id: str, alert_type: str) -> bool:
        key = f"alert_sent:{experiment_id}:{alert_type}"
        if key in self.sent_alerts_cache:
            return True
        val = await redis_client.get(key)
        if val:
            self.sent_alerts_cache.add(key)
            return True
        return False

    async def _mark_alert_sent(self, experiment_id: str, alert_type: str):
        key = f"alert_sent:{experiment_id}:{alert_type}"
        self.sent_alerts_cache.add(key)
        # Expire after 1 hour (enough for most experiments)
        await redis_client.set(key, "1", ex=3600)

    async def process_metrics(
        self, 
        experiment_id: str, 
        metrics: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Process incoming metrics for an experiment and detect live anomalies.
        """
        if experiment_id not in self.metric_buffer:
            self.metric_buffer[experiment_id] = {}

        # 1. Update Buffers
        for metric, val in metrics.items():
            if metric not in self.metric_buffer[experiment_id]:
                self.metric_buffer[experiment_id][metric] = []
            self.metric_buffer[experiment_id][metric].append(val)
            # Keep only last 100 values
            if len(self.metric_buffer[experiment_id][metric]) > 100:
                self.metric_buffer[experiment_id][metric].pop(0)

        # 2. Run Anomaly Detection
        anomalies = anomaly_engine.analyze_metrics(self.metric_buffer[experiment_id])
        
        alerts = []
        for anomaly in anomalies:
            # Include metric in alert type for better deduplication
            metric_str = "_".join(anomaly.affected_metrics)
            alert_type = f"STAT_ANOMALY_{anomaly.anomaly_type}_{metric_str}"
            
            if not await self._has_sent_alert(experiment_id, alert_type):
                alert = {
                    "experiment_id": experiment_id,
                    "type": "LIVE_ANOMALY",
                    "severity": anomaly.severity,
                    "metric": metric_str,
                    "data": anomaly.model_dump()
                }
                alerts.append(alert)
                await event_stream.publish_alert(alert)
                await self._mark_alert_sent(experiment_id, alert_type)
                print(f"SENT ALERT: {alert_type} for {experiment_id}")
            else:
                # Optional: log that it was blocked
                pass

        # 3. Handle Predictions (Dynamic)
        predictions = anomaly_engine.get_predictions(self.metric_buffer[experiment_id])
        if predictions:
            from app.websockets.manager import ws_manager
            # Broadcast predictions for UI sidebar
            await ws_manager.broadcast({
                "channel": "live_predictions",
                "experiment_id": experiment_id,
                "data": predictions
            })

        return alerts

live_monitor = LiveMonitor()
