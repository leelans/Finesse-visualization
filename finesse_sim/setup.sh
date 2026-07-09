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

# --- Detect existing environment ---
ENV_EXISTS=0
if conda env list 2>/dev/null | grep -q "^finesse_sim "; then
    ENV_EXISTS=1
fi

if [ "$ENV_EXISTS" -eq 1 ]; then
    echo "Found existing environment: finesse_sim"
    echo "Checking required packages ..."
    MISSING=""
    for pkg in finesse numpy scipy networkx flask; do
        if ! conda list -n finesse_sim 2>/dev/null | grep -qi "^${pkg} "; then
            MISSING="$MISSING $pkg"
        fi
    done

    if [ -z "$MISSING" ]; then
        echo "All required packages are already installed."
        read -r -p "The environment is already set up. Reinstall anyway? [y/N]: " REINSTALL
        if [[ "$REINSTALL" =~ ^[Yy]$ ]]; then
            conda env remove -n finesse_sim -y
        else
            echo "Nothing to do - the environment is ready. You can run run.sh now."
            exit 0
        fi
    else
        echo "The environment exists but is missing:$MISSING"
        read -r -p "Reinstall the environment to fix it? [y/N]: " REINSTALL
        if [[ "$REINSTALL" =~ ^[Yy]$ ]]; then
            conda env remove -n finesse_sim -y
        else
            echo "Aborted. No changes made."
            exit 0
        fi
    fi
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
