import time
import random
from modellogger import ModelLogger

def run_bf16_overflow():
    logger = ModelLogger()
    
    exp_id = logger.start_experiment(
        name="BF16 Precision Test",
        description="Training with bf16 mixed precision",
        metadata={
            "model": "gpt-tiny",
            "precision": "bf16",
            "gpu": "A100"
        }
    )
    
    print(f"Started BF16 training: {exp_id}")
    
    # Simulate gradual overflow
    for step in range(40):
        grad_norm = (step / 5) ** 2 + random.uniform(0, 5)
        logger.log_metric("grad_norm", grad_norm)
        
        if grad_norm > 20:
            logger.log_event("EXPLODING_GRADIENT", f"Gradient norm high: {grad_norm:.2f}", severity="WARNING")
        
        if step == 35:
            logger.log_event("NAN_DETECTED", "Bf16 overflow detected in optimizer state.", severity="CRITICAL")
            break
            
        time.sleep(0.1)
    
    logger.end_experiment()

if __name__ == "__main__":
    run_bf16_overflow()
