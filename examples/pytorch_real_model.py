import torch
import torch.nn as nn
import torch.optim as optim
from modellogger import ModelLogger
import time

# 1. Define a standard PyTorch model
class ResearchModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(10, 100),
            nn.ReLU(),
            nn.Linear(100, 1)
        )
    
    def forward(self, x):
        return self.net(x)

def train_real_model():
    # 2. Initialize ModelLogger
    logger = ModelLogger()
    logger.start_experiment(
        name="PyTorch Auto-Hook Test",
        description="Testing automated anomaly detection via PyTorch hooks",
        metadata={"learning_rate": 0.1, "batch_size": 32}
    )

    # 3. Create Model and ATTACH ModelLogger
    # This automatically monitors gradients and weights!
    model = ResearchModel()
    ModelLogger.attach(model, logger)
    
    optimizer = optim.SGD(model.parameters(), lr=0.1)
    criterion = nn.MSELoss()

    print("Starting real-world training loop...")
    
    for epoch in range(20):
        # Generate dummy data
        inputs = torch.randn(32, 10)
        targets = torch.randn(32, 1)

        # Forward pass
        outputs = model(inputs)
        loss = criterion(outputs, targets)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        
        # 4. Manual logging for metrics you want to chart
        logger.log_metric("loss", loss.item())
        
        # Simulate a sudden explosion to test the hook
        if epoch == 15:
            print("!!! Simulating gradient explosion !!!")
            with torch.no_grad():
                for p in model.parameters():
                    p.grad *= 1000.0

        optimizer.step()
        
        print(f"Epoch {epoch} | Loss: {loss.item():.4f}")
        time.sleep(0.5)

    logger.end_experiment()
    print("Training complete. Check your dashboard for auto-detected anomalies!")

if __name__ == "__main__":
    train_real_model()
