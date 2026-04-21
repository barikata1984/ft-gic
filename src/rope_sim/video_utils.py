"""Video encoding utilities shared across rope recording scripts."""

from __future__ import annotations

import time
from pathlib import Path


def encode_mp4(frames: list, out_path: Path, fps: int) -> None:
    """Write RGB frame list to an mp4 file using cv2 (H.264 preferred, mp4v fallback)."""
    import cv2
    import numpy as np  # noqa: F401 — kept for callers that pass np arrays

    h, w = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (w, h))
    for frame in frames:
        writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    writer.release()


def default_output_path(suffix: str = "") -> Path:
    """Return debug/<timestamp><suffix>.mp4, creating the debug/ dir if needed.

    suffix should include a leading underscore if non-empty, e.g. '_swing_rope'.
    """
    debug_dir = Path(__file__).resolve().parents[2] / "debug"
    debug_dir.mkdir(exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    return debug_dir / f"{ts}{suffix}.mp4"
