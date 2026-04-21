"""Record rope simulation: anchor swings about its local X axis (sinusoidal).

Anchor is fixed at xy=(0,0) at height = rope_length + 0.10 m above the floor,
so the rope tip clears the ground by ~10 cm at rest.

Swing motion:  θ(t) = (π/4) · sin(2π · t / swing_period)  [rad]
applied as a USD RotateX op on Segment_000 (kinematic anchor).

Run via:
    /isaac-sim/python.sh scripts/swing_rope.py [options]
    scripts/run_headless.sh scripts/swing_rope.py [options]
"""
from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

_G = 9.81


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Record sinusoidal-swing rope simulation to MP4",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    rope = p.add_argument_group("rope")
    rope.add_argument("--rope-length", type=float, default=0.6, metavar="M")
    rope.add_argument("--rope-diameter", type=float, default=0.01, metavar="M")
    rope.add_argument("--rope-mass", type=float, default=0.1, metavar="KG")
    rope.add_argument("--youngs-modulus", type=float, default=1e9, metavar="PA")
    rope.add_argument("--fill-factor", type=float, default=0.1, metavar="PHI")
    rope.add_argument("--poissons-ratio", type=float, default=0.35, metavar="NU")
    rope.add_argument("--damping-ratio", type=float, default=0.3, metavar="ZETA")

    sim = p.add_argument_group("simulation")
    sim.add_argument("--segments", type=int, default=64)
    sim.add_argument("--swing-limit", type=float, default=60.0, metavar="DEG")
    sim.add_argument("--ground-clearance", type=float, default=0.1, metavar="M",
                     help="Gap between rope tip (at rest) and ground [m]")
    sim.add_argument("--dt", type=float, default=1 / 60.0, metavar="S")
    sim.add_argument("--duration", type=float, default=10.0, metavar="S",
                     help="Total simulation duration [s]")

    motion = p.add_argument_group("anchor swing motion")
    motion.add_argument("--swing-amplitude", type=float, default=math.pi / 4,
                        metavar="RAD",
                        help="Peak swing angle about local X axis [rad] (default: π/4)")
    motion.add_argument("--swing-period", type=float, default=1.0, metavar="S",
                        help="Period of the sinusoidal swing [s]")

    rec = p.add_argument_group("recording")
    rec.add_argument("--fps", type=int, default=30)
    rec.add_argument("--width", type=int, default=1280)
    rec.add_argument("--height", type=int, default=720)
    rec.add_argument("--output", type=str, default="",
                     help="Output MP4 path (default: debug/<timestamp>_swing.mp4)")

    return p


def main() -> None:
    args, _ = _build_parser().parse_known_args()

    from isaacsim import SimulationApp

    simulation_app = SimulationApp({
        "headless": True,
        "renderer": "RayTracedLighting",
    })

    import carb
    import numpy as np
    from pxr import Gf, UsdGeom

    from rope_sim.camera_utils import make_camera
    from rope_sim.rope_builder import RopeBuilder, RopeConfig
    from rope_sim.scene_utils import setup_recording_world
    from rope_sim.sim_utils import clamp_dt, compute_joint_drive

    k_bend, c_damp = compute_joint_drive(
        youngs_modulus=args.youngs_modulus,
        rope_diameter=args.rope_diameter,
        rope_length=args.rope_length,
        rope_mass=args.rope_mass,
        segments=args.segments,
        damping_ratio=args.damping_ratio,
        fill_factor=args.fill_factor,
    )

    dt = clamp_dt(
        args.dt,
        youngs_modulus=args.youngs_modulus,
        rope_diameter=args.rope_diameter,
        rope_length=args.rope_length,
        rope_mass=args.rope_mass,
        segments=args.segments,
        fill_factor=args.fill_factor,
        label="swing",
    )
    args.dt = dt

    # anchor_height: top of Segment_000 sits at this z.
    # Segment_000 center is at anchor_height - L_seg/2.
    # Rope tip (bottom of last segment) at rest: anchor_height - rope_length.
    # Require: anchor_height - rope_length >= ground_clearance
    anchor_height = args.rope_length + args.ground_clearance
    carb.log_warn(
        f"[swing] anchor_height={anchor_height:.3f}m "
        f"(rope_length={args.rope_length}m + clearance={args.ground_clearance}m)"
    )

    world, stage = setup_recording_world(simulation_app, physics_dt=dt, fps=args.fps)

    cfg = RopeConfig(
        length=args.rope_length,
        diameter=args.rope_diameter,
        mass=args.rope_mass,
        segments=args.segments,
        swing_limit_deg=args.swing_limit,
        anchor_height=anchor_height,
        joint_stiffness=k_bend,
        joint_damping=c_damp,
    )
    builder = RopeBuilder(cfg, stage)
    builder.build()

    # ── camera placement ────────────────────────────────────────────────────
    camera = make_camera(
        world,
        prim_path="/World/RecordCam",
        position=[3.5, 0.0, 1.2],
        target=[0.0, 0.0, 0.4],
        fps=args.fps,
        resolution=(args.width, args.height),
    )

    # ── anchor swing setup ──────────────────────────────────────────────────
    # Add a RotateX op to Segment_000 so we can drive the swing angle each step.
    # The TranslateOp is already on the prim (set by RopeBuilder); we append RotateX.
    _anchor_prim = builder.segment_prims[0]
    _anchor_xformable = UsdGeom.Xformable(_anchor_prim)

    # Add RotateX op (appended after Translate in xform stack)
    _rotate_x_op = _anchor_xformable.AddRotateXOp()
    _rotate_x_op.Set(0.0)  # start at 0°

    swing_omega = 2.0 * math.pi / args.swing_period
    amp_deg = math.degrees(args.swing_amplitude)
    carb.log_warn(
        f"[swing] sinusoidal swing: amplitude={amp_deg:.1f}°, "
        f"period={args.swing_period:.2f}s, omega={swing_omega:.3f} rad/s"
    )

    def _update_anchor_swing(t: float) -> None:
        angle_deg = amp_deg * math.sin(swing_omega * t)
        _rotate_x_op.Set(angle_deg)

    world.add_physics_callback(
        "anchor_swing", lambda _: _update_anchor_swing(world.current_time)
    )

    # ── output path ─────────────────────────────────────────────────────────
    from rope_sim.video_utils import default_output_path

    out_path = Path(args.output) if args.output else default_output_path("_swing_rope")

    # ── recording loop ──────────────────────────────────────────────────────
    capture_dt = 1.0 / args.fps
    num_steps = int(args.duration / dt)
    steps_per_frame = max(1, int(round(capture_dt / dt)))
    expected_frames = num_steps // steps_per_frame
    carb.log_warn(
        f"[swing] {num_steps} physics steps, capturing every {steps_per_frame} steps "
        f"→ ~{expected_frames} frames @ {args.fps}fps → {args.duration:.1f}s video"
    )
    carb.log_warn(f"[swing] output: {out_path}")

    frames: list[np.ndarray] = []
    wall_start = time.time()

    for step in range(num_steps):
        do_render = (step % steps_per_frame == 0)
        world.step(render=do_render)
        if do_render:
            rgba = camera.get_rgba()
            if rgba is not None and rgba.size > 0:
                frames.append(rgba[:, :, :3].copy())

        if step % (steps_per_frame * args.fps * 5) == 0:
            t_sim = world.current_time
            t_wall = time.time() - wall_start
            carb.log_warn(
                f"[swing] sim={t_sim:.1f}s  wall={t_wall:.1f}s  frames={len(frames)}"
            )

    wall_elapsed = time.time() - wall_start
    carb.log_warn(
        f"[swing] done: {len(frames)} frames in {wall_elapsed:.1f}s wall-time"
    )

    if frames:
        from rope_sim.video_utils import encode_mp4

        carb.log_warn(f"[swing] encoding {len(frames)} frames ...")
        encode_mp4(frames, out_path, args.fps)
        carb.log_warn(f"[swing] saved → {out_path}")
    else:
        carb.log_warn("[swing] no frames captured — skipping encode")

    simulation_app.close()


if __name__ == "__main__":
    main()
