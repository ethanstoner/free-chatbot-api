@echo off
REM Start Donald Trump Discord Bot

cd /d "%~dp0"

echo ==================================================
echo Starting Donald Trump Discord Bot...
echo ==================================================

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
)

REM Run the bot
python donald_trump_bot.py

pause
