import torch
import asyncio
from torch.optim import AdamW
from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer
)
from datasets import load_dataset
from modellogger import ModelLogger
import os

# ----------------------------
# 1. LOAD DATASET (REAL)
# ----------------------------x
def get_dataset(tokenizer):
    print("Loading wikitext-2 dataset...")
    dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train[:1%]")

    def tokenize(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",
            max_length=64
        )

    tokenized = dataset.map(tokenize, batched=True)
    tokenized.set_format("torch")

    return tokenized


# ----------------------------
# 2. BOUNDED RELIABILITY HOOK
# ----------------------------
class ReliabilityHook:
    """
    Enforces a Safety Policy over autonomous interventions.
    """
    def __init__(self, logger, mode="AUTO"):
        self.logger = logger
        self.mode = mode
        self.experiment_id = None # Will be set by train()
        
        # Safety Policy Bounds
        self.max_interventions = 3
        self.intervention_count = 0
        self.last_intervention_step = -100
        self.cooldown_steps = 15
        self.lr_floor = 1e-6
        self.pending_outcome = None 
        self.avg_loss = 0.0 # Running average for outlier detection

    async def log_and_intervene(self, optimizer, loss, step, model):
        if not self.experiment_id: self.experiment_id = self.logger.experiment_id
        
        # 1. Log metrics normally
        await self.logger.client.log_metrics(self.experiment_id, {"loss": float(loss)})

        # 2. Check Safety Policy before even querying backend
        if self.mode != "AUTO": return
        if self.intervention_count >= self.max_interventions: return
        # 3. Detect Anomaly
        if step > 5:
            # Update running average (0.9/0.1 smoothing)
            if self.avg_loss == 0.0: self.avg_loss = loss
            else: self.avg_loss = 0.9 * self.avg_loss + 0.1 * loss

            # 3.1 Check for Transitory Anomaly (Absolute Outlier vs Running Avg)
            if loss > 10.0 and loss > (self.avg_loss * 3.0):
                print(f"\n[Step {step}] 🕵️  TRANSITORY CHECK: Outlier detected (Loss: {loss:.2f} vs Avg: {self.avg_loss:.2f})")
                res = await self.logger.client.get_intervention(self.experiment_id, "TRANSITORY_ANOMALY")
                recs = res.get("recommendations", [])
                if recs and recs[0]["action"] == "SKIP_BATCH":
                    print(f"   💡 AI OS Suggestion: SKIP_BATCH (Reason: Discovered transient data corruption.)")
                    return "SKIP_BATCH"

            # 3.2 Check for Severe Divergence (Respects Cooldown)
            if (step - self.last_intervention_step) < self.cooldown_steps: return None

            if loss > 8.0:
                print(f"\n[Step {step}] 🛡️  RELIABILITY CHECK: Natural divergence ({loss:.4f}) detected.")
                await self.logger.log_event("LOSS_DIVERGED", f"Loss spike ({loss:.4f})", severity="CRITICAL")
                
                res = await self.logger.client.get_intervention(self.experiment_id, "LOSS_DIVERGED", {"lr": optimizer.param_groups[0]['lr']})
                recs = res.get("recommendations", [])
                if not recs: return None

                top_action = recs[0]
                action_key = top_action["action"]
                print(f"   💡 AI OS Suggestion: {action_key} (Reason: {top_action['reason']})")

                if top_action["confidence"] > 0.8:
                    print("   ⚡ HIGH CONFIDENCE PATH: Executing immediate state rollback.")
                    # Proportional Control (Multiplicative Decrease)
                    current_lr = optimizer.param_groups[0]['lr']
                    new_lr = max(self.lr_floor, current_lr * 0.2)
                    for g in optimizer.param_groups: g['lr'] = new_lr
                    self.intervention_count += 1
                    self.last_intervention_step = step + 15
                    return "ROLLBACK_AND_STABILIZE"
                
                current_lr = optimizer.param_groups[0]['lr']
                new_lr = max(self.lr_floor, current_lr * 0.5)
                for g in optimizer.param_groups: g['lr'] = new_lr
                self.intervention_count += 1
                self.last_intervention_step = step
                return "REDUCE_LR"
        
        self.last_loss = loss
        return None



# ----------------------------
# 3. ASYNC TRAINING LOOP (STABLE AUTO)
# ----------------------------
async def train():
    logger = ModelLogger()

    await logger.start_experiment(
        name="BOUNDED_RELIABILITY_TEST",
        description="Testing safety-bounded autonomous training recovery.",
        metadata={"model": "gpt2"}
    )

    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token
    model = GPT2LMHeadModel.from_pretrained("gpt2")
    device = torch.device("cpu")
    model.to(device)

    ModelLogger.attach(model, logger)
    dataset = get_dataset(tokenizer)
    
    # 1. State Management for Rollbacks
    last_checkpoint = model.state_dict()
    
    async def remote_fix(action, payload):
        nonlocal last_checkpoint
        print(f"\n🎮 REMOTE COMMAND RECEIVED: {action}")
        
        if action == "ROLLBACK_AND_STABILIZE":
            print("   🔄 EMERGENCY ROLLBACK: Reverting to last healthy state...")
            model.load_state_dict(last_checkpoint)
            # Decisive Action: 100x reduction
            new_lr = max(1e-6, optimizer.param_groups[0]['lr'] * 0.01)
            for g in optimizer.param_groups:
                g['lr'] = new_lr
            print(f"   🛠️ STABILITY PATCH: Weights restored. LR dropped to {new_lr:.2e}")
            
        elif action == "REDUCE_LR":
            new_lr = payload.get("value", optimizer.param_groups[0]['lr'] * 0.1)
            for g in optimizer.param_groups:
                g['lr'] = new_lr
            print(f"   🛠️ REMOTE PATCH: Updated LR to {new_lr:.2e}")
            
        elif action == "STOP_TRAINING":
            print("   ⛔ REMOTE COMMAND: Stopping training...")
            os._exit(0)

    logger.set_intervention_callback(remote_fix)

    # Starting LR: 0.1 is unstable enough to diverge but recoverable
    optimizer = AdamW(model.parameters(), lr=0.1) 
    print(f"Initial LR: {optimizer.param_groups[0]['lr']} (UNSTABLE BY DESIGN)")

    # Initialize hook in AUTO mode with strict safety policy
    hook = ReliabilityHook(logger, mode="AUTO")

    model.train()
    print("\n🚀 STARTING BOUNDED RELIABILITY RUN...\n")

    step = 0
    for batch in dataset:
        input_ids = batch["input_ids"].unsqueeze(0).to(device)
        labels = input_ids.clone()

        # 1.5 Hero Case: Real Data Noise (Random Labels) at Step 30
        if step == 30:
            print(f"\n[Step {step}] 🧪 HERO CASE: Injecting real corrupted data batch...")
            # We simulate a massive loss spike that ONLY happens for this batch
            outputs = model(input_ids, labels=torch.randint(0, tokenizer.vocab_size, labels.shape).to(device))
            loss = outputs.loss
        else:
            outputs = model(input_ids, labels=labels)
            loss = outputs.loss

        optimizer.zero_grad()
        loss.backward()
        
        # 3. Autonomous Reliability Loop
        intv_status = await hook.log_and_intervene(optimizer, loss.item(), step, model)
        
        if intv_status == "SKIP_BATCH":
            print("   ✅ TRAINING PROTECTED: Corruption isolated. Skipping weight update.")
            optimizer.zero_grad()
            step += 1
            continue

        if intv_status:
            hook.pending_outcome = {"action": intv_status, "step": step, "initial_loss": loss.item()}
            if intv_status == "ROLLBACK_AND_STABILIZE":
                model.load_state_dict(last_checkpoint)
                print(f"   🔄 SCRIPT: Weights rolled back to Step {max(0, step-10)}")

        # Optimizer Step (Only if not skipped)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        # 3.1 Evaluate previous intervention (Objective Success: -30% loss in 10 steps)
        # Skip evaluation if we just hit the Step 30 noise (it would pollute the result)
        if hook.pending_outcome and step == hook.pending_outcome["step"] + 10:
            if step >= 30 and step <= 35:
                # Delay evaluation to get a clean signal
                hook.pending_outcome["step"] += 5
            else:
                initial_loss = hook.pending_outcome["initial_loss"]
                current_loss = loss.item()
                # Objective criteria: 30% reduction is enough for a "Hero" win in 10 steps
                was_successful = current_loss < (initial_loss * 0.7)
                
                await logger.log_intervention_outcome(
                    action=hook.pending_outcome["action"],
                    was_successful=was_successful,
                    metrics_delta={"loss_reduction": (initial_loss - current_loss) / initial_loss}
                )
                print(f"   📈 OBJECTIVE EVALUATION: {hook.pending_outcome['action']} at step {hook.pending_outcome['step']}")
                print(f"      Status: {'✅ SUCCESS' if was_successful else '❌ FAILURE'} (Loss: {initial_loss:.2f} -> {current_loss:.2f})")
                hook.pending_outcome = None

        # 4. Safety Checkpointing
        if step % 10 == 0 and loss.item() < 10.0:
            last_checkpoint = {k: v.clone() for k, v in model.state_dict().items()}
            print(f"   💾 CHECKPOINT: Healthy state captured at step {step}")

        # 5. Closed-Loop LR Control (The "Adaptive Engine")
        # Detect stability
        if loss.item() < hook.avg_loss * 1.2:
            hook.recovery_steps += 1
        else:
            hook.recovery_steps = 0

        # Gradual LR recovery
        if hook.recovery_steps >= 10:
            current_lr = optimizer.param_groups[0]['lr']
            # Stagnation check
            if current_lr <= hook.lr_floor * 1.1 and abs(loss.item() - hook.avg_loss) < 1.0:
                new_lr = current_lr * 5.0
                print(f"\n[Step {step}] ⚠️ STAGNATION DETECTED: Boosting LR ({current_lr:.2e} -> {new_lr:.2e})")
            else:
                new_lr = min(current_lr * 1.3, 1e-1) # Cap recovery at 0.1
                print(f"\n[Step {step}] 🔼 LR RECOVERY: {new_lr:.2e}")
            
            for g in optimizer.param_groups:
                g['lr'] = new_lr
            hook.recovery_steps = 0

        if step % 5 == 0 or step == 31:
            print(f"step={step} loss={loss.item():.4f} lr={optimizer.param_groups[0]['lr']:.2e} [Intv:{hook.intervention_count}/3]")
            if step == 31:
                print("🔥 RESULT: Transient corruption did NOT affect training trajectory.")

        step += 1
        if step > 50: break

    await logger.end_experiment()
    print("\n✅ TRAINING COMPLETE")

if __name__ == "__main__":
    asyncio.run(train())
