import time
from modellogger import ModelLogger

def run_tokenizer_regression():
    logger = ModelLogger()
    
    exp_id = logger.start_experiment(
        name="Tokenizer Vocab Expansion",
        description="Expanding vocab size to include domain-specific tokens",
        metadata={
            "old_vocab_size": 50257,
            "new_vocab_size": 50304
        }
    )
    
    print(f"Started tokenizer regression test: {exp_id}")
    
    logger.log_event("TOKENIZER_CHANGED", "Resized tokenizer from 50257 to 50304.")
    
    # Simulate mismatch error in training loop
    time.sleep(1)
    
    log_text = "RuntimeError: weight of size [50257, 768] is not compatible with input [50304, 768]"
    logger.log_event("TOKENIZER_MISMATCH", log_text, severity="ERROR", metadata={"error": log_text})
    
    logger.end_experiment()

if __name__ == "__main__":
    run_tokenizer_regression()
