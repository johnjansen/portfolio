# Portfolio

⚠️ **Prototype Implementation Notice**: This is a proof-of-concept implementation of an LRU-based model server intended for learning and experimentation. While it demonstrates key concepts like model caching and memory management, it is not designed or tested for production use cases. Use at your own risk.

Portfolio is an experimental ML model serving system that demonstrates caching and memory management patterns using a Least Recently Used (LRU) eviction strategy.

## Key Features

- LRU-based model caching with configurable memory limits
- Support for PyTorch and TensorFlow models
- RESTful API with FastAPI
- Configurable model loading/unloading
- Basic metrics and monitoring
- Memory usage tracking

## Installation

### Prerequisites
- Python 3.9+
- pip
- virtualenv (recommended)

### Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Usage

### Starting the Server
```bash
# Configure environment
export PORTFOLIO_ENV=development
export PORTFOLIO_CONFIG_PATH=config/development/config.yaml

# Run server
python -m portfolio.main
```

### Using the CLI Tools
```bash
# Create example model
python examples/create_model.py

# Test inference
python examples/test_inference.py

# Check system status
python examples/test_system_status.py
```

## Development

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

### Code Quality
```bash
# Format code
make format

# Run linters
make lint

# Run all checks
make check
```

### Documentation
API documentation is available at `http://localhost:8000/docs` when running the server.

For detailed implementation documentation, see the `docs/` directory.

## Configuration

See `config/development/config.yaml` for available configuration options:

```yaml
models:
  model_name:
    path: "models/model.pt"
    type: "pytorch"
    memory_estimate: "1GB"
    preload: true

cache:
  max_memory: "8GB"
  soft_limit: "6GB"
  ttl: 3600
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT
