from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import MemoryEvent
from app.retrieval.hybrid_retriever import hybrid_retriever
from app.models.enums import Severity

class RootCauseEngine:
    async def analyze_failure(
        self, 
        db: AsyncSession, 
        event_id: str
    ) -> Dict[str, Any]:
        """
        Analyze a failure event to infer likely causes based on historical memory.
        """
        # 1. Fetch the event
        from app.repositories.memory_event import memory_event_repo
        event = await memory_event_repo.get(db, event_id)
        if not event or event.severity not in [Severity.ERROR, Severity.CRITICAL]:
            return {"error": "Event not found or not a failure event"}

        # 2. Retrieve Similar Historical Failures
        similar_memories = await hybrid_retriever.search(
            db, 
            query_text=event.summary,
            event_type=event.event_type,
            limit=5
        )

        likely_causes = []
        shared_patterns = []
        recommended_actions = []
        supporting_events = []

        # 3. Pattern Detection & Reasoning
        # If we have similar events, look at their metadata and solutions
        for hit in similar_memories:
            other_event = hit["event"]
            if other_event.id == event.id:
                continue

            supporting_events.append({
                "id": str(other_event.id),
                "summary": other_event.summary,
                "similarity": hit["similarity"]
            })

            # Check for shared metadata patterns (e.g. same GPU, same model, same learning rate)
            for key in ["model_type", "precision", "gpu_type", "batch_size"]:
                if key in event.metadata_json and key in other_event.metadata_json:
                    if event.metadata_json[key] == other_event.metadata_json[key]:
                        shared_patterns.append(f"Shared {key}: {event.metadata_json[key]}")

            # Extract previously recorded "causes" or "resolutions" from metadata if they exist
            if "resolution" in other_event.metadata_json:
                likely_causes.append(f"Likely related to {other_event.event_type.value.lower()}")
                recommended_actions.append(other_event.metadata_json["resolution"])

        # 4. Fallback/Heuristic Reasoning
        if event.event_type.value == "CUDA_OOM":
            likely_causes.append("Insufficient GPU memory for current batch size/model configuration.")
            recommended_actions.append("Decrease batch size or use gradient accumulation.")
            recommended_actions.append("Check for memory leaks in data loaders.")
        
        if event.event_type.value == "NAN_DETECTED":
            likely_causes.append("Numerical instability (likely exploding gradients or division by zero).")
            recommended_actions.append("Check learning rate and weight initialization.")
            recommended_actions.append("Enable anomaly detection in your framework.")

        # 5. Synthesis
        return {
            "event_summary": event.summary,
            "likely_causes": list(set(likely_causes)),
            "confidence": min(0.9, 0.4 + (len(supporting_events) * 0.1)),
            "supporting_events": supporting_events,
            "shared_patterns": list(set(shared_patterns)),
            "recommended_actions": list(set(recommended_actions))
        }

root_cause_engine = RootCauseEngine()
