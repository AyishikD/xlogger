from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import MemoryEvent, Relationship
from app.models.enums import RelationshipType
from app.repositories.memory_event import memory_event_repo
from app.db.session import AsyncSessionLocal

class RelationshipBuilder:
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold

    async def build_relationships_for_event(self, db: AsyncSession, event: MemoryEvent):
        """
        Find and build relationships between a new event and existing memories.
        """
        if event.embedding is None:
            return

        # 1. Find similar events
        # We need to pass the list[float] from the vector
        embedding_list = list(event.embedding)
        similar_results = await memory_event_repo.find_similar(
            db, 
            embedding=embedding_list, 
            limit=10
        )

        for other_event, score in similar_results:
            if other_event.id == event.id or score is None:
                continue

            if score >= self.similarity_threshold:
                # Create SIMILAR_TO relationship
                rel = Relationship(
                    source_id=event.id,
                    target_id=other_event.id,
                    relationship_type=RelationshipType.SIMILAR_TO,
                    metadata_json={"similarity_score": float(score)}
                )
                db.add(rel)

                # Check for SHARED_FAILURE_PATTERN
                if event.event_type == other_event.event_type and event.event_type.value in ["CUDA_OOM", "NAN_DETECTED", "LOSS_DIVERGENCE"]:
                    rel_fail = Relationship(
                        source_id=event.id,
                        target_id=other_event.id,
                        relationship_type=RelationshipType.CAUSED_BY, # Using existing enum for shared cause logic
                        metadata_json={"pattern": event.event_type.value}
                    )
                    db.add(rel_fail)

        # 2. Temporal relationships (e.g. regressed_after)
        # (This would require more complex logic across experiments, simplified for now)
        
        await db.commit()

relationship_builder = RelationshipBuilder()
