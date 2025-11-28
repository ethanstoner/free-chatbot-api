@echo off
REM This script starts the short response Discord bot

echo Starting Short Response Discord Bot...
echo.

REM Check if bot is already running and stop it first
echo Checking for existing bot processes...
wsl.exe bash -c "pkill -f 'python.*discord_bot_short.py' 2>/dev/null; sleep 1"

REM Use WSL to run the Discord bot
wsl.exe bash -c "cd '/home/ethan/cursor projects/free-chatbot-api' && source venv/bin/activate && python discord_bot_short.py"

echo.
echo Discord Bot closed.
pause
