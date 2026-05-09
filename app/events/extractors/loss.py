import re
from typing import Optional
from app.events.extractors.base import BaseExtractor, CanonicalEventResult
from app.models.enums import EventType, Severity

class LossDivergenceExtractor(BaseExtractor):
    @property
    def event_type(self) -> EventType:
        return EventType.LOSS_DIVERGENCE

    def extract(self, text: str) -> Optional[CanonicalEventResult]:
        # Pattern: Loss spiked from 1.2 to 500.5
        # Pattern: Loss diverged: 1e9
        patterns = [
            r"Loss spiked from ([\d\.]+) to ([\d\.]+)",
            r"Loss diverged: ([\d\.e\-\+]+)",
            r"Instability detected: loss ([\d\.e\-\+]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                metadata = {"pattern": pattern}
                if len(groups) == 2:
                    metadata["previous_loss"] = float(groups[0])
                    metadata["current_loss"] = float(groups[1])
                    summary = f"Loss spiked: {groups[0]} -> {groups[1]}"
                else:
                    metadata["current_loss"] = float(groups[0])
                    summary = f"Loss diverged: {groups[0]}"
                
                return CanonicalEventResult(
                    event_type=self.event_type,
                    severity=Severity.ERROR,
                    summary=summary,
                    metadata=metadata,
                    content=text
                )
        
        return None
