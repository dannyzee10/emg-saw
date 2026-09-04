@echo off
REM One-click Michael — opens the EMG lab assistant chat window.
cd /d "%~dp0"
if exist venv\Scripts\python.exe (
  venv\Scripts\python.exe michael\michael_chat.py
) else (
  python michael\michael_chat.py
)
if errorlevel 1 pause
