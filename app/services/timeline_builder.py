from typing import List, Dict, Any, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import MemoryEvent, Experiment, Relationship
import uuid

class TimelineBuilder:
    async def build_experiment_timeline(
        self, 
        db: AsyncSession, 
        experiment_id: str
    ) -> List[Dict[str, Any]]:
        """
        Build a chronological timeline of events, regressions, and relationship evolution for an experiment.
        """
        # 1. Fetch all events for the experiment
        stmt = select(MemoryEvent).where(MemoryEvent.experiment_id == experiment_id).order_by(MemoryEvent.created_at)
        result = await db.execute(stmt)
        events = result.scalars().all()

        timeline = []
        for event in events:
            entry = {
                "timestamp": event.created_at.isoformat(),
                "event_id": str(event.id),
                "type": event.event_type.value,
                "severity": event.severity.value,
                "summary": event.summary,
                "meta": event.metadata_json
            }
            
            # Fetch relationships for this event
            rel_stmt = select(Relationship).where(Relationship.source_id == event.id)
            rel_result = await db.execute(rel_stmt)
            rels = rel_result.scalars().all()
            
            if rels:
                entry["relationships"] = [
                    {"target": str(r.target_id), "type": r.relationship_type.value}
                    for r in rels
                ]
                
            timeline.append(entry)

        return timeline

timeline_builder = TimelineBuilder()
