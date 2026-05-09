from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.models import Learning, Relationship
from app.services.confidence_engine import confidence_engine
import datetime

class MemoryEvolution:
    async def evolve_memory(self, db: AsyncSession):
        """
        Continuously evolve organizational memory by merging, decaying, and reinforcing.
        """
        # 1. Merge Duplicate Learnings
        # (Using simple title/content similarity)
        learnings = (await db.execute(select(Learning))).scalars().all()
        # Logic to merge would go here...

        # 2. Update Confidence for all learnings
        for learning in learnings:
            meta = learning.metadata_json
            count = meta.get("occurrence_count", 1)
            last_seen = datetime.datetime.fromisoformat(meta.get("last_seen", datetime.datetime.now().isoformat()))
            
            # Decay confidence if not seen recently
            days_since = (datetime.datetime.now(datetime.timezone.utc) - last_seen).days
            decay_factor = max(0.5, 1.0 - (days_since / 365.0)) # Decay over a year
            
            # Recalculate base confidence
            # In a real system, we'd fetch the latest evidence count
            new_confidence = confidence_engine.compute_score(
                evidence_count=count,
                recurrence_frequency=meta.get("frequency", 0.5),
                temporal_consistency=meta.get("consistency", 0.7),
                avg_embedding_similarity=0.9,
                metadata_overlap_ratio=0.6
            ) * decay_factor
            
            meta["confidence"] = round(new_confidence, 4)
            learning.metadata_json = meta
            db.add(learning)

        # 3. Prune low-confidence relationships
        # (Relationship decay logic)
        # delete_stmt = delete(Relationship).where(Relationship.metadata_json["confidence"].as_float() < 0.2)
        # await db.execute(delete_stmt)

        await db.commit()

    async def reinforce_pattern(self, db: AsyncSession, learning_id: str, evidence_id: str):
        """
        Reinforce a learning with new evidence.
        """
        learning = await db.get(Learning, learning_id)
        if not learning:
            return

        meta = learning.metadata_json
        meta["occurrence_count"] = meta.get("occurrence_count", 0) + 1
        meta["last_seen"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if evidence_id not in meta.get("supporting_events", []):
            meta.get("supporting_events", []).append(evidence_id)
            
        learning.metadata_json = meta
        db.add(learning)
        await db.commit()

memory_evolution = MemoryEvolution()
