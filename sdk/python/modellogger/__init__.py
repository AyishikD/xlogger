from .client import ModelLoggerClient
import asyncio
from typing import Dict, Any, Optional
import logging

class ModelLogger:
    def __init__(self, base_url: str = "http://127.0.0.1:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.client = ModelLoggerClient(self.base_url, api_key)
        self.experiment_id: Optional[str] = None
        self._intervention_callback = None
        try:
            self._loop = asyncio.get_event_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

    async def start_experiment(self, name: str, description: str = "", metadata: Dict[str, Any] = {}):
        """Async experiment creation and command listener start"""
        self.experiment_id = await self.client.create_experiment(name, description, metadata)
        
        # Start background listener for remote interventions
        asyncio.create_task(self.client.listen_for_commands(self.experiment_id, self._handle_command))
        
        return self.experiment_id

    async def _handle_command(self, command: Dict[str, Any]):
        """Internal dispatcher for remote commands"""
        action = command.get("action")
        payload = command.get("payload", {})
        
        if self._intervention_callback:
            await self._intervention_callback(action, payload)

    def set_intervention_callback(self, callback):
        """Register a callback for human-in-the-loop interventions"""
        self._intervention_callback = callback

    async def log_metric(self, name: str, value: float):
        if not self.experiment_id:
            return
        await self.client.log_metrics(self.experiment_id, {name: value})

    async def log_event(self, event_type: str, summary: str, severity: str = "INFO", metadata: Dict[str, Any] = {}):
        if not self.experiment_id:
            return
        await self.client.log_event(self.experiment_id, event_type, summary, severity, metadata)

    async def log_intervention_outcome(self, action: str, was_successful: bool, metrics_delta: Dict[str, Any] = {}):
        if not self.experiment_id:
            return
        await self.client.log_recommendation_outcome(self.experiment_id, action, was_successful, metrics_delta)

    def end_experiment_sync(self):
        # Fallback for sync cleanup
        if self.experiment_id:
            self._loop.run_until_complete(self.log_event("TRAINING_STOPPED", "Experiment concluded."))
            self.experiment_id = None

    async def end_experiment(self):
        await self.log_event("TRAINING_STOPPED", "Experiment concluded.")
        self.experiment_id = None

    @classmethod
    def attach(cls, model, logger_instance=None):
        """Attach PyTorch hooks to a model"""
        from .integrations.pytorch import attach_hooks
        # For now, hooks remain sync but they can spawn async tasks
        return attach_hooks(model, logger_instance or cls())

    # Sync compatibility wrappers (original behavior)
    def start_experiment_sync(self, name: str, description: str = "", metadata: Dict[str, Any] = {}):
        return self._loop.run_until_complete(self.start_experiment(name, description, metadata))

    def log_event_sync(self, event_type: str, summary: str, severity: str = "INFO", metadata: Dict[str, Any] = {}):
        self._loop.run_until_complete(self.log_event(event_type, summary, severity, metadata))
