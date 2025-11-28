#!/bin/bash
# Start Donald Trump Discord Bot

cd "$(dirname "$0")"

echo "=================================================="
echo "Starting Donald Trump Discord Bot..."
echo "=================================================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
fi

# Run the bot
python3 donald_trump_bot.py
