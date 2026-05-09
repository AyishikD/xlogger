import re
from typing import Optional
from app.events.extractors.base import BaseExtractor, CanonicalEventResult
from app.models.enums import EventType, Severity

class CUDAOutOfMemoryExtractor(BaseExtractor):
    @property
    def event_type(self) -> EventType:
        return EventType.CUDA_OOM

    def extract(self, text: str) -> Optional[CanonicalEventResult]:
        # Pattern: RuntimeError: CUDA out of memory. Tried to allocate 512 MiB
        pattern = r"CUDA out of memory\. Tried to allocate ([\d\.]+) ([M|G]iB)"
        match = re.search(pattern, text)
        
        if not match:
            return None
            
        amount = float(match.group(1))
        unit = match.group(2)
        
        # Convert to MB for consistency if needed
        allocation_mb = amount if unit == "MiB" else amount * 1024
        
        return CanonicalEventResult(
            event_type=self.event_type,
            severity=Severity.CRITICAL,
            summary=f"CUDA Out of Memory: Failed to allocate {amount} {unit}",
            metadata={
                "allocation_mb": allocation_mb,
                "unit": unit,
                "raw_allocation": amount
            },
            content=text
        )
