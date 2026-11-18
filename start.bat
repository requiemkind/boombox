@echo off

if not exist ".venv" (
    echo Creating virtual environment...
    py -m venv .venv
)

echo Downloading Boombox dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo Initializing...
".venv\Scripts\python.exe" src\main.py

pause
