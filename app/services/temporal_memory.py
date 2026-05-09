from typing import List, Dict, Any, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import MemoryEvent, Experiment
from app.models.enums import EventType
import datetime

class TemporalMemory:
    async def get_event_recurrence(
        self, 
        db: AsyncSession, 
        event_type: EventType,
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze the recurrence and temporal evolution of a specific event type.
        """
        stmt = select(MemoryEvent).where(MemoryEvent.event_type == event_type)
        
        # Add metadata filters if provided
        if metadata_filters:
            for key, value in metadata_filters.items():
                stmt = stmt.where(MemoryEvent.metadata_json[key].as_string() == str(value))
        
        result = await db.execute(stmt)
        events = result.scalars().all()
        
        if not events:
            return {"count": 0, "status": "no_occurrences"}

        timestamps = [e.created_at for e in events]
        first_seen = min(timestamps)
        last_seen = max(timestamps)
        count = len(events)
        
        # Calculate frequency (events per week)
        span_weeks = max(1.0, (last_seen - first_seen).days / 7.0)
        frequency = count / span_weeks

        # Trend analysis (comparing last 30 days to previous period)
        now = datetime.datetime.now(datetime.timezone.utc)
        thirty_days_ago = now - datetime.timedelta(days=30)
        recent_count = len([t for t in timestamps if t > thirty_days_ago])
        
        trend = "stable"
        if recent_count > (count / span_weeks) * 4: # Crude check for spike
            trend = "increasing"
        elif recent_count < (count / span_weeks) * 0.5:
            trend = "decreasing"

        return {
            "event_type": event_type,
            "count": count,
            "first_seen": first_seen.isoformat(),
            "last_seen": last_seen.isoformat(),
            "frequency_per_week": round(frequency, 2),
            "trend": trend,
            "is_recurring": count > 1
        }

    async def detect_regressions(
        self, 
        db: AsyncSession, 
        experiment_id: str
    ) -> List[Dict[str, Any]]:
        """
        Identify if current experiment shows regressions compared to historical baseline.
        """
        # 1. Get current experiment metrics
        exp_stmt = select(MemoryEvent).where(
            and_(
                MemoryEvent.experiment_id == experiment_id,
                MemoryEvent.metadata_json.has_key("metrics")
            )
        )
        exp_result = await db.execute(exp_stmt)
        current_events = exp_result.scalars().all()
        
        if not current_events:
            return []

        # 2. Extract latest metrics
        latest_event = sorted(current_events, key=lambda e: e.created_at)[-1]
        current_metrics = latest_event.metadata_json.get("metrics", {})

        # 3. Compare with historical averages for similar experiments
        # (Simplified: compare with all historical events of same type)
        regressions = []
        for metric_name, current_val in current_metrics.items():
            # In a real system, we'd filter by model_family, etc.
            if not isinstance(current_val, (int, float)):
                continue
                
            # Compute historical average for this metric
            # This is expensive in SQL, ideally cached or pre-computed
            # For now, we just mock the logic
            historical_avg = 0.5 # Placeholder
            threshold = 1.1 # 10% regression threshold
            
            if "loss" in metric_name.lower() and current_val > historical_avg * threshold:
                regressions.append({
                    "metric": metric_name,
                    "current": current_val,
                    "baseline": historical_avg,
                    "severity": "high"
                })
        
        return regressions

temporal_memory = TemporalMemory()
