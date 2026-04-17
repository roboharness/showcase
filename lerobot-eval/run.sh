#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ------------------------------------------------------------------
# Ensure a virtual environment exists
# ------------------------------------------------------------------
if [ ! -d ".venv" ]; then
    if command -v uv &> /dev/null; then
        echo "Creating virtual environment with uv ..."
        uv venv
    else
        echo "Creating virtual environment with python -m venv ..."
        python3 -m venv .venv
    fi
fi

source .venv/bin/activate

# ------------------------------------------------------------------
# Local dev mode: install roboharness from source if ROBOHARNESS_SRC is set
# ------------------------------------------------------------------
if [ -n "${ROBOHARNESS_SRC:-}" ]; then
    if [ ! -f "$ROBOHARNESS_SRC/pyproject.toml" ]; then
        echo "ERROR: ROBOHARNESS_SRC is set but $ROBOHARNESS_SRC/pyproject.toml does not exist"
        exit 1
    fi
    echo "[dev] Installing roboharness from source: $ROBOHARNESS_SRC"
    if command -v uv &> /dev/null; then
        uv pip install -e "$ROBOHARNESS_SRC[demo]"
    else
        pip install -e "$ROBOHARNESS_SRC[demo]"
    fi
else
    echo "[prod] Using roboharness from PyPI"
fi

# ------------------------------------------------------------------
# Ensure dependencies are installed
# Smoke mode only needs [demo] + classic-control rendering; full mode needs [lerobot]
# ------------------------------------------------------------------
if [ "${SMOKE:-0}" == "1" ]; then
    if command -v uv &> /dev/null; then
        uv pip install roboharness[demo] "gymnasium[classic-control]"
    else
        pip install roboharness[demo] "gymnasium[classic-control]"
    fi
else
    if command -v uv &> /dev/null; then
        uv pip install -r requirements.txt
    else
        pip install -r requirements.txt
    fi
fi

# ------------------------------------------------------------------
# Run showcase
# ------------------------------------------------------------------
python lerobot_eval_showcase.py "$@"
