from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Experiment, MemoryEvent
from app.services.summarizer import summarizer
from app.services.root_cause_engine import root_cause_engine
from app.services.timeline_builder import timeline_builder
from app.services.temporal_memory import temporal_memory
import datetime

class PostmortemGenerator:
    async def generate_postmortem(
        self, 
        db: AsyncSession, 
        experiment_id: str
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive, structured research postmortem for a failed experiment.
        """
        # 1. Fetch Basic Context
        from app.repositories.experiment import experiment_repo
        experiment = await experiment_repo.get(db, experiment_id)
        if not experiment:
            return {"error": "Experiment not found"}

        # 2. Get Timeline and Failure Events
        timeline = await timeline_builder.build_experiment_timeline(db, experiment_id)
        failure_events = [e for e in timeline if e["severity"] in ["ERROR", "CRITICAL"]]
        
        # 3. Root Cause Analysis for the main failure
        analysis = {}
        if failure_events:
            main_failure_id = failure_events[-1]["event_id"]
            analysis = await root_cause_engine.analyze_failure(db, main_failure_id)

        # 4. Temporal Context (Is this a recurring issue?)
        recurrence = {}
        if failure_events:
            last_event_type = failure_events[-1]["type"]
            recurrence = await temporal_memory.get_event_recurrence(db, last_event_type)

        # 5. Synthesize Postmortem
        return {
            "experiment_name": experiment.name,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "summary": summarizer.summarize(experiment, []), # Need to fetch actual events if needed
            "status": "failed",
            "failure_timeline": failure_events,
            "root_cause_analysis": analysis,
            "recurrence_metrics": recurrence,
            "organizational_impact": "high" if recurrence.get("count", 0) > 5 else "medium",
            "remediation_status": "pending",
            "action_items": analysis.get("recommended_actions", [])
        }

postmortem_generator = PostmortemGenerator()
