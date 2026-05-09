from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Learning, MemoryEvent, Experiment
from app.models.enums import LearningType, Severity
from app.services.confidence_engine import confidence_engine
from app.services.embedding import embedding_service
from app.repositories.memory_event import memory_event_repo
import datetime
import logging

class LearningEngine:
    async def generate_learning_from_cluster(
        self, 
        db: AsyncSession, 
        events: List[MemoryEvent],
        learning_type: LearningType = LearningType.FAILURE_PATTERN
    ) -> Optional[Learning]:
        """
        Aggregate a cluster of events into a single organizational learning.
        Deduplicates against existing learnings.
        """
        if not events:
            return None

        logger = logging.getLogger("learning_engine")
        logger.info(f"Generating learning from {len(events)} events...")
        common_type = events[0].event_type.value
        title = f"Recurring {common_type.replace('_', ' ').title()}"
        
        stmt = select(Learning).where(Learning.title == title)
        existing_res = await db.execute(stmt)
        existing_learning = existing_res.scalar_one_or_none()
        
        if existing_learning:
            # Reinforce existing learning
            for e in events:
                await self.reinforce_learning(db, existing_learning, e)
            return existing_learning
        
        summaries = [e.summary for e in events]
        
        # 1. Synthesize title and content using LLM (Llama-3/Mistral)
        common_type = events[0].event_type.value
        title = f"Recurring {common_type.replace('_', ' ').title()}"
        
        from app.services.llm_service import llm_service
        synthesis = await llm_service.synthesize_learning(
            common_type, 
            [e.summary for e in events]
        )
        
        content = synthesis["content"]
        recommendations = synthesis["recommendations"]
        llm_confidence = synthesis["confidence"]

        # 2. Compute Confidence
        timestamps = [e.created_at for e in events]
        span_days = (max(timestamps) - min(timestamps)).days + 1
        recurrence_freq = len(events) / span_days
        
        confidence = confidence_engine.compute_score(
            evidence_count=len(events),
            recurrence_frequency=recurrence_freq,
            temporal_consistency=0.8,
            avg_embedding_similarity=0.9,
            metadata_overlap_ratio=0.6
        )

        # 3. Create Learning object
        learning_metadata = {
            "learning_type": learning_type.value,
            "confidence": confidence,
            "supporting_experiments": list(set([str(e.experiment_id) for e in events])),
            "supporting_events": [str(e.id) for e in events],
            "recommendations": recommendations,
            "occurrence_count": len(events),
            "first_seen": min(timestamps).isoformat(),
            "last_seen": max(timestamps).isoformat()
        }

        # Generate embedding for the learning itself
        learning_text = f"{title}. {content}"
        embedding = await embedding_service.generate_embedding(learning_text)

        learning = Learning(
            title=title,
            content=content,
            metadata_json=learning_metadata,
            embedding=embedding
        )

        db.add(learning)
        await db.commit()
        await db.refresh(learning)
        
        logger.info(f"Successfully created learning: {learning.id} - {learning.title}")
        return learning

    async def reinforce_learning(self, db: AsyncSession, learning: Learning, event: MemoryEvent):
        """
        Update an existing learning with new evidence.
        """
        meta = learning.metadata_json
        
        # Avoid duplicate events
        supporting_events = meta.get("supporting_events", [])
        if str(event.id) not in supporting_events:
            supporting_events.append(str(event.id))
            meta["supporting_events"] = supporting_events
            meta["occurrence_count"] = meta.get("occurrence_count", 0) + 1
            
            # Update last_seen
            meta["last_seen"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            # Recalculate confidence (simplified)
            meta["confidence"] = min(0.98, meta.get("confidence", 0.5) + 0.02)
            
            learning.metadata_json = meta
            db.add(learning)
            await db.commit()

learning_engine = LearningEngine()
