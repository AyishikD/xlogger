from typing import List, Dict, Any
from app.models.models import MemoryEvent, Experiment
from app.models.enums import EventType, Severity

class ExperimentSummarizer:
    def summarize(self, experiment: Experiment, events: List[MemoryEvent]) -> str:
        """
        Generates a concise research memory summary based on experiment events.
        """
        if not events:
            return f"Experiment '{experiment.name}' has no recorded events."

        # Sort events by time
        sorted_events = sorted(events, key=lambda e: e.created_at)
        
        # Categorize events
        critical_events = [e for e in sorted_events if e.severity in [Severity.CRITICAL, Severity.ERROR]]
        terminal_event = sorted_events[-1] if sorted_events else None
        
        # Build summary components
        summary_parts = []
        
        # 1. State current status
        if terminal_event and terminal_event.event_type == EventType.TRAINING_STOPPED:
            summary_parts.append("Training completed/stopped.")
        elif critical_events:
            summary_parts.append(f"Training encountered {len(critical_events)} critical issues.")
        
        # 2. Add key failure patterns
        unique_critical_types = {e.event_type for e in critical_events}
        if unique_critical_types:
            failure_str = ", ".join([t.value.replace('_', ' ').lower() for t in unique_critical_types])
            summary_parts.append(f"Key issues detected: {failure_str}.")
        
        # 3. Incorporate metrics if available in metadata
        latest_metrics = {}
        for event in reversed(sorted_events):
            if "metrics" in event.metadata_json:
                latest_metrics = event.metadata_json["metrics"]
                break
        
        if latest_metrics:
            metric_str = " | ".join([f"{k}: {v}" for k, v in latest_metrics.items()])
            summary_parts.append(f"Final metrics: {metric_str}.")

        # 4. Synthesize narrative
        if not critical_events and terminal_event:
            return f"Experiment {experiment.name} proceeded normally. " + " ".join(summary_parts)
        
        narrative = f"Experiment {experiment.name} "
        if critical_events:
            first_fail = critical_events[0]
            narrative += f"failed/diverged during {first_fail.event_type.value.lower()}. "
        
        return narrative + " ".join(summary_parts)

summarizer = ExperimentSummarizer()
