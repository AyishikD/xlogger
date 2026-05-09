import time
import random
from modellogger import ModelLogger

def run_stable_training():
    logger = ModelLogger()
    
    # Start experiment
    exp_id = logger.start_experiment(
        name="Stable GPT-Tiny Training",
        description="Baseline training run on tiny-shakespeare",
        metadata={
            "model": "gpt-tiny",
            "batch_size": 32,
            "learning_rate": 3e-4,
            "precision": "fp32",
            "optimizer": "adamw"
        }
    )
    
    print(f"Started stable training: {exp_id}")
    
    logger.log_event("TRAINING_STARTED", "Starting training on baseline config.")
    
    # Simulate training loop
    for step in range(100):
        # Metrics improve over time
        loss = 5.0 * (0.95 ** (step / 10)) + random.uniform(-0.05, 0.05)
        accuracy = min(0.99, 0.2 + (0.7 * (1 - 0.95 ** (step / 10))))
        
        logger.log_metric("loss", loss)
        logger.log_metric("accuracy", accuracy)
        
        if step % 25 == 0:
            logger.log_event("CHECKPOINT_SAVED", f"Saved checkpoint at step {step}", metadata={"step": step})
            
        time.sleep(0.1)
    
    logger.end_experiment()
    print("Stable training completed.")

if __name__ == "__main__":
    run_stable_training()
