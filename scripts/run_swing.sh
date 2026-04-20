#!/usr/bin/env bash
# Record sinusoidal-swing rope simulation to MP4 (headless offscreen rendering).
#
# Anchor is fixed at xy=(0,0) and oscillates about its local X axis:
#   θ(t) = (π/4) · sin(2π · t / swing_period)
#
# Output: debug/<timestamp>_swing_rope.mp4
#
# Examples:
#   scripts/run_swing.sh --duration 10
#   scripts/run_swing.sh --swing-amplitude 0.785 --swing-period 1.0 --duration 10
#   scripts/run_swing.sh --duration 10 --fps 30 --width 1280 --height 720
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

PYTHONPATH="${PROJECT_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}" \
    /isaac-sim/python.sh "${SCRIPT_DIR}/swing_rope.py" "$@"
