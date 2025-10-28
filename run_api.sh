#!/bin/bash

# Bash script to run H. pylori CDSS API

echo "🏥 H. pylori CDSS - Starting API Server"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip --quiet

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration!"
fi

# Check for models directory
if [ ! -d "models" ]; then
    echo "⚠️  Warning: models directory not found. Creating..."
    mkdir models
    echo "Please place your model files in the models/ directory!"
    echo ""
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Starting FastAPI server..."
echo "API will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo "Frontend UI at: http://localhost:8000/ui/index.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
