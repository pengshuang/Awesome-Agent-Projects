#!/bin/bash

# Data Synthesis System Startup Script

echo "🚀 Starting Data Synthesis System..."
echo "=================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "❗ Please edit .env file and configure your API keys before running."
    exit 1
fi

# Initialize system
echo "🔧 Initializing system..."
python init_system.py

# Check if initialization succeeded
if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✅ System initialized successfully"
    echo "=================================="
    echo ""
    echo "🌐 Starting Gradio Web UI..."
    echo "📍 Access the UI at: http://localhost:7860"
    echo ""
    python web_ui.py
else
    echo ""
    echo "❌ System initialization failed"
    echo "Please check the error messages above and fix the issues."
    exit 1
fi
