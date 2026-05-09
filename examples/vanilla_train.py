import torch
from torch.optim import AdamW
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from datasets import load_dataset

def get_dataset(tokenizer):
    dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train[:1%]")
    def tokenize(examples):
        return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=64)
    tokenized = dataset.map(tokenize, batched=True)
    tokenized.set_format("torch")
    return tokenized

def train():
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token
    model = GPT2LMHeadModel.from_pretrained("gpt2")
    device = torch.device("cpu")
    model.to(device)
    
    dataset = get_dataset(tokenizer)
    # UNSTABLE CONFIG (Same as real_hf_train.py)
    optimizer = AdamW(model.parameters(), lr=0.5) 
    
    print("\n🚀 STARTING VANILLA TRAINING (UNPROTECTED)...\n")
    
    model.train()
    step = 0
    for batch in dataset:
        input_ids = batch["input_ids"].unsqueeze(0).to(device)
        labels = input_ids.clone()
        
        # HERO CASE: Real Data Noise at Step 30
        if step == 30:
            print(f"\n[Step {step}] 🧪 HERO CASE: Injecting real corrupted data batch...")
            labels = torch.randint(0, tokenizer.vocab_size, labels.shape).to(device)

        outputs = model(input_ids, labels=labels)
        loss = outputs.loss
        
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        
        if step % 5 == 0:
            print(f"step={step} loss={loss.item():.4f} lr={optimizer.param_groups[0]['lr']:.2e}")
        
        if loss.item() > 500.0 or torch.isnan(loss):
            print(f"\n❌ TRAINING CRASHED/DIVERGED at step {step} (Loss: {loss.item()})")
            break

        step += 1
        if step > 50: break

if __name__ == "__main__":
    train()
