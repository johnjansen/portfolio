#!/bin/bash

# setup_catwalk.sh
# Creates the initial directory structure and stub files for the Catwalk project

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🚀 Setting up Catwalk project structure..."

# Create main project directory
mkdir -p catwalk/{src,tests,config,docs,scripts}

# Create source code structure
mkdir -p catwalk/src/catwalk/{api,core,models,storage,utils}
mkdir -p catwalk/src/catwalk/api/{v1,middleware}
mkdir -p catwalk/src/catwalk/core/{cache,manager}

# Create test directory structure
mkdir -p catwalk/tests/{unit,integration,performance}

# Create config directory
mkdir -p catwalk/config/{development,production}

# Create basic Python files
touch catwalk/src/catwalk/__init__.py
touch catwalk/src/catwalk/api/__init__.py
touch catwalk/src/catwalk/core/__init__.py
touch catwalk/src/catwalk/models/__init__.py
touch catwalk/src/catwalk/storage/__init__.py
touch catwalk/src/catwalk/utils/__init__.py

# Create main application files
cat > catwalk/src/catwalk/main.py << EOF
"""
Catwalk - LRU-based Machine Learning Model Server
Main application entry point
"""
from fastapi import FastAPI
from catwalk.api.v1 import router as api_router

app = FastAPI(title="Catwalk", description="LRU-based ML Model Server")

app.include_router(api_router, prefix="/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Create basic configuration files
cat > catwalk/config/development/config.yaml << EOF
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
cat > catwalk/requirements.txt << EOF
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
cat > catwalk/README.md << EOF
# Catwalk

LRU-based Machine Learning Model Server

## Installation

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Usage

\`\`\`bash
python -m catwalk.main
\`\`\`

## Development

\`\`\`bash
pytest tests/
\`\`\`
EOF

# Create basic gitignore
cat > catwalk/.gitignore << EOF
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
chmod +x catwalk/scripts/*.sh

echo -e "${GREEN}✅ Catwalk project structure created successfully!${NC}"
echo -e "Next steps:"
echo -e "1. cd catwalk"
echo -e "2. python -m venv venv"
echo -e "3. source venv/bin/activate"
echo -e "4. pip install -r requirements.txt"
echo -e "5. python src/catwalk/main.py"
