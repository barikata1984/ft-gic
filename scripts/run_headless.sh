#!/usr/bin/env bash
# Headless runner for hang_rope.py.
#
# Forwards every extra argument to the Python script. Common rope-material flags:
#   --youngs-modulus 1e9 --poissons-ratio 0.35 --damping-ratio 0.3
# See scripts/hang_rope.py --help for the full list.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

PYTHONPATH="${PROJECT_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}" \
    /isaac-sim/python.sh "${SCRIPT_DIR}/hang_rope.py" --headless "$@"
