@echo off
REM This script runs the chatbot through WSL since the project is in WSL

echo Starting chatbot...
echo.

REM Use WSL to run the Python script
wsl.exe bash -c "cd '/home/ethan/cursor projects/free-chatbot-api' && source venv/bin/activate && python chat.py"

echo.
echo Chatbot closed.
pause
