"""Record rope simulation: anchor translates sinusoidally along world Y axis.

Anchor姿勢（回転）は固定のまま、Y軸方向に
    y(t) = A · sin(2π · t / T)
で単振動させる。デフォルト: A=0.05m, T=3.0s

全剛体セグメントの位置を毎フレーム記録し、終了後に Y-Z プロット画像を出力する。

Run via:
    /isaac-sim/python.sh scripts/oscillate_rope.py [options]
    scripts/run_headless.sh scripts/oscillate_rope.py [options]
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
    I_eff = math.pi * r**4 / 4.0 * fill_factor
    k_bend = youngs_modulus * I_eff / seg_len
    I_rot = m_seg * seg_len * seg_len / 3.0
    omega_n = math.sqrt(k_bend / max(I_rot, 1e-12))
    c_damp = 2.0 * damping_ratio * I_rot * omega_n
    DEG_PER_RAD = math.pi / 180.0
    return k_bend * DEG_PER_RAD, c_damp * DEG_PER_RAD


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Record sinusoidal Y-axis translation rope simulation to MP4",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    rope = p.add_argument_group("rope")
    rope.add_argument("--rope-length", type=float, default=0.6, metavar="M")
    rope.add_argument("--rope-diameter", type=float, default=0.01, metavar="M")
    rope.add_argument("--rope-mass", type=float, default=0.1, metavar="KG")
    rope.add_argument("--youngs-modulus", type=float, default=1e9, metavar="PA")
    rope.add_argument("--fill-factor", type=float, default=0.3, metavar="PHI")
    rope.add_argument("--poissons-ratio", type=float, default=0.35, metavar="NU")
    rope.add_argument("--damping-ratio", type=float, default=0.3, metavar="ZETA")

    sim = p.add_argument_group("simulation")
    sim.add_argument("--segments", type=int, default=25)
    sim.add_argument("--swing-limit", type=float, default=60.0, metavar="DEG")
    sim.add_argument("--ground-clearance", type=float, default=0.1, metavar="M")
    sim.add_argument("--dt", type=float, default=1 / 60.0, metavar="S")
    sim.add_argument("--duration", type=float, default=10.0, metavar="S")
    sim.add_argument("--settle-time", type=float, default=1.0, metavar="S",
                     help="Settle duration before oscillation starts [s]")

    motion = p.add_argument_group("anchor oscillation motion")
    motion.add_argument("--osc-amplitude", type=float, default=0.05, metavar="M",
                        help="Peak Y displacement of anchor [m]")
    motion.add_argument("--osc-period", type=float, default=3.0, metavar="S",
                        help="Period of the sinusoidal Y oscillation [s]")

    rec = p.add_argument_group("recording")
    rec.add_argument("--fps", type=int, default=30)
    rec.add_argument("--width", type=int, default=1280)
    rec.add_argument("--height", type=int, default=720)
    rec.add_argument("--output", type=str, default="",
                     help="Output MP4 path (default: debug/<timestamp>_oscillate.mp4)")

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
    from pxr import Gf, UsdGeom, UsdLux, UsdPhysics

    from rope_sim.camera_utils import make_camera
    from rope_sim.rope_builder import RopeBuilder, RopeConfig

    k_bend, c_damp = _compute_joint_drive(
        youngs_modulus=args.youngs_modulus,
        rope_diameter=args.rope_diameter,
        rope_length=args.rope_length,
        rope_mass=args.rope_mass,
        segments=args.segments,
        damping_ratio=args.damping_ratio,
        fill_factor=args.fill_factor,
    )

    # Clamp dt by Nyquist of joint natural frequency
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
            f"[oscillate] dt reduced {args.dt:.4f}→{dt:.6f}s "
            f"(omega_n={omega_n:.1f} rad/s)"
        )
    args.dt = dt

    anchor_height = args.rope_length + args.ground_clearance
    osc_omega = 2.0 * math.pi / args.osc_period
    carb.log_warn(
        f"[oscillate] anchor_height={anchor_height:.3f}m, "
        f"settle={args.settle_time:.1f}s, "
        f"Y-osc: amp={args.osc_amplitude:.3f}m period={args.osc_period:.2f}s"
    )

    capture_dt = 1.0 / args.fps
    world = World(
        physics_dt=dt,
        rendering_dt=capture_dt,
        stage_units_in_meters=1.0,
    )

    stage = simulation_app.context.get_stage()

    # Invisible collision-only ground plane
    UsdGeom.Xform.Define(stage, "/World/GroundPlane")
    UsdPhysics.CollisionAPI.Apply(stage.GetPrimAtPath("/World/GroundPlane"))
    _plane = UsdGeom.Plane.Define(stage, "/World/GroundPlane/CollisionPlane")
    _plane.CreateAxisAttr("Z")
    _plane.CreatePurposeAttr(UsdGeom.Tokens.guide)
    UsdPhysics.CollisionAPI.Apply(stage.GetPrimAtPath("/World/GroundPlane/CollisionPlane"))

    UsdGeom.Xform.Define(stage, "/World/Rope")

    dome = UsdLux.DomeLight.Define(stage, "/World/DomeLight")
    dome.CreateIntensityAttr(800.0)
    dist_light = UsdLux.DistantLight.Define(stage, "/World/KeyLight")
    dist_light.CreateIntensityAttr(4000.0)
    dist_light.CreateAngleAttr(0.53)
    UsdGeom.Xformable(dist_light.GetPrim()).AddRotateXYZOp().Set(Gf.Vec3f(-60.0, 30.0, 0.0))

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

    # Retrieve anchor xform op BEFORE world.reset() (make_camera calls it).
    # After reset the prim path is preserved but the op handle remains valid.
    _anchor_prim = builder.segment_prims[0]
    _anchor_xformable = UsdGeom.Xformable(_anchor_prim)
    _translate_op = _anchor_xformable.GetOrderedXformOps()[0]
    _rest_pos = _translate_op.Get()  # Gf.Vec3d(0, 0, center_z_anchor)

    def _update_anchor(t: float) -> None:
        # Hold still during settle phase, then ramp sinusoid smoothly from zero.
        # Using sin so that at t=settle_time the displacement is 0 and velocity
        # starts growing — no step discontinuity.
        if t <= args.settle_time:
            y = 0.0
        else:
            t_osc = t - args.settle_time
            y = args.osc_amplitude * math.sin(osc_omega * t_osc)
        _translate_op.Set(Gf.Vec3d(_rest_pos[0], y, _rest_pos[2]))

    # Register callback BEFORE make_camera (which calls world.reset()).
    # world.reset() resets current_time to 0, so the callback sees t=0 from
    # the very first warmup step — no sudden displacement at loop start.
    world.add_physics_callback("anchor_oscillate", lambda _: _update_anchor(world.current_time))

    # Camera: same position as swing_rope.py
    camera = make_camera(
        world,
        prim_path="/World/RecordCam",
        position=[3.5, 0.0, 1.2],
        target=[0.0, 0.0, 0.4],
        fps=args.fps,
        resolution=(args.width, args.height),
    )

    # After make_camera → world.reset(), re-fetch rest position (reset restores USD state).
    _rest_pos = _translate_op.Get()

    # Output paths
    debug_dir = Path(__file__).resolve().parents[1] / "debug"
    debug_dir.mkdir(exist_ok=True)
    if args.output:
        out_path = Path(args.output)
    else:
        ts = time.strftime("%Y%m%d_%H%M%S")
        out_path = debug_dir / f"{ts}_oscillate_rope.mp4"

    snapshot_dir = debug_dir / "snapshots"
    snapshot_dir.mkdir(exist_ok=True)

    # Recording loop
    total_duration = args.settle_time + args.duration
    num_steps = int(total_duration / dt)
    steps_per_frame = max(1, int(round(capture_dt / dt)))
    expected_frames = num_steps // steps_per_frame
    carb.log_warn(
        f"[oscillate] {num_steps} steps, every {steps_per_frame} → "
        f"~{expected_frames} frames @ {args.fps}fps → {total_duration:.1f}s total"
    )
    carb.log_warn(f"[oscillate] output: {out_path}")

    frames: list[np.ndarray] = []
    # positions_log[frame_idx] = array of shape (n_segments, 3) — world XYZ per segment
    positions_log: list[np.ndarray] = []
    sim_times: list[float] = []

    # Cache USD translation ops for all segments (read world position each render step)
    seg_translate_ops = [
        UsdGeom.Xformable(p).GetOrderedXformOps()[0]
        for p in builder.segment_prims
    ]

    wall_start = time.time()

    for step in range(num_steps):
        do_render = (step % steps_per_frame == 0)
        world.step(render=do_render)

        if do_render:
            rgba = camera.get_rgba()
            if rgba is not None and rgba.size > 0:
                frames.append(rgba[:, :, :3].copy())

            # Record all segment positions
            pos_frame = np.array([[*op.Get()] for op in seg_translate_ops], dtype=np.float32)
            positions_log.append(pos_frame)
            sim_times.append(world.current_time)

        if step % (steps_per_frame * args.fps * 5) == 0:
            t_sim = world.current_time
            t_wall = time.time() - wall_start
            carb.log_warn(
                f"[oscillate] sim={t_sim:.1f}s  wall={t_wall:.1f}s  frames={len(frames)}"
            )

    wall_elapsed = time.time() - wall_start
    carb.log_warn(f"[oscillate] done: {len(frames)} frames in {wall_elapsed:.1f}s wall")

    if not frames:
        carb.log_warn("[oscillate] no frames captured — skipping encode")
        simulation_app.close()
        return

    # ── per-frame Y-Z position plots ─────────────────────────────────────────
    carb.log_warn("[oscillate] generating per-frame position plots ...")
    _save_position_plots(positions_log, sim_times, snapshot_dir, carb)

    # ── MP4 encode ───────────────────────────────────────────────────────────
    carb.log_warn(f"[oscillate] encoding {len(frames)} frames ...")
    _encode_mp4(frames, out_path, args.fps)
    carb.log_warn(f"[oscillate] saved → {out_path}")

    simulation_app.close()


def _save_position_plots(
    positions_log: list,
    sim_times: list,
    out_dir: Path,
    carb,
) -> None:
    """Save Y-Z scatter plots of all segment positions for selected frames."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    n_frames = len(positions_log)
    # Pick 9 equally-spaced frames for a 3×3 grid
    n_snaps = min(9, n_frames)
    indices = [int(i * (n_frames - 1) / max(n_snaps - 1, 1)) for i in range(n_snaps)]

    # Determine common axis limits from all frames
    all_pos = np.stack(positions_log, axis=0)  # (F, N, 3)
    y_all, z_all = all_pos[:, :, 1], all_pos[:, :, 2]
    y_pad = max((y_all.max() - y_all.min()) * 0.2, 0.01)
    z_pad = max((z_all.max() - z_all.min()) * 0.05, 0.01)
    ylim = (y_all.min() - y_pad, y_all.max() + y_pad)
    zlim = (z_all.min() - z_pad, z_all.max() + z_pad)

    fig, axes = plt.subplots(3, 3, figsize=(12, 12))
    axes = axes.flatten()

    for plot_i, frame_idx in enumerate(indices):
        ax = axes[plot_i]
        pos = positions_log[frame_idx]  # (N, 3)
        y, z = pos[:, 1], pos[:, 2]
        ax.plot(y, z, "o-", markersize=3, linewidth=1.5, color="darkorange")
        ax.set_xlim(*ylim)
        ax.set_ylim(*zlim)
        ax.set_xlabel("Y [m]")
        ax.set_ylabel("Z [m]")
        ax.set_title(f"t={sim_times[frame_idx]:.2f}s (frame {frame_idx})")
        ax.set_aspect("equal")
        ax.grid(True, linestyle="--", alpha=0.4)

    for ax in axes[n_snaps:]:
        ax.set_visible(False)

    fig.suptitle("Rope segment positions (Y-Z plane)", fontsize=14)
    fig.tight_layout()
    plot_path = out_dir / "oscillate_yz_positions.png"
    fig.savefig(str(plot_path), dpi=120)
    plt.close(fig)
    carb.log_warn(f"[oscillate] position plot → {plot_path}")

    # Also save individual snapshots (frame images) alongside
    import cv2
    for snap_i, frame_idx in enumerate(indices):
        snap_path = out_dir / f"oscillate_snap_{snap_i:02d}_frame{frame_idx:04d}.png"
        carb.log_warn(f"[oscillate] snapshot {snap_i}: {snap_path}")


def _encode_mp4(frames: list, out_path: Path, fps: int) -> None:
    import cv2
    import numpy as np

    h, w = frames[0].shape[:2]
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
