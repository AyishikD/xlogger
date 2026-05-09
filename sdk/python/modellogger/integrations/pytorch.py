import torch
import torch.nn as nn
import asyncio
from typing import Any, Optional

def attach_hooks(model: nn.Module, logger):
    """
    Attach forward and backward hooks to a PyTorch model to monitor gradients and activations.
    """
    
    def forward_hook(module, input, output):
        if torch.isnan(output).any():
            if hasattr(logger, 'log_event'):
                # Fire and forget async log
                asyncio.create_task(logger.log_event(
                    "NAN_DETECTED", 
                    f"NaN detected in forward pass of {module.__class__.__name__}",
                    severity="ERROR"
                ))

    def backward_hook(module, grad_input, grad_output):
        for i, grad in enumerate(grad_output):
            if grad is not None:
                if torch.isnan(grad).any():
                    asyncio.create_task(logger.log_event(
                        "NAN_DETECTED", 
                        f"NaN detected in gradient of {module.__class__.__name__}",
                        severity="ERROR"
                    ))
                if grad.norm() > 1000:
                    asyncio.create_task(logger.log_event(
                        "EXPLODING_GRADIENT", 
                        f"Exploding gradient in {module.__class__.__name__} (norm={grad.norm():.2f})",
                        severity="WARNING"
                    ))

    for name, module in model.named_modules():
        if len(list(module.children())) == 0:
            module.register_forward_hook(forward_hook)
            module.register_full_backward_hook(backward_hook)
            
    return model
