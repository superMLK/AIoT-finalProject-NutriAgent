#!/usr/bin/env bash
# NutriAgent - Environment Setup Script for macOS / Linux
set -e

echo "==================================================="
echo " NutriAgent - Setup Environment Script"
echo "==================================================="
echo ""

echo "[1/3] Checking Python installation..."
python3 --version || { echo "[ERROR] Python 3 not found!"; exit 1; }

echo ""
echo "[2/3] Setting up virtual environment (.venv)..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Virtual environment created."
else
    echo "Virtual environment (.venv) already exists."
fi

echo ""
echo "[3/3] Installing dependencies from requirements.txt..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "==================================================="
echo " Setup Complete!"
echo " You can now execute:"
echo "   ./run_demo.sh  -> Run CLI demonstration"
echo "   ./run_web.sh   -> Start Web Cockpit"
echo "   ./run_test.sh  -> Run unit test suite"
echo "==================================================="
