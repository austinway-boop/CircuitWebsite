#!/bin/bash
# Setup script for LinkedIn Profile Search Application

set -e  # Exit on error

echo "======================================"
echo "LinkedIn Profile Search - Setup"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || {
    echo "Error: Python 3 is required but not installed."
    exit 1
}

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

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p logs
mkdir -p docs

# Check if .env exists
echo ""
if [ -f ".env" ]; then
    echo "✓ .env file exists"
else
    echo "⚠️  .env file not found"
    echo "Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Please edit .env and add your LinkedIn API credentials:"
    echo "  - LINKEDIN_CLIENT_ID"
    echo "  - LINKEDIN_CLIENT_SECRET"
    echo ""
fi

# Make main.py executable
chmod +x main.py

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your LinkedIn credentials"
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo "3. Run the application:"
echo "   python main.py info"
echo ""
echo "For more information, see README.md"
echo ""

