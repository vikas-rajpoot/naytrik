#!/bin/bash
# Installation script for Gemini Workflow Automation

set -e

echo "🚀 Installing Gemini Workflow Automation..."
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.10 or higher is required (found $python_version)"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install package in development mode
echo "📥 Installing package..."
pip install -e ".[dev]"

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env and add your GEMINI_API_KEY"
fi

# Create workflows directory
mkdir -p workflows/examples

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Set your API key in .env file"
echo "  3. Run an example: python examples/basic_recording.py"
echo ""
echo "Or use the CLI:"
echo "  gemini-workflow --help"
echo ""
