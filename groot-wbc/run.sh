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
# Install roboharness
# Priority: ROBOHARNESS_SRC > local source > git main > PyPI
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
elif [ "${ROBOHARNESS_PYPI:-0}" == "1" ]; then
    echo "[pypi] Installing roboharness from PyPI"
else
    echo "[git] Installing roboharness from main branch"
    if command -v uv &> /dev/null; then
        uv pip install "roboharness[demo] @ git+https://github.com/MiaoDX/roboharness.git"
    else
        pip install "roboharness[demo] @ git+https://github.com/MiaoDX/roboharness.git"
    fi
fi

# ------------------------------------------------------------------
# Ensure dependencies are installed
# ------------------------------------------------------------------
if command -v uv &> /dev/null; then
    uv pip install -r requirements.txt
else
    pip install -r requirements.txt
fi

# ------------------------------------------------------------------
# Run showcase
# ------------------------------------------------------------------
python groot_wbc_showcase.py "$@"
