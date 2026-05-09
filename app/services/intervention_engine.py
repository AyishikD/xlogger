from typing import List, Dict, Any, Optional
from sqlalchemy import select, func, Integer, cast
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import RecommendationOutcome, Learning
from app.models.enums import EventType

class InterventionPolicy:
    """Hard safety constraints for autonomous interventions"""
    MIN_LR_FLOOR = 1e-6
    MAX_INTERVENTIONS_PER_RUN = 3
    MIN_COOLDOWN_STEPS = 50
    CONFIDENCE_THRESHOLD = 0.8
    
    # Intervention Modes
    MODE_OBSERVE = "OBSERVE"     # Just log the suggestion
    MODE_RECOMMEND = "RECOMMEND" # UI notifications only
    MODE_AUTO = "AUTO"           # Actually change parameters

class InterventionEngine:
    async def recommend_intervention(
        self, 
        db: AsyncSession,
        experiment_id: str, 
        failure_type: str,
        current_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recommend corrective actions with safety bounds and confidence scores.
        """
        # 1. Fetch historical success rates
        stmt = select(
            RecommendationOutcome.action_taken,
            func.count(RecommendationOutcome.id).label("total"),
            func.sum(cast(RecommendationOutcome.was_successful, Integer)).label("successes")
        ).group_by(RecommendationOutcome.action_taken)
        
        result = await db.execute(stmt)
        stats = {row[0]: (row[2] / row[1] if row[1] > 0 else 0) for row in result.all()}

        # 2. Check Research Memory (Learnings)
        # Match against human-readable titles (e.g. "Loss Diverged" instead of "LOSS_DIVERGED")
        search_term = failure_type.replace("_", " ").title()
        learning_stmt = select(Learning).where(Learning.title.ilike(f"%{search_term}%"))
        learning_res = await db.execute(learning_stmt)
        related_learnings = learning_res.scalars().all()
        
        # 3. Base strategies
        base_recommendations = []
        if failure_type in ["NAN_DETECTED", "LOSS_DIVERGED", "DIVERGENCE_RISK"]:
            base_recommendations = ["ROLLBACK_AND_STABILIZE", "REDUCE_LR"]
        elif failure_type == "TRANSITORY_ANOMALY":
            base_recommendations = ["SKIP_BATCH"]
        else:
            base_recommendations = ["AUDIT_LOGS"]

        # 3. Apply Confidence Gating and Policy Bounds
        final_recs = []
        for action in base_recommendations:
            # Special Case: SKIP_BATCH for Transitory Anomalies is always high confidence
            if action == "SKIP_BATCH" and failure_type == "TRANSITORY_ANOMALY":
                final_recs.append({
                    "action": action,
                    "confidence": 0.95,
                    "reason": "Transient spike detected; preserving weights via batch skip.",
                    "description": self._get_description(action)
                })
                continue

            success_rate = stats.get(action, 0.4)
            
            # Policy: Only suggest if we meet confidence threshold OR if it's a known safety fix
            if success_rate >= InterventionPolicy.CONFIDENCE_THRESHOLD or action == "REDUCE_LR":
                
                # Check state-specific bounds (e.g. LR floor)
                if action == "REDUCE_LR":
                    current_lr = current_state.get("lr", 1.0)
                    if current_lr <= InterventionPolicy.MIN_LR_FLOOR:
                        continue # Policy violation: Cannot drop LR further
                
                # Boost confidence if we have research memory
                has_learning = False
                learning_reason = ""
                for l in related_learnings:
                    if action in l.content or action == "REDUCE_LR":
                        has_learning = True
                        learning_reason = f"Validated by Research Memory: '{l.title}'"
                        break

                # Intelligence Formula:
                # 1. Start with base success rate (or 0.4 if unknown)
                # 2. Add 0.2 if we have any successful history
                # 3. Add 0.3 if research memory exists
                base_score = stats.get(action, 0.4)
                
                final_confidence = base_score
                if stats.get(action, 0) > 0.7:
                    final_confidence += 0.1
                if has_learning:
                    final_confidence += 0.3
                
                final_confidence = min(0.95, final_confidence)
                
                final_recs.append({
                    "action": action,
                    "confidence": final_confidence,
                    "reason": learning_reason or f"Experimental confidence based on {stats.get(action, 0)*100:.0f}% success rate.",
                    "description": self._get_description(action)
                })

        # Sort by confidence
        final_recs.sort(key=lambda x: x["confidence"], reverse=True)

        return {
            "recommendations": final_recs,
            "policy_meta": {
                "max_interventions": InterventionPolicy.MAX_INTERVENTIONS_PER_RUN,
                "cooldown_required": InterventionPolicy.MIN_COOLDOWN_STEPS,
                "lr_floor": InterventionPolicy.MIN_LR_FLOOR
            }
        }

    def _get_description(self, action: str) -> str:
        detail_map = {
            "REDUCE_BATCH_SIZE": "Decrease batch_size by 50% for immediate recovery.",
            "REDUCE_LR": "Lower the learning rate (Bounded by Policy).",
            "ROLLBACK_AND_STABILIZE": "Revert to last healthy checkpoint and apply stability patch.",
            "SKIP_BATCH": "Discard current anomalous batch and proceed with training.",
            "GRADIENT_CLIPPING": "Implement global norm clipping at 1.0.",
            "OPTIMIZE_CHECKPOINTING": "Enable gradient checkpointing to save memory."
        }
        return detail_map.get(action, "Stabilize training.")

intervention_engine = InterventionEngine()
