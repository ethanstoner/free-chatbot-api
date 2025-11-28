@echo off
REM This script sets up and runs the chatbot through WSL

echo Setting up chatbot...
echo.

REM Use WSL to set up venv and run
wsl.exe bash -c "cd '/home/ethan/cursor projects/free-chatbot-api' && if [ ! -d 'venv' ]; then python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python chat.py; else source venv/bin/activate && python chat.py; fi"

echo.
echo Chatbot closed.
pause
