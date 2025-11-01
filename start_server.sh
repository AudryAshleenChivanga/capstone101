#!/bin/bash
# Production startup script for Render.com (Linux)

echo "========================================"
echo "  H. pylori CDSS - Starting Server"
echo "========================================"
echo ""

# Use PORT environment variable from Render, default to 8000 for local
PORT=${PORT:-8000}

echo "Starting FastAPI server on port $PORT..."
echo "Environment: Production"
echo ""

# Start server with production settings
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2

