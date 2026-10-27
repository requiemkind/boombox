@echo off

if not exist ".venv" python -m venv .venv

echo Downloading Boombox dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo Initializing...
".venv\Scripts\python.exe" main.py

pause