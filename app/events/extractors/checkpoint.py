import re
from typing import Optional
from app.events.extractors.base import BaseExtractor, CanonicalEventResult
from app.models.enums import EventType, Severity

class CheckpointCorruptionExtractor(BaseExtractor):
    @property
    def event_type(self) -> EventType:
        return EventType.CHECKPOINT_CORRUPTION

    def extract(self, text: str) -> Optional[CanonicalEventResult]:
        # Pattern: Checkpoint at path/to/model.pt is corrupted
        # Pattern: Error loading state_dict: key mismatch or unexpected EOF
        patterns = [
            r"Checkpoint .* is corrupted",
            r"unexpected EOF while reading checkpoint",
            r"Error loading state_dict",
            r"unpickling stack underflow"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return CanonicalEventResult(
                    event_type=self.event_type,
                    severity=Severity.CRITICAL,
                    summary="Checkpoint Corruption Detected",
                    metadata={"pattern": pattern},
                    content=text
                )
        
        return None
