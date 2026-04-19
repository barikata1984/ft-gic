"""Analyze segment position CSV recorded by hang_rope.py --segment-csv.

Usage:
    python scripts/analyze_segments.py /tmp/segments.csv \
        --circle-radius 0.1 --circle-period 3.0 --anchor-height 0.8

Prints:
  - Anchor (seg0) XY trajectory: expected circle vs actual
  - Per-segment mean XY radius at last 3 s (steady-state estimate)
  - Per-segment mean Z at last 3 s
  - Rope shape at the last recorded timestep
"""
from __future__ import annotations

import argparse
import math
import sys

import numpy as np


def load_csv(path: str) -> dict[float, np.ndarray]:
    """Return {t: positions array (n_segs, 3)}."""
    import csv

    records: dict[float, list] = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            t = float(row["t"])
            seg = int(row["seg"])
            xyz = (float(row["x"]), float(row["y"]), float(row["z"]))
            records.setdefault(t, []).append((seg, xyz))

    result = {}
    for t, segs in records.items():
        segs_sorted = sorted(segs, key=lambda s: s[0])
        n = len(segs_sorted)
        arr = np.zeros((n, 3))
        for idx, (_, xyz) in enumerate(segs_sorted):
            arr[idx] = xyz
        result[t] = arr
    return dict(sorted(result.items()))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("--circle-radius", type=float, default=0.1)
    p.add_argument("--circle-period", type=float, default=3.0)
    p.add_argument("--anchor-height", type=float, default=0.8)
    p.add_argument("--seg-length", type=float, default=None,
                   help="Segment length [m]; auto-computed if omitted")
    args = p.parse_args()

    print(f"Loading {args.csv} …")
    data = load_csv(args.csv)
    times = np.array(list(data.keys()))
    n_segs = next(iter(data.values())).shape[0]
    print(f"  {len(times)} snapshots, {n_segs} segments, t={times[0]:.3f}..{times[-1]:.3f} s")

    omega = 2 * math.pi / args.circle_period
    R = args.circle_radius

    # ── Anchor (seg 0) trajectory ──────────────────────────────────────────────
    print("\n=== Anchor (seg 0) XY motion ===")
    print(f"{'t':>7}  {'x_sim':>8}  {'y_sim':>8}  {'x_expect':>10}  {'y_expect':>10}  {'err_r':>8}")
    for t, pos in data.items():
        xe, ye = R * math.cos(omega * t), R * math.sin(omega * t)
        xs, ys = pos[0, 0], pos[0, 1]
        err = math.hypot(xs - xe, ys - ye)
        print(f"{t:7.3f}  {xs:+8.4f}  {ys:+8.4f}  {xe:+10.4f}  {ye:+10.4f}  {err:8.4f}")

    # ── Steady-state shape (last 3 s) ──────────────────────────────────────────
    t_steady = times[times >= times[-1] - 3.0]
    steady_pos = np.stack([data[t] for t in t_steady], axis=0)  # (T, n_segs, 3)

    mean_x = steady_pos[:, :, 0].mean(axis=0)
    mean_y = steady_pos[:, :, 1].mean(axis=0)
    mean_z = steady_pos[:, :, 2].mean(axis=0)
    mean_r = np.sqrt(mean_x**2 + mean_y**2)

    print(f"\n=== Per-segment mean position (last {t_steady[-1]-t_steady[0]:.1f} s, {len(t_steady)} samples) ===")
    print(f"{'seg':>4}  {'mean_x':>8}  {'mean_y':>8}  {'mean_z':>8}  {'mean_r_xy':>10}")
    for i in range(n_segs):
        print(f"{i:4d}  {mean_x[i]:+8.4f}  {mean_y[i]:+8.4f}  {mean_z[i]:+8.4f}  {mean_r[i]:10.4f}")

    # ── Last snapshot shape ────────────────────────────────────────────────────
    t_last, pos_last = times[-1], data[times[-1]]
    print(f"\n=== Rope shape at t={t_last:.3f} s ===")
    print(f"{'seg':>4}  {'x':>8}  {'y':>8}  {'z':>8}  {'r_xy':>8}")
    for i in range(n_segs):
        r_xy = math.hypot(pos_last[i, 0], pos_last[i, 1])
        print(f"{i:4d}  {pos_last[i,0]:+8.4f}  {pos_last[i,1]:+8.4f}  {pos_last[i,2]:+8.4f}  {r_xy:8.4f}")

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n=== Summary ===")
    print(f"Anchor (seg0) z mean     : {mean_z[0]:.4f} m  (expect ~{args.anchor_height - (args.seg_length or (args.anchor_height/n_segs)/2):.4f})")
    print(f"Anchor (seg0) r_xy mean  : {mean_r[0]:.4f} m  (expect ~{R:.4f})")
    print(f"Tip    (seg{n_segs-1}) z mean  : {mean_z[-1]:.4f} m")
    print(f"Tip    (seg{n_segs-1}) r_xy mean: {mean_r[-1]:.4f} m")
    r_increase = mean_r[-1] - mean_r[0]
    print(f"r_xy tip - anchor mean   : {r_increase:+.4f} m  ({'outward tilt ✓' if r_increase > 0 else 'NO outward tilt'})")


if __name__ == "__main__":
    main()
