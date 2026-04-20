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


def _compute_joint_drive(
    youngs_modulus: float,
    poissons_ratio: float,
    rope_diameter: float,
    rope_length: float,
    rope_mass: float,
    segments: int,
    damping_ratio: float = 0.3,
    fill_factor: float = 0.3,
) -> tuple[float, float]:
    r = rope_diameter / 2.0
    seg_len = rope_length / segments
    m_seg = rope_mass / segments
    I_eff = math.pi * r**4 / 4.0 * fill_factor  # effective 2nd moment for twisted rope
    k_bend = youngs_modulus * I_eff / seg_len
    I_rot = m_seg * seg_len * seg_len / 3.0
    omega_n = math.sqrt(k_bend / max(I_rot, 1e-12))
    c_damp = 2.0 * damping_ratio * I_rot * omega_n
    DEG_PER_RAD = math.pi / 180.0
    return k_bend * DEG_PER_RAD, c_damp * DEG_PER_RAD


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
    rope.add_argument("--fill-factor", type=float, default=0.3, metavar="PHI",
                     help="Cross-section fill factor φ for twisted/braided rope (0–1). "
                          "I_eff = I_solid * φ. Typical nylon rope: 0.3–0.5")
    rope.add_argument("--poissons-ratio", type=float, default=0.35, metavar="NU")
    rope.add_argument("--damping-ratio", type=float, default=0.3, metavar="ZETA")

    sim = p.add_argument_group("simulation")
    sim.add_argument("--segments", type=int, default=25)
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
    from isaacsim.core.api import World
    from isaacsim.sensors.camera import Camera
    from pxr import Gf, UsdGeom

    from rope_sim.rope_builder import RopeBuilder, RopeConfig

    # ── joint drive parameters ──────────────────────────────────────────────
    k_bend, c_damp = _compute_joint_drive(
        youngs_modulus=args.youngs_modulus,
        poissons_ratio=args.poissons_ratio,
        rope_diameter=args.rope_diameter,
        rope_length=args.rope_length,
        rope_mass=args.rope_mass,
        segments=args.segments,
        damping_ratio=args.damping_ratio,
        fill_factor=args.fill_factor,
    )

    r = args.rope_diameter / 2.0
    I_eff = math.pi * r**4 / 4.0 * args.fill_factor
    L_seg = args.rope_length / args.segments
    m_seg = args.rope_mass / args.segments
    I_rot = max(m_seg * L_seg * L_seg / 3.0, 1e-12)
    omega_n = math.sqrt((args.youngs_modulus * I_eff / L_seg) / I_rot)
    dt_max = 0.5 / omega_n
    dt = min(args.dt, dt_max)
    if dt < args.dt:
        carb.log_warn(
            f"[record] dt reduced {args.dt:.4f}→{dt:.6f}s "
            f"(omega_n={omega_n:.1f} rad/s)"
        )
    args.dt = dt

    # physics_dt=dt, rendering_dt drives how often camera.get_rgba() is valid.
    # We capture every N physics steps so rendering_dt can stay at 1/fps.
    capture_dt = 1.0 / args.fps
    world = World(
        physics_dt=dt,
        rendering_dt=capture_dt,
        stage_units_in_meters=1.0,
    )
    world.scene.add_default_ground_plane()

    stage = simulation_app.context.get_stage()
    UsdGeom.Xform.Define(stage, "/World/Rope")

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
    # Position: 1.5 m diagonally, looking at rope center
    cam_pos = (1.2, -1.2, 0.8)
    cam_target = (0.0, 0.0, args.anchor_height / 2.0)

    camera = Camera(
        prim_path="/World/RecordCam",
        position=np.array(cam_pos),
        frequency=args.fps,
        resolution=(args.width, args.height),
    )

    # Point camera toward rope center using look-at quaternion
    _eye = np.array(cam_pos)
    _tgt = np.array(cam_target)
    _fwd = _tgt - _eye
    _fwd /= np.linalg.norm(_fwd)
    # Isaac Sim camera default forward = -Z in camera frame; use USD camera convention
    # We set orientation via prim xform after initialize()
    world.reset()
    camera.initialize()

    # Orient camera to look at rope: compute rotation from -Z to _fwd direction
    # Using Gf.Rotation for axis-angle quaternion
    _cam_prim = stage.GetPrimAtPath("/World/RecordCam")
    _xformable = UsdGeom.Xformable(_cam_prim)
    _xform_ops = _xformable.GetOrderedXformOps()
    # Set translate op
    for op in _xform_ops:
        if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
            op.Set(Gf.Vec3d(*cam_pos))
            break
    # Compute look-at rotation: camera -Z → _fwd
    _default_fwd = Gf.Vec3d(0, 0, -1)
    _target_fwd = Gf.Vec3d(*_fwd.tolist())
    _rot = Gf.Rotation(_default_fwd, _target_fwd)
    _quat = _rot.GetQuaternion()
    _qi = _quat.GetImaginary()
    _qr = _quat.GetReal()
    for op in _xform_ops:
        if op.GetOpType() == UsdGeom.XformOp.TypeOrient:
            op.Set(Gf.Quatd(float(_qr), float(_qi[0]), float(_qi[1]), float(_qi[2])))
            break

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
    debug_dir = Path(__file__).resolve().parents[1] / "debug"
    debug_dir.mkdir(exist_ok=True)
    if args.output:
        out_path = Path(args.output)
    else:
        ts = time.strftime("%Y%m%d_%H%M%S")
        suffix = f"_circle_r{args.circle_radius:.2f}" if circle else ""
        out_path = debug_dir / f"{ts}_rope{suffix}.mp4"

    # ── recording loop ──────────────────────────────────────────────────────
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
        carb.log_warn(f"[record] encoding {len(frames)} frames via ffmpeg ...")
        _encode_mp4_ffmpeg(frames, out_path, args.fps)
        carb.log_warn(f"[record] saved → {out_path}")
    else:
        carb.log_warn("[record] no frames captured — skipping encode")

    simulation_app.close()


def _encode_mp4_ffmpeg(frames: list, out_path: Path, fps: int) -> None:
    # cv2 in Isaac Sim's Python env has FFMPEG built-in — use VideoWriter directly
    import cv2

    h, w = frames[0].shape[:2]
    # Try H.264 first (requires FFMPEG backend), fall back to mp4v
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (w, h))
    if not writer.isOpened():
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(out_path), fourcc, fps, (w, h))
    for frame in frames:
        writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    writer.release()


if __name__ == "__main__":
    main()
