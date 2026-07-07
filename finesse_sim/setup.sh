#!/bin/bash
# Finesse3 Optics Simulator — macOS / Linux Setup
# Run once to create the conda environment and install dependencies.
# Usage: bash setup.sh

set -e

echo "========================================"
echo " Finesse3 Optics Simulator — Setup"
echo "========================================"
echo ""

# Check conda
if ! command -v conda &> /dev/null; then
    echo "ERROR: conda not found. Install Miniconda first:"
    echo "  https://docs.conda.io/en/latest/miniconda.html"
    echo ""
    echo "  curl -L https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh -o ~/miniconda.sh"
    echo "  bash ~/miniconda.sh -b -p $HOME/miniconda3"
    exit 1
fi

# Create environment
echo "Creating conda environment: finesse_sim ..."
conda create -n finesse_sim python=3.12 -y

# Install dependencies
echo ""
echo "Installing dependencies ..."
conda install -y -n finesse_sim -c conda-forge finesse numpy scipy networkx flask || {
    echo ""
    echo "WARNING: Some packages may not have installed correctly."
    echo "Try manually:"
    echo "  conda activate finesse_sim"
    echo "  conda install -c conda-forge finesse numpy scipy networkx flask"
}

echo ""
echo "========================================"
echo " Setup complete!"
echo ""
echo " To launch:"
echo "   bash run.sh"
echo ""
echo " Or manually:"
echo "   conda activate finesse_sim"
echo "   python launcher.py"
echo "========================================"
