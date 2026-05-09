from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def process(self, db: AsyncSession, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
