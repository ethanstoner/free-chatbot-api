@echo off
REM This script stops the Discord bot

echo Stopping Discord Bot...
echo.

REM Stop the bot process
wsl.exe bash -c "pkill -f 'python.*discord_bot.py' && echo 'Bot stopped successfully' || echo 'No bot process found'"

echo.
pause
