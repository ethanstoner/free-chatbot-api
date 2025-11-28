@echo off
REM This script starts the Discord bot in the background through WSL

echo Starting Discord Bot in background...
echo.

REM Check if bot is already running and stop it first
echo Checking for existing bot processes...
wsl.exe bash -c "pkill -f 'python.*discord_bot.py' 2>/dev/null; sleep 1"

REM Use WSL to run the Discord bot in background
wsl.exe bash -c "cd '/home/ethan/cursor projects/free-chatbot-api' && source venv/bin/activate && nohup python discord_bot.py >> discord_bot.log 2>&1 &"

echo.
echo Discord Bot started in background!
echo Log file: discord_bot.log
echo.
echo To view logs, run: wsl.exe bash -c "cd '/home/ethan/cursor projects/free-chatbot-api' && tail -f discord_bot.log"
echo To stop the bot, run: stop_discord_bot.bat
echo.
pause
