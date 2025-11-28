@echo off
REM This script shows the Discord bot logs

echo Viewing Discord Bot logs...
echo Press Ctrl+C to exit
echo.

REM Use WSL to tail the log file
wsl.exe bash -c "cd '/home/ethan/cursor projects/free-chatbot-api' && tail -f discord_bot.log"
