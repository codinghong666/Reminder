#!/bin/bash

# QQ Bot DDL Reminder Installation Script
# This script sets up the environment for the QQ Bot DDL Reminder project

echo "=== QQ Bot DDL Reminder Installation ==="
echo ""

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Error: Conda is not installed. Please install Anaconda or Miniconda first."
    echo "Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✓ Conda found"

# Create conda environment
echo "Creating conda environment 'qqbot'..."
conda env create -f environment.yml

if [ $? -eq 0 ]; then
    echo "✓ Environment created successfully"
else
    echo "Error: Failed to create conda environment"
    exit 1
fi

# Activate environment and install additional packages
echo "Activating environment and installing additional packages..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate qqbot

# Install additional packages via pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ All packages installed successfully"
else
    echo "Warning: Some packages may not have installed correctly"
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "To activate the environment, run:"
echo "  conda activate qqbot"
echo ""
echo "To start the bot, run:"
echo "  python main.py"
echo ""
echo "Make sure to configure your config.env file before running!"
