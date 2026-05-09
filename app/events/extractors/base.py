from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from app.models.enums import EventType, Severity

class CanonicalEventResult(BaseModel):
    event_type: EventType
    severity: Severity
    summary: str
    metadata: Dict[str, Any] = {}
    content: Optional[str] = None

class BaseExtractor(ABC):
    @property
    @abstractmethod
    def event_type(self) -> EventType:
        pass

    @abstractmethod
    def extract(self, text: str) -> Optional[CanonicalEventResult]:
        """
        Attempt to extract a canonical event from the given text/logs.
        Returns None if no match is found.
        """
        pass
