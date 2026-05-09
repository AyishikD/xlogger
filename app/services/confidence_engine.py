from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ConfidenceWeights(BaseModel):
    evidence_count: float = 0.4
    recurrence_frequency: float = 0.2
    temporal_consistency: float = 0.1
    embedding_density: float = 0.2
    metadata_overlap: float = 0.1

class ConfidenceEngine:
    def __init__(self, weights: Optional[ConfidenceWeights] = None):
        self.weights = weights or ConfidenceWeights()

    def compute_score(
        self,
        evidence_count: int,
        recurrence_frequency: float,  # frequency per unit time
        temporal_consistency: float,   # 0 to 1, how consistent is the pattern over time
        avg_embedding_similarity: float,
        metadata_overlap_ratio: float
    ) -> float:
        """
        Compute a normalized confidence score (0.0 to 1.0) for a learning or pattern.
        """
        # Normalize evidence count (logarithmic saturation)
        # 1 evidence = ~0.2, 5 = ~0.6, 20+ = ~0.95
        import math
        count_score = min(1.0, math.log(evidence_count + 1) / math.log(20))
        
        # Recurrence frequency (assuming 0 to 1 normalization)
        freq_score = min(1.0, recurrence_frequency)
        
        # Temporal consistency (already 0 to 1)
        consistency_score = min(1.0, temporal_consistency)
        
        # Embedding density (already 0 to 1)
        similarity_score = min(1.0, avg_embedding_similarity)
        
        # Metadata overlap (already 0 to 1)
        overlap_score = min(1.0, metadata_overlap_ratio)

        weighted_score = (
            (count_score * self.weights.evidence_count) +
            (freq_score * self.weights.recurrence_frequency) +
            (consistency_score * self.weights.temporal_consistency) +
            (similarity_score * self.weights.embedding_density) +
            (overlap_score * self.weights.metadata_overlap)
        )

        return float(round(min(1.0, weighted_score), 4))

    def evaluate_hypothesis_confidence(self, hits: List[Dict[str, Any]]) -> float:
        """
        Evaluate confidence for a root-cause hypothesis based on search hits.
        """
        if not hits:
            return 0.0
            
        avg_similarity = sum(h["similarity"] for h in hits) / len(hits)
        evidence_count = len(hits)
        
        # Heuristic for hypothesis confidence
        return self.compute_score(
            evidence_count=evidence_count,
            recurrence_frequency=0.5, # Assume moderate frequency for single hypothesis
            temporal_consistency=0.7, 
            avg_embedding_similarity=avg_similarity,
            metadata_overlap_ratio=0.5
        )

confidence_engine = ConfidenceEngine()
