import time
import random
import math
from modellogger import ModelLogger

def run_failing_training():
    logger = ModelLogger()
    
    # Start experiment with aggressive LR
    exp_id = logger.start_experiment(
        name="Aggressive LR Experiment",
        description="Testing high learning rate for faster convergence",
        metadata={
            "model": "gpt-tiny",
            "batch_size": 32,
            "learning_rate": 5e-2, # Intentionally high
            "precision": "fp32"
        }
    )
    
    print(f"Started failing training: {exp_id}")
    
    logger.log_event("TRAINING_STARTED", "Starting training with high LR.")
    
    # Simulate training loop
    for step in range(50):
        if step < 20:
            loss = 4.0 - (step * 0.1) + random.uniform(-0.1, 0.1)
        else:
            # Loss starts to diverge
            loss = (step - 19) ** 2 + random.uniform(0, 1)
        
        logger.log_metric("loss", loss)
        
        if loss > 50 and step >= 25:
            logger.log_event("LOSS_DIVERGED", f"Loss spiked to {loss:.2f} at step {step}", severity="ERROR")
            # Trigger NaN soon
            if step > 30:
                logger.log_metric("loss", float('nan'))
                logger.log_event("NAN_DETECTED", "NaN detected in loss calculation.", severity="CRITICAL")
                break
            
        time.sleep(0.1)
    
    logger.end_experiment()
    print("Failing training stopped.")

if __name__ == "__main__":
    run_failing_training()
