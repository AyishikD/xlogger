from transformers import TrainerCallback, TrainerState, TrainerControl
from typing import Dict, Any, Optional

class ModelLoggerCallback(TrainerCallback):
    def __init__(self, logger_instance=None):
        from modellogger import ModelLogger
        self.logger = logger_instance or ModelLogger()

    def on_train_begin(self, args, state, control, **kwargs):
        if not self.logger.experiment_id:
            self.logger.start_experiment(
                name=args.run_name or "HF_Experiment",
                metadata=args.to_dict()
            )
        self.logger.log_event("TRAINING_STARTED", "HuggingFace training session started.")

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs:
            self.logger.client._loop.run_until_complete(
                self.logger.client.log_metrics(self.logger.experiment_id, logs)
            )

    def on_save(self, args, state, control, **kwargs):
        self.logger.log_event(
            "CHECKPOINT_SAVED", 
            f"Checkpoint saved at step {state.global_step}",
            metadata={"global_step": state.global_step}
        )

    def on_train_end(self, args, state, control, **kwargs):
        self.logger.log_event("TRAINING_STOPPED", "HuggingFace training session completed.")
        self.logger.end_experiment()
