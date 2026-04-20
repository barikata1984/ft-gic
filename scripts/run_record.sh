#!/usr/bin/env bash
# Record rope simulation to MP4 (headless offscreen rendering).
#
# Output: debug/<timestamp>_rope[_circle_r<R>].mp4
#
# Examples:
#   scripts/run_record.sh --duration 10
#   scripts/run_record.sh --circle-radius 0.1 --circle-period 3.0 --duration 10
#   scripts/run_record.sh --duration 10 --fps 30 --width 1280 --height 720
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

PYTHONPATH="${PROJECT_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}" \
    /isaac-sim/python.sh "${SCRIPT_DIR}/record_rope.py" "$@"
