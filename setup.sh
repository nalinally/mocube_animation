#!/bin/bash

set -e

VENV_NAME="venv_mcb_ani"

echo "Installing python venv package..."
sudo apt update
sudo apt install -y python3-venv

echo "Creating virtual environment..."
python3 -m venv "${VENV_NAME}"

echo "Activating virtual environment..."
source "${VENV_NAME}/bin/activate"

echo "Installing uv..."
pip install --upgrade pip
pip install uv

echo "Installing requirements..."
uv pip install -r requirements.txt

echo ""
echo "Setup completed."
echo "To activate the environment later:"
echo "source activate_venv.sh"