import re
from typing import Optional
from app.events.extractors.base import BaseExtractor, CanonicalEventResult
from app.models.enums import EventType, Severity

class TokenizerMismatchExtractor(BaseExtractor):
    @property
    def event_type(self) -> EventType:
        return EventType.TOKENIZER_MISMATCH

    def extract(self, text: str) -> Optional[CanonicalEventResult]:
        # Pattern: Tokenizer vocabulary size (50257) does not match model embedding size (50260)
        # Pattern: Resize tokenizer: from 32000 to 32005
        patterns = [
            r"vocab size \((\d+)\) does not match .* size \((\d+)\)",
            r"Resize tokenizer: from (\d+) to (\d+)",
            r"Tokenizer mismatch detected"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                metadata = {"pattern": pattern}
                if len(groups) == 2:
                    metadata["tokenizer_size"] = int(groups[0])
                    metadata["model_size"] = int(groups[1])
                    summary = f"Tokenizer mismatch: {groups[0]} vs {groups[1]}"
                else:
                    summary = "Tokenizer mismatch detected"
                
                return CanonicalEventResult(
                    event_type=self.event_type,
                    severity=Severity.WARNING,
                    summary=summary,
                    metadata=metadata,
                    content=text
                )
        
        return None
