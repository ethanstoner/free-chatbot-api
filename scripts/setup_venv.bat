@echo off
REM Setup script for Windows

cd /d "%~dp0\.."

echo Setting up virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Setup complete! Activate the venv with: venv\Scripts\activate

pause
