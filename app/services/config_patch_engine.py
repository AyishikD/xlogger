from typing import List, Dict, Any, Optional
from app.models.enums import EventType

class ConfigPatchEngine:
    async def generate_patch(
        self, 
        failure_type: str, 
        current_config: Dict[str, Any],
        historical_successes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a structured config patch to resolve a training failure.
        """
        patch = {}
        
        # 1. Failure-Specific Heuristics
        if failure_type == "CUDA_OOM":
            current_bs = current_config.get("batch_size", 32)
            patch["batch_size"] = max(1, current_bs // 2)
            patch["gradient_accumulation_steps"] = current_config.get("gradient_accumulation_steps", 1) * 2

        if failure_type == "NAN_DETECTED":
            current_lr = current_config.get("learning_rate", 1e-4)
            patch["learning_rate"] = current_lr * 0.1
            patch["max_grad_norm"] = 1.0

        # 2. Historical Success Reinforcement
        # If we have similar historical failures where a specific patch worked, prioritize it
        for success in historical_successes:
            if "patch" in success:
                patch.update(success["patch"])
                
        return patch

config_patch_engine = ConfigPatchEngine()
