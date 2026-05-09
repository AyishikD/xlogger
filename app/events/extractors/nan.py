import re
from typing import Optional
from app.events.extractors.base import BaseExtractor, CanonicalEventResult
from app.models.enums import EventType, Severity

class NaNDetectedExtractor(BaseExtractor):
    @property
    def event_type(self) -> EventType:
        return EventType.NAN_DETECTED

    def extract(self, text: str) -> Optional[CanonicalEventResult]:
        # Common patterns for NaN detection in PyTorch/TensorFlow
        patterns = [
            r"NaN detected in ([\w\.]+)",
            r"Loss is NaN",
            r"gradient is NaN",
            r"Found inf or nan in ([\w\.]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                component = match.group(1) if match.groups() else "unknown"
                return CanonicalEventResult(
                    event_type=self.event_type,
                    severity=Severity.ERROR,
                    summary=f"NaN/Inf Detected in {component}",
                    metadata={
                        "component": component,
                        "pattern_matched": pattern
                    },
                    content=text
                )
        
        return None
