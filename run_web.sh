#!/usr/bin/env bash
# NutriAgent - Run Web Cockpit for macOS / Linux
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi
echo "Starting NutriAgent Web Cockpit at http://127.0.0.1:5000 ..."
python3 app.py
