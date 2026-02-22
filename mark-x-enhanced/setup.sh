#!/bin/bash

echo "=================================================="
echo "  Mark-X Enhanced - Setup Script"
echo "=================================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys!"
    echo ""
fi

# Create data directory
echo "Creating data directory..."
mkdir -p data

echo ""
echo "=================================================="
echo "  Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Download Vosk model (see README.md)"
echo "3. Activate virtual environment: source venv/bin/activate"
echo "4. Run the application: python main.py"
echo ""
echo "For detailed instructions, see README.md"
echo ""
