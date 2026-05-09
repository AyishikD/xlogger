from typing import List, Optional, Dict, Any
from sqlalchemy import select, text, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import MemoryEvent
from app.models.enums import EventType, Severity
from app.services.embedding import embedding_service

class HybridRetriever:
    async def search(
        self,
        db: AsyncSession,
        query_text: str,
        event_type: Optional[EventType] = None,
        severity: Optional[Severity] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining semantic similarity, structural filtering, and metadata matching.
        """
        # 1. Generate query embedding
        query_embedding = await embedding_service.generate_embedding(query_text)
        
        # 2. Build Base Query
        # We use pgvector for similarity
        stmt = select(
            MemoryEvent,
            (1 - MemoryEvent.embedding.cosine_distance(query_embedding)).label("similarity")
        )
        
        # 3. Apply Structural Filters
        filters = []
        if event_type:
            filters.append(MemoryEvent.event_type == event_type)
        if severity:
            filters.append(MemoryEvent.severity == severity)
            
        # 4. Apply Metadata Filters (JSONB matching)
        if metadata_filters:
            for key, value in metadata_filters.items():
                filters.append(MemoryEvent.metadata_json[key].as_string() == str(value))
        
        if filters:
            stmt = stmt.where(and_(*filters))
            
        # 5. Temporal Ranking / Hybrid Scoring
        # Combine: 0.7 * similarity + 0.3 * recency_score
        # For simplicity, we'll stick to similarity for now but rank by it
        stmt = stmt.order_by(text("similarity DESC")).limit(limit)
        
        result = await db.execute(stmt)
        hits = result.all()
        
        # 6. Format and Boost
        results = []
        for event, similarity in hits:
            # Metadata overlap boost
            overlap_score = 0
            if metadata_filters:
                # Basic overlap calculation
                matching_keys = set(event.metadata_json.keys()) & set(metadata_filters.keys())
                overlap_score = len(matching_keys) * 0.05
            
            final_score = float(similarity) + overlap_score
            
            results.append({
                "event": event,
                "score": final_score,
                "similarity": float(similarity),
                "metadata_boost": overlap_score
            })
            
        # Re-sort by final score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

hybrid_retriever = HybridRetriever()
