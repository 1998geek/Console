#!/bin/bash

# 🚀 AIPortal Development Startup Script

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 Starting AIPortal Development Environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if in Dev Container
if [ ! -f /.dockerenv ] && [ ! -f /run/.containerenv ]; then
    echo "⚠️  Warning: Not running in Dev Container"
    echo "   Consider reopening in container for best experience"
    echo ""
fi

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "🐍 Python version: $PYTHON_VERSION"

# Install dependencies if needed
if [ ! -f ".dependencies_installed" ]; then
    echo ""
    echo "📦 Installing FastAPI dependencies..."
    pip install -r requirements_api.txt -q
    touch .dependencies_installed
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔥 Starting FastAPI Server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 API will be available at:"
echo "   • http://localhost:8000"
echo "   • http://localhost:8000/docs (Swagger UI)"
echo "   • http://localhost:8000/redoc (ReDoc)"
echo ""
echo "🔐 Test credentials:"
echo "   • Admin: admin / admin123"
echo "   • User:  user / user123"
echo ""
echo "💡 Tip: Press Ctrl+C to stop the server"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start FastAPI with auto-reload
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
