# src/catwalk/api/v1/docs.py
"""
API Documentation using OpenAPI specs
"""

model_predict_desc = """
Perform inference using the specified model.

The endpoint accepts model inputs in a standardized format and returns
predictions along with metadata about the inference process.

Parameters:
- model_id: Unique identifier for the model
- inputs: Dictionary of model inputs
- parameters: Optional inference parameters
"""
