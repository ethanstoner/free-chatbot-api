@echo off
REM This script starts the second Discord bot

echo Starting Second Discord Bot (Alex)...
echo.

REM Check if bot is already running and stop it first
echo Checking for existing bot processes...
wsl.exe bash -c "pkill -f 'python.*discord_bot_2.py' 2>/dev/null; sleep 1"

REM Use WSL to run the Discord bot
wsl.exe bash -c "cd '/home/ethan/cursor projects/free-chatbot-api' && source venv/bin/activate && python discord_bot_2.py"

echo.
echo Discord Bot closed.
pause
