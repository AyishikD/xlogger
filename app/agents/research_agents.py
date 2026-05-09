from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.base import BaseAgent
from app.services.root_cause_engine import root_cause_engine
from app.services.intervention_engine import intervention_engine
from app.services.postmortem_generator import postmortem_generator

class FailureAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__("FailureAnalysisAgent")

    async def process(self, db: AsyncSession, input_data: Dict[str, Any]) -> Dict[str, Any]:
        event_id = input_data.get("event_id")
        if not event_id:
            return {"error": "Missing event_id"}
        
        analysis = await root_cause_engine.analyze_failure(db, event_id)
        return {
            "agent": self.name,
            "status": "completed",
            "findings": analysis
        }

class InterventionAgent(BaseAgent):
    def __init__(self):
        super().__init__("InterventionAgent")

    async def process(self, db: AsyncSession, input_data: Dict[str, Any]) -> Dict[str, Any]:
        experiment_id = input_data.get("experiment_id")
        failure_type = input_data.get("failure_type")
        
        recommendations = await intervention_engine.recommend_intervention(
            experiment_id, failure_type, input_data.get("current_state", {})
        )
        
        # Add config patch generation logic
        patches = []
        for rec in recommendations:
            if rec["action"] == "REDUCE_LR":
                patches.append({"lr": input_data.get("current_lr", 1e-4) * 0.5})
            if rec["action"] == "REDUCE_BATCH_SIZE":
                patches.append({"batch_size": input_data.get("current_batch_size", 32) // 2})

        return {
            "agent": self.name,
            "recommendations": recommendations,
            "suggested_patches": patches
        }

class PostmortemAgent(BaseAgent):
    def __init__(self):
        super().__init__("PostmortemAgent")

    async def process(self, db: AsyncSession, input_data: Dict[str, Any]) -> Dict[str, Any]:
        experiment_id = input_data.get("experiment_id")
        postmortem = await postmortem_generator.generate_postmortem(db, experiment_id)
        return {
            "agent": self.name,
            "postmortem": postmortem
        }
