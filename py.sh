#!/bin/bash
# FnF Marketing Simulator — Python 3.11 wrapper
# Usage: ./py.sh run.py | ./py.sh -m pip install xxx | ./py.sh -c "print('hi')"
DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$DIR/.venv/Scripts/python.exe" "$@"
