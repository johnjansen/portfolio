#!/bin/bash

# setup_portfolio.sh
# Creates the initial directory structure and stub files for the Portfolio project

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🚀 Setting up Portfolio project structure..."

# Create main project directory
mkdir -p portfolio/{src,tests,config,docs,scripts}

# Create source code structure
mkdir -p portfolio/src/portfolio/{api,core,models,storage,utils}
mkdir -p portfolio/src/portfolio/api/{v1,middleware}
mkdir -p portfolio/src/portfolio/core/{cache,manager}

# Create test directory structure
mkdir -p portfolio/tests/{unit,integration,performance}

# Create config directory
mkdir -p portfolio/config/{development,production}

# Create basic Python files
touch portfolio/src/portfolio/__init__.py
touch portfolio/src/portfolio/api/__init__.py
touch portfolio/src/portfolio/core/__init__.py
touch portfolio/src/portfolio/models/__init__.py
touch portfolio/src/portfolio/storage/__init__.py
touch portfolio/src/portfolio/utils/__init__.py

# Create main application files
cat > portfolio/src/portfolio/main.py << EOF
"""
Portfolio - LRU-based Machine Learning Model Server
Main application entry point
"""
from fastapi import FastAPI
from portfolio.api.v1 import router as api_router

app = FastAPI(title="Portfolio", description="LRU-based ML Model Server")

app.include_router(api_router, prefix="/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Create basic configuration files
cat > portfolio/config/development/config.yaml << EOF
models:
  model1:
    path: /models/model1
    type: pytorch
    memory_estimate: 2GB
    preload: true

cache:
  max_memory: 8GB
  soft_limit: 7GB
  ttl: 3600
EOF

# Create requirements file
cat > portfolio/requirements.txt << EOF
fastapi>=0.68.0
uvicorn>=0.15.0
pyyaml>=5.4.1
pydantic>=1.8.2
python-multipart>=0.0.5
aiofiles>=0.7.0
pytest>=6.2.5
pytest-asyncio>=0.15.1
httpx>=0.19.0
EOF

# Create README
cat > portfolio/README.md << EOF
# Portfolio

LRU-based Machine Learning Model Server

## Installation

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Usage

\`\`\`bash
python -m portfolio.main
\`\`\`

## Development

\`\`\`bash
pytest tests/
\`\`\`
EOF

# Create basic gitignore
cat > portfolio/.gitignore << EOF
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
.env
.venv
venv/
ENV/
.idea/
.vscode/
*.swp
.DS_Store
EOF

# Make the script executable
chmod +x portfolio/scripts/*.sh

echo -e "${GREEN}✅ Portfolio project structure created successfully!${NC}"
echo -e "Next steps:"
echo -e "1. cd portfolio"
echo -e "2. python -m venv venv"
echo -e "3. source venv/bin/activate"
echo -e "4. pip install -r requirements.txt"
echo -e "5. python src/portfolio/main.py"
