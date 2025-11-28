#!/bin/bash
# Setup script for Linux/WSL

cd "$(dirname "$0")/.."

echo "Setting up virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete! Activate the venv with: source venv/bin/activate"
