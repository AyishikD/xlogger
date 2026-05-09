from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.models import Learning

class CRUDLearning(BaseRepository[Learning]):
    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[Learning]:
        stmt = select(self.model).offset(skip).limit(limit).order_by(self.model.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

learning_repo = CRUDLearning(Learning)
