#!/bin/bash
# One-click Michael for macOS — double-click to open the EMG lab assistant chat window.
# First time only, make it double-clickable:  chmod +x Michael.command
cd "$(dirname "$0")"
if [ -d venv ]; then source venv/bin/activate; fi
python3 michael/michael_chat.py
