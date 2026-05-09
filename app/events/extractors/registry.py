from typing import List, Optional
from app.events.extractors.base import BaseExtractor, CanonicalEventResult
from app.events.extractors.cuda import CUDAOutOfMemoryExtractor
from app.events.extractors.nan import NaNDetectedExtractor
from app.events.extractors.loss import LossDivergenceExtractor
from app.events.extractors.tokenizer import TokenizerMismatchExtractor
from app.events.extractors.checkpoint import CheckpointCorruptionExtractor

class ExtractorRegistry:
    def __init__(self):
        self._extractors: List[BaseExtractor] = []
        self._initialize_default_extractors()

    def _initialize_default_extractors(self):
        self.register(CUDAOutOfMemoryExtractor())
        self.register(NaNDetectedExtractor())
        self.register(LossDivergenceExtractor())
        self.register(TokenizerMismatchExtractor())
        self.register(CheckpointCorruptionExtractor())

    def register(self, extractor: BaseExtractor):
        self._extractors.append(extractor)

    def extract_all(self, text: str) -> List[CanonicalEventResult]:
        results = []
        for extractor in self._extractors:
            result = extractor.extract(text)
            if result:
                results.append(result)
        return results

extractor_registry = ExtractorRegistry()
