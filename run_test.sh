#!/usr/bin/env bash
# NutriAgent - Run Tests for macOS / Linux
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi
python3 -m unittest tests/test_agent.py
