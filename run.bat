@echo off
title Edura — Unified School Management System
echo Launching Edura — Unified School Management System...
python main.py
if errorlevel 1 (
    echo.
    echo Application exited with an error or Python was not found in PATH.
    echo Trying explicit Python path...
    C:\Python314\python.exe main.py
)
pause
