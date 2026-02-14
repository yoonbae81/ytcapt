#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"

# Default to running the web app if no arguments, 
# otherwise pass arguments to the CLI tool.
if [ $# -eq 0 ]; then
    echo "Starting web application..."
    "$VENV_PYTHON" "$PROJECT_DIR/src/app.py"
else
    echo "Running CLI tool..."
    "$VENV_PYTHON" "$PROJECT_DIR/src/ytcapt.py" "$@"
fi
