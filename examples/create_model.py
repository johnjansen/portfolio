# examples/create_model.py
import torch
import torch.nn as nn
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(2, 1)

    def forward(self, x):
        return self.linear(x)

def create_and_save_model():
    # Get absolute path to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(project_root, 'models')

    # Create models directory if it doesn't exist
    os.makedirs(models_dir, exist_ok=True)

    # Create and initialize the model
    model = SimpleModel()

    # Convert to TorchScript
    example_input = torch.randn(2)
    traced_model = torch.jit.trace(model, example_input)

    # Save the model
    model_path = os.path.join(models_dir, 'simple_model.pt')
    torch.jit.save(traced_model, model_path)
    logger.info(f"Model saved to {model_path}")

    # Test loading
    loaded_model = torch.jit.load(model_path)
    test_input = torch.tensor([1.0, 2.0])
    with torch.no_grad():
        output = loaded_model(test_input)
    logger.info(f"Test prediction with input {test_input}: {output.item()}")

if __name__ == "__main__":
    create_and_save_model()
