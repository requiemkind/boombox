@echo off
echo Downloading Boombox dependencies...
python -m pip install -r requirements.txt
echo.
echo Initializing...
python main.py
pause