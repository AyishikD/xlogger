import litellm
from typing import List, Dict, Any, Optional
import os
from app.core.config import settings

class LLMService:
    def __init__(self):
        # LiteLLM allows us to swap Llama-3 (Groq), Mistral (MistralAI), or OpenAI easily
        self.model = os.getenv("LLM_MODEL", "groq/llama3-70b-8192")
        self.api_key = os.getenv("GROQ_API_KEY")

    async def synthesize_learning(self, event_type: str, logs: List[str]) -> Dict[str, Any]:
        """
        Use Llama-3/Mistral to synthesize a research learning from raw logs.
        """
        if not self.api_key:
            # Fallback to local heuristic if no key provided
            return self._heuristic_fallback(event_type, logs)

        prompt = f"""
        Analyze these ML training logs for the failure type: {event_type}.
        Logs:
        {chr(10).join(logs[:5])}
        
        Provide:
        1. A concise Root Cause Analysis (RCA).
        2. 3 Actionable steps to fix this.
        3. A confidence score (0.0 to 1.0).
        
        Format as JSON:
        {{
            "content": "RCA text",
            "recommendations": ["step 1", "step 2", "step 3"],
            "confidence": 0.85
        }}
        """

        try:
            response = await litellm.acompletion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._heuristic_fallback(event_type, logs)

    def _heuristic_fallback(self, event_type: str, logs: List[str]) -> Dict[str, Any]:
        # Our existing "Expert Logic" as a safety net
        fallbacks = {
            "LOSS_DIVERGED": {
                "content": "Potential mismatch between learning rate and batch size detected via heuristic analysis.",
                "recommendations": ["Reduce learning rate by 0.1x", "Enable gradient clipping at 1.0", "Check data shuffle"],
                "confidence": 0.6
            }
        }
        return fallbacks.get(event_type, {
            "content": f"Automated analysis of {event_type} events.",
            "recommendations": ["Audit training logs", "Check hardware health"],
            "confidence": 0.4
        })

llm_service = LLMService()
