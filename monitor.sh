#!/bin/bash

# Navigate to the script directory
cd "$(dirname "$0")"

# Check if venv exists, if so use it, otherwise use system python
if [ -d "venv" ]; then
    ./venv/bin/python3 monitor.py
else
    python3 monitor.py
fi
