from typing import List, Optional
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import MemoryEvent
from app.repositories.base import BaseRepository
from app.models.enums import EventType

class MemoryEventRepository(BaseRepository[MemoryEvent]):
    def __init__(self):
        super().__init__(MemoryEvent)

    async def find_similar(
        self, 
        db: AsyncSession, 
        embedding: List[float], 
        event_type: Optional[EventType] = None,
        limit: int = 5
    ) -> List[tuple[MemoryEvent, float]]:
        # Using pgvector cosine distance (<=>)
        # 1 - (embedding <=> column) = cosine similarity
        
        query = select(
            MemoryEvent,
            (1 - MemoryEvent.embedding.cosine_distance(embedding)).label("similarity")
        )
        
        if event_type:
            query = query.where(MemoryEvent.event_type == event_type)
            
        query = query.order_by(text("similarity DESC")).limit(limit)
        
        result = await db.execute(query)
        return result.all()

memory_event_repo = MemoryEventRepository()
