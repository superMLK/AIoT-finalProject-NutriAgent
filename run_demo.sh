#!/usr/bin/env bash
# NutriAgent - Run CLI Demo for macOS / Linux
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi
python3 demo_run.py
