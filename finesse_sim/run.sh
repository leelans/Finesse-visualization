#!/bin/bash
# Finesse3 Optics Simulator — macOS / Linux Launcher
# Usage: bash run.sh

set -e
cd "$(dirname "$0")"

echo "Optics Simulator starting..."

# Auto-detect conda and activate finesse_sim env
if [ -z "$CONDA_PREFIX" ]; then
    # Try common conda locations
    if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
    elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/anaconda3/etc/profile.d/conda.sh"
    elif [ -f "/opt/miniconda3/etc/profile.d/conda.sh" ]; then
        source "/opt/miniconda3/etc/profile.d/conda.sh"
    elif [ -f "/usr/local/miniconda3/etc/profile.d/conda.sh" ]; then
        source "/usr/local/miniconda3/etc/profile.d/conda.sh"
    fi
    conda activate finesse_sim 2>/dev/null || {
        echo "ERROR: conda environment 'finesse_sim' not found."
        echo "Run 'bash setup.sh' first to create it."
        exit 1
    }
fi

# Auto-detect free port (start from 5000)
PORT=5000
while lsof -i :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
    PORT=$((PORT + 1))
    [ $PORT -gt 5100 ] && break
done
echo "Using port: $PORT"

echo ""
python launcher.py --port $PORT
echo "Server stopped."
