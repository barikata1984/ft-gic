"""Record rope simulation to MP4 using offscreen camera rendering.

Runs headless (no GUI window). Camera captures frames at ~30 fps wall-time,
physics advances at the stability-required dt (many substeps per frame).

Output: debug/<timestamp>_rope.mp4

Run via:
    /isaac-sim/python.sh scripts/record_rope.py [options]
    # or with the shell wrapper:
    scripts/run_headless.sh scripts/record_rope.py [options]
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
        description="Record rope simulation to MP4",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    rope = p.add_argument_group("rope")
    rope.add_argument("--rope-length", type=float, default=0.6, metavar="M")
    rope.add_argument("--rope-diameter", type=float, default=0.01, metavar="M")
    rope.add_argument("--rope-mass", type=float, default=0.1, metavar="KG")
    rope.add_argument("--youngs-modulus", type=float, default=1e9, metavar="PA",
                     help="Young's modulus E of the fibre material [Pa] (solid nylon ~1e9)")
    rope.add_argument("--fill-factor", type=float, default=0.1, metavar="PHI",
                     help="Cross-section fill factor φ for twisted/braided rope (0–1). "
                          "I_eff = I_solid * φ. Typical nylon rope: 0.3–0.5")
    rope.add_argument("--poissons-ratio", type=float, default=0.35, metavar="NU")
    rope.add_argument("--damping-ratio", type=float, default=0.3, metavar="ZETA")

    sim = p.add_argument_group("simulation")
    sim.add_argument("--segments", type=int, default=64)
    sim.add_argument("--swing-limit", type=float, default=60.0, metavar="DEG")
    sim.add_argument("--anchor-height", type=float, default=0.8, metavar="M")
    sim.add_argument("--dt", type=float, default=1 / 60.0, metavar="S")
    sim.add_argument("--duration", type=float, default=10.0, metavar="S",
                     help="Simulation duration to record [s]")

    motion = p.add_argument_group("anchor motion")
    motion.add_argument("--circle-radius", type=float, default=0.0, metavar="M")
    motion.add_argument("--circle-period", type=float, default=3.0, metavar="S")

    rec = p.add_argument_group("recording")
    rec.add_argument("--fps", type=int, default=30,
                     help="Video frame rate [fps]")
    rec.add_argument("--width", type=int, default=1280, help="Video width [px]")
    rec.add_argument("--height", type=int, default=720, help="Video height [px]")
    rec.add_argument("--output", type=str, default="",
                     help="Output MP4 path (default: debug/<timestamp>_rope.mp4)")

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

    # ── joint drive parameters ──────────────────────────────────────────────
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
        label="record",
    )
    args.dt = dt

    world, stage = setup_recording_world(simulation_app, physics_dt=dt, fps=args.fps)

    cfg = RopeConfig(
        length=args.rope_length,
        diameter=args.rope_diameter,
        mass=args.rope_mass,
        segments=args.segments,
        swing_limit_deg=args.swing_limit,
        anchor_height=args.anchor_height,
        joint_stiffness=k_bend,
        joint_damping=c_damp,
    )
    builder = RopeBuilder(cfg, stage)
    builder.build()

    # Pre-shift rope to circle start position (avoids transient shock)
    if args.circle_radius > 0.0:
        x0 = args.circle_radius
        for prim in builder.segment_prims:
            t_op = next(
                op for op in UsdGeom.Xformable(prim).GetOrderedXformOps()
                if op.GetOpType() == UsdGeom.XformOp.TypeTranslate
            )
            cur = t_op.Get()
            t_op.Set(Gf.Vec3d(cur[0] + x0, cur[1], cur[2]))

    # ── camera placement ────────────────────────────────────────────────────
    # Parameters tuned via _check_camera.py: d=3.5, y=0.0, z=1.2, target_z=0.4
    camera = make_camera(
        world,
        prim_path="/World/RecordCam",
        position=[3.5, 0.0, 1.2],
        target=[0.0, 0.0, 0.4],
        fps=args.fps,
        resolution=(args.width, args.height),
    )

    # ── anchor circle setup ─────────────────────────────────────────────────
    circle = args.circle_radius > 0.0
    omega = 0.0
    anchor_center_z = args.anchor_height - L_seg / 2.0
    if circle:
        omega = 2.0 * math.pi / args.circle_period
        carb.log_warn(
            f"[record] circular anchor: R={args.circle_radius}m, "
            f"T={args.circle_period}s, omega={omega:.3f} rad/s"
        )

    _anchor_translate_op = None
    if circle:
        _anchor_prim = builder.segment_prims[0]
        _anchor_translate_op = next(
            op for op in UsdGeom.Xformable(_anchor_prim).GetOrderedXformOps()
            if op.GetOpType() == UsdGeom.XformOp.TypeTranslate
        )

    def _update_anchor(t: float) -> None:
        if not circle or _anchor_translate_op is None:
            return
        x = args.circle_radius * math.cos(omega * t)
        y = args.circle_radius * math.sin(omega * t)
        _anchor_translate_op.Set(Gf.Vec3d(x, y, anchor_center_z))

    if circle:
        world.add_physics_callback(
            "anchor_circle", lambda _: _update_anchor(world.current_time)
        )

    # ── output path ─────────────────────────────────────────────────────────
    from rope_sim.video_utils import default_output_path

    if args.output:
        out_path = Path(args.output)
    else:
        suffix = f"_circle_r{args.circle_radius:.2f}" if circle else "_rope"
        out_path = default_output_path(suffix)

    # ── recording loop ──────────────────────────────────────────────────────
    capture_dt = 1.0 / args.fps
    num_steps = int(args.duration / dt)
    # Capture every N physics steps to achieve ~fps
    steps_per_frame = max(1, int(round(capture_dt / dt)))
    expected_frames = num_steps // steps_per_frame
    carb.log_warn(
        f"[record] {num_steps} physics steps, capturing every {steps_per_frame} steps "
        f"→ ~{expected_frames} frames @ {args.fps}fps → {args.duration:.1f}s video"
    )
    carb.log_warn(f"[record] output: {out_path}")

    frames: list[np.ndarray] = []
    wall_start = time.time()

    for step in range(num_steps):
        do_render = (step % steps_per_frame == 0)
        world.step(render=do_render)
        if do_render:
            rgba = camera.get_rgba()
            if rgba is not None and rgba.size > 0:
                frames.append(rgba[:, :, :3].copy())  # drop alpha, keep RGB

        if step % (steps_per_frame * args.fps * 5) == 0:  # log every 5s of sim
            t_sim = world.current_time
            t_wall = time.time() - wall_start
            carb.log_warn(
                f"[record] sim={t_sim:.1f}s  wall={t_wall:.1f}s  "
                f"frames={len(frames)}"
            )

    wall_elapsed = time.time() - wall_start
    carb.log_warn(
        f"[record] done: {len(frames)} frames in {wall_elapsed:.1f}s wall-time "
        f"(sim={args.duration:.1f}s, ratio={args.duration/wall_elapsed:.2f}x)"
    )

    # simulation_app.close() calls sys.exit() — encode BEFORE it.
    # Use a subprocess ffmpeg pipe opened at loop start so we stream frames
    # incrementally and don't hold all in RAM. But frames are already collected,
    # so we open the pipe here and flush before close().
    if frames:
        from rope_sim.video_utils import encode_mp4

        carb.log_warn(f"[record] encoding {len(frames)} frames via ffmpeg ...")
        encode_mp4(frames, out_path, args.fps)
        carb.log_warn(f"[record] saved → {out_path}")
    else:
        carb.log_warn("[record] no frames captured — skipping encode")

    simulation_app.close()


if __name__ == "__main__":
    main()
