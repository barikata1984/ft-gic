"""Simulate a rope hanging from a fixed anchor under gravity.

With --circle-radius > 0, the anchor traces a horizontal circle.

Run via the provided shell scripts, which set PYTHONPATH and use
/isaac-sim/python.sh as the interpreter.

Headed:   scripts/run_gui.sh [options]
Headless: scripts/run_headless.sh [options]
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

_G = 9.81  # m/s²


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Rope hanging simulation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # ── mode ──────────────────────────────────────────────────────────────────
    p.add_argument("--headless", action="store_true", default=False, help="Run without GUI")

    # ── rope physical properties ───────────────────────────────────────────────
    rope = p.add_argument_group("rope")
    rope.add_argument("--rope-length", type=float, default=0.6, metavar="M",
                      help="Total rope length [m]")
    rope.add_argument("--rope-diameter", type=float, default=0.01, metavar="M",
                      help="Rope diameter [m]")
    rope.add_argument("--rope-mass", type=float, default=0.1, metavar="KG",
                      help="Total rope mass [kg]")
    rope.add_argument("--youngs-modulus", type=float, default=1e9, metavar="PA",
                      help="Young's modulus E of the rope fibre material [Pa] (solid nylon ~1e9)")
    rope.add_argument("--fill-factor", type=float, default=0.3, metavar="PHI",
                      help="Cross-section fill factor φ for twisted/braided rope (0–1). "
                           "I_eff = I_solid * φ. Typical nylon rope: 0.3–0.5")
    rope.add_argument("--poissons-ratio", type=float, default=0.35, metavar="NU",
                      help="Poisson's ratio ν of the rope material")
    rope.add_argument("--damping-ratio", type=float, default=0.3, metavar="ZETA",
                      help="Target damping ratio ζ for the per-joint angular drive "
                           "(0 = undamped, 1 = critically damped)")

    # ── simulation parameters ──────────────────────────────────────────────────
    sim = p.add_argument_group("simulation")
    sim.add_argument("--segments", type=int, default=25,
                     help="Number of rigid-body segments")
    sim.add_argument("--swing-limit", type=float, default=60.0, metavar="DEG",
                     help="Max joint swing angle per segment [deg]")
    sim.add_argument("--anchor-height", type=float, default=0.8, metavar="M",
                     help="Height of the fixed anchor point [m]")
    sim.add_argument("--dt", type=float, default=1 / 60.0, metavar="S",
                     help="Physics timestep [s]")
    sim.add_argument("--duration", type=float, default=5.0, metavar="S",
                     help="Simulation duration (headless only) [s]")

    # ── anchor motion ──────────────────────────────────────────────────────────
    motion = p.add_argument_group("anchor motion")
    motion.add_argument("--circle-radius", type=float, default=0.0, metavar="M",
                        help="Radius of anchor circular path; 0 = static [m]")
    motion.add_argument("--circle-period", type=float, default=3.0, metavar="S",
                        help="Time for one full revolution [s]")

    # ── geometry / initial condition ──────────────────────────────────────────
    geom = p.add_argument_group("geometry")
    geom.add_argument("--horizontal", action="store_true", default=False,
                      help="Build rope horizontally along +X (cantilever test)")
    geom.add_argument("--tip-offset-x", type=float, default=0.0, metavar="M",
                      help="After reset, nudge tip segment by this Δx for perturbation tests")
    geom.add_argument("--log-every", type=int, default=60, metavar="N",
                      help="Log summary state every N steps")
    geom.add_argument("--tip-trace", action="store_true", default=False,
                      help="Log tip position every step (for oscillation/period analysis)")
    geom.add_argument("--segment-csv", type=str, default="", metavar="PATH",
                      help="Write all segment positions (t, seg, x, y, z) to CSV")

    # ── recording ─────────────────────────────────────────────────────────────
    rec = p.add_argument_group("recording")
    rec.add_argument("--record", action="store_true", default=False,
                     help="Record simulation to MP4 (forces headless)")
    rec.add_argument("--fps", type=int, default=30, metavar="N")
    rec.add_argument("--width", type=int, default=1280, metavar="PX")
    rec.add_argument("--height", type=int, default=720, metavar="PX")
    rec.add_argument("--output", type=str, default="",
                     help="Output MP4 path (default: debug/<timestamp>_hang_rope.mp4)")

    return p


def main() -> None:
    # parse_known_args: Isaac Sim's python.sh may inject extra flags
    args, _ = _build_parser().parse_known_args()

    if args.record:
        args.headless = True

    # SimulationApp MUST be created before any other Isaac Sim / pxr imports
    from isaacsim import SimulationApp

    simulation_app = SimulationApp({"headless": args.headless})

    from isaacsim.core.api import World
    from pxr import UsdGeom

    from rope_sim.rope_builder import RopeBuilder, RopeConfig
    from rope_sim.sim_utils import clamp_dt, compute_joint_drive

    import carb

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
        label="rope",
    )
    args.dt = dt

    rendering_dt = (1.0 / args.fps) if args.record else (1.0 / 60.0)
    world = World(
        physics_dt=dt,
        rendering_dt=rendering_dt,
        stage_units_in_meters=1.0,
    )

    stage = simulation_app.context.get_stage()

    if args.record:
        from rope_sim.scene_utils import add_default_lighting, add_invisible_ground
        add_invisible_ground(stage)
        add_default_lighting(stage)
    else:
        world.scene.add_default_ground_plane()

    UsdGeom.Xform.Define(stage, "/World/Rope")

    k_bend_si = k_bend / (math.pi / 180.0)  # SI value for display [N·m/rad]
    carb.log_warn(
        f"[rope] material: E={args.youngs_modulus:.3e} Pa, nu={args.poissons_ratio:.2f}, "
        f"zeta={args.damping_ratio:.2f} -> "
        f"k_bend={k_bend_si:.4e} N·m/rad (USD={k_bend:.4e} N·m/deg), "
        f"c_damp={c_damp:.4e} N·m·s/deg, dt={dt:.6f}s"
    )

    cfg = RopeConfig(
        length=args.rope_length,
        diameter=args.rope_diameter,
        mass=args.rope_mass,
        segments=args.segments,
        swing_limit_deg=args.swing_limit,
        anchor_height=args.anchor_height,
        joint_stiffness=k_bend,
        joint_damping=c_damp,
        horizontal=args.horizontal,
    )
    builder = RopeBuilder(cfg, stage)
    builder.build()

    if args.record:
        from pxr import Gf, UsdGeom as _UG
        from rope_sim.camera_utils import make_camera

        circle = args.circle_radius > 0.0
        seg_length = args.rope_length / args.segments

        # Apply circle start offset BEFORE make_camera (which calls world.reset()).
        # This matches the working record_rope.py approach.
        if circle:
            x0 = args.circle_radius
            for prim in builder.segment_prims:
                t_op = next(
                    op for op in _UG.Xformable(prim).GetOrderedXformOps()
                    if op.GetOpType() == _UG.XformOp.TypeTranslate
                )
                cur = t_op.Get()
                t_op.Set(Gf.Vec3d(cur[0] + x0, cur[1], cur[2]))

            omega = 2.0 * math.pi / args.circle_period
            anchor_center_z = args.anchor_height - seg_length / 2.0
            _anchor_translate_op = next(
                op for op in _UG.Xformable(builder.segment_prims[0]).GetOrderedXformOps()
                if op.GetOpType() == _UG.XformOp.TypeTranslate
            )

            def _update_anchor(t: float) -> None:
                x = args.circle_radius * math.cos(omega * t)
                y = args.circle_radius * math.sin(omega * t)
                _anchor_translate_op.Set(Gf.Vec3d(x, y, anchor_center_z))

            world.add_physics_callback(
                "anchor_circle", lambda _: _update_anchor(world.current_time)
            )
            carb.log_warn(
                f"[rope] circular anchor: R={args.circle_radius}m, T={args.circle_period}s, "
                f"omega={omega:.3f} rad/s"
            )

        if circle:
            cam_pos = [4.5, 0.0, 1.0]
            cam_target = [0.0, 0.0, 0.5]
        else:
            cam_pos = [3.5, 0.0, 1.2]
            cam_target = [0.0, 0.0, 0.4]

        # make_camera calls world.reset() + 15 warmup steps internally.
        # Callback is already registered, so warmup runs with correct anchor motion.
        camera = make_camera(
            world,
            prim_path="/World/RecordCam",
            position=cam_pos,
            target=cam_target,
            fps=args.fps,
            resolution=(args.width, args.height),
        )
    else:
        # Shift segments to circle start position before reset (non-record path)
        if args.circle_radius > 0.0 and not args.horizontal:
            from pxr import Gf, UsdGeom as _UG
            x0 = args.circle_radius
            for prim in builder.segment_prims:
                t_op = next(
                    op for op in _UG.Xformable(prim).GetOrderedXformOps()
                    if op.GetOpType() == _UG.XformOp.TypeTranslate
                )
                cur = t_op.Get()
                t_op.Set(Gf.Vec3d(cur[0] + x0, cur[1], cur[2]))
        world.reset()
        camera = None

    # Apply a small lateral offset to the tip segment for perturbation tests.
    if abs(args.tip_offset_x) > 0.0:
        from pxr import Gf, UsdGeom
        tip_prim = builder.segment_prims[-1]
        xform_ops = UsdGeom.Xformable(tip_prim).GetOrderedXformOps()
        translate_op = next(
            op for op in xform_ops if op.GetOpType() == UsdGeom.XformOp.TypeTranslate
        )
        current = translate_op.Get()
        translate_op.Set(
            Gf.Vec3d(current[0] + args.tip_offset_x, current[1], current[2])
        )
        carb.log_warn(
            f"[rope] tip offset applied: Δx={args.tip_offset_x:+.4f} m "
            f"(tip now at {translate_op.Get()})"
        )

    if args.record:
        _run_record(simulation_app, world, builder, camera, args)
    else:
        _run(simulation_app, world, builder, args)

    simulation_app.close()


def _run_record(simulation_app, world, builder, camera, args) -> None:
    import time

    import carb
    import numpy as np

    from rope_sim.video_utils import default_output_path, encode_mp4

    circle = args.circle_radius > 0.0
    dt = args.dt

    capture_dt = 1.0 / args.fps
    steps_per_frame = max(1, int(round(capture_dt / dt)))
    num_steps = int(args.duration / dt)
    expected_frames = num_steps // steps_per_frame

    out_path = Path(args.output) if args.output else default_output_path(
        f"_hang_rope_circle_r{args.circle_radius:.2f}" if circle else "_hang_rope"
    )

    carb.log_warn(
        f"[rope] recording: {num_steps} steps, every {steps_per_frame} → "
        f"~{expected_frames} frames @ {args.fps}fps → {args.duration:.1f}s"
    )
    carb.log_warn(f"[rope] output: {out_path}")

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
            carb.log_warn(
                f"[rope] sim={world.current_time:.1f}s  wall={time.time()-wall_start:.1f}s  "
                f"frames={len(frames)}"
            )

    carb.log_warn(f"[rope] done: {len(frames)} frames in {time.time()-wall_start:.1f}s")

    if frames:
        carb.log_warn(f"[rope] encoding {len(frames)} frames ...")
        encode_mp4(frames, out_path, args.fps)
        carb.log_warn(f"[rope] saved → {out_path}")
    else:
        carb.log_warn("[rope] no frames captured — skipping encode")


def _run(simulation_app, world, builder, args) -> None:
    import csv
    import math

    import carb
    import numpy as np
    from omni.isaac.core.prims import RigidPrimView

    seg_mass = args.rope_mass / args.segments
    seg_length = args.rope_length / args.segments

    # RigidPrimViews give direct PhysX reads/writes — avoids the USD stale-read
    # problem that occurs when render=False skips the PhysX→USD sync.
    seg_paths = [prim.GetPath().pathString for prim in builder.segment_prims]
    all_segs_view = RigidPrimView(prim_paths_expr=seg_paths, reset_xform_properties=False)
    all_segs_view.initialize()

    def _get_all_positions() -> np.ndarray:
        pos, _ = all_segs_view.get_world_poses(usd=False)
        return pos  # (n_segs, 3) float32, directly from PhysX

    def _tip_pos() -> np.ndarray:
        return _get_all_positions()[-1]

    # Anchor circular motion setup
    circle = args.circle_radius > 0.0
    omega = 0.0
    anchor_center_z = args.anchor_height - seg_length / 2.0
    if circle:
        omega = 2.0 * math.pi / args.circle_period
        carb.log_warn(
            f"[rope] circular anchor: R={args.circle_radius}m, T={args.circle_period}s, "
            f"omega={omega:.3f} rad/s"
        )

    # Anchor update via USD TranslateOp — NOT RigidPrimView.set_world_poses().
    # During simulation set_world_poses() ignores `usd` and calls _physics_view.set_transforms()
    # (PhysX only), leaving Fabric un-updated → ghost artefact. Writing the USD TranslateOp
    # is propagated to Fabric by Isaac Sim's USD-Fabric sync each step.
    _anchor_translate_op = None
    if circle:
        from pxr import Gf as _Gf, UsdGeom as _UsdGeom
        _anchor_prim = builder.segment_prims[0]
        _anchor_translate_op = next(
            op for op in _UsdGeom.Xformable(_anchor_prim).GetOrderedXformOps()
            if op.GetOpType() == _UsdGeom.XformOp.TypeTranslate
        )

    def _update_anchor(t: float) -> None:
        if not circle:
            return
        x = args.circle_radius * math.cos(omega * t)
        y = args.circle_radius * math.sin(omega * t)
        _anchor_translate_op.Set(_Gf.Vec3d(x, y, anchor_center_z))

    if circle:
        # Register as physics callback so it fires inside every Kit substep
        # (not just once per Python loop iteration which skips ~166 of 167 substeps).
        world.add_physics_callback("anchor_circle", lambda _: _update_anchor(world.current_time))

    def _compute_anchor_wrench() -> tuple[np.ndarray, np.ndarray]:
        """Compute anchor reaction force & torque analytically (Newton's 2nd law).

        Assumes steady-state: vertical accelerations ≈ 0.
        Horizontal centripetal accelerations a_i = -ω² * (x_i, y_i) at each segment.

        F_anchor = sum_i(m_i * a_i) + (0, 0, m_total * g)   [Newton's 2nd for system]
        T_anchor = sum_i(r_i × m_i * (a_i + g_vec_negated))  [moment balance about anchor joint]

        The anchor joint is at the bottom of Segment_000 (= top of Segment_001).
        """
        positions = _get_all_positions()  # (n_segs, 3), from PhysX directly
        joint_pos = positions[0] + np.array([0.0, 0.0, -seg_length / 2.0])

        F = np.array([0.0, 0.0, args.rope_mass * _G])
        T = np.zeros(3)

        for p in positions:
            r = p - joint_pos
            if circle:
                a = np.array([-omega**2 * p[0], -omega**2 * p[1], 0.0])
                F += seg_mass * a
                T += np.cross(r, seg_mass * a)
            T += np.cross(r, np.array([0.0, 0.0, seg_mass * _G]))

        return F, T

    def _expected_Fz() -> float:
        return args.rope_mass * _G

    def _expected_F_horizontal() -> float:
        """Minimum centripetal force if rope centre-of-mass is exactly at anchor radius."""
        if not circle:
            return 0.0
        return args.rope_mass * omega**2 * args.circle_radius

    def _log_state(elapsed: float) -> None:
        tip_pos = _tip_pos()
        F, T = _compute_anchor_wrench()
        F_h = math.hypot(F[0], F[1])

        if circle:
            F_h_min = _expected_F_horizontal()
            carb.log_warn(
                f"[rope] t={elapsed:5.2f}s  "
                f"tip=({tip_pos[0]:+.4f}, {tip_pos[1]:+.4f}, {tip_pos[2]:+.4f}) m  "
                f"F=({F[0]:+.3f}, {F[1]:+.3f}, {F[2]:+.3f}) N "
                f"|Fxy|={F_h:.3f} [expect>={F_h_min:.3f}]  "
                f"T=({T[0]:+.3f}, {T[1]:+.3f}, {T[2]:+.3f}) Nm"
            )
        else:
            Fz_exp = _expected_Fz()
            carb.log_warn(
                f"[rope] t={elapsed:5.2f}s  "
                f"tip=({tip_pos[0]:+.4f}, {tip_pos[1]:+.4f}, {tip_pos[2]:+.4f}) m  "
                f"F=({F[0]:+.3f}, {F[1]:+.3f}, {F[2]:+.3f}) N "
                f"[Fz expect={Fz_exp:.3f}]  "
                f"T=({T[0]:+.3f}, {T[1]:+.3f}, {T[2]:+.3f}) Nm [expect≈0]"
            )

    def _log_tip(elapsed: float) -> None:
        p = _tip_pos()
        carb.log_warn(
            f"[tip] t={elapsed:.6f}  x={p[0]:+.6f}  y={p[1]:+.6f}  z={p[2]:+.6f}"
        )

    # CSV recording setup
    _csv_file = None
    _csv_writer = None
    if args.segment_csv:
        _csv_file = open(args.segment_csv, "w", newline="")
        _csv_writer = csv.writer(_csv_file)
        _csv_writer.writerow(["t", "seg", "x", "y", "z"])
        carb.log_warn(f"[rope] recording segment positions to {args.segment_csv}")

    def _record_segments(t: float) -> None:
        if _csv_writer is None:
            return
        positions = _get_all_positions()
        for idx, p in enumerate(positions):
            _csv_writer.writerow([f"{t:.6f}", idx, f"{p[0]:.6f}", f"{p[1]:.6f}", f"{p[2]:.6f}"])

    log_every = max(1, args.log_every)
    _last_log_t = -1.0

    try:
        if args.headless:
            num_steps = int(args.duration / args.dt)
            carb.log_warn(f"[rope] running {num_steps} steps ({args.duration:.1f}s) headless")
            for step in range(num_steps):
                _update_anchor(world.current_time)
                world.step(render=False)
                t = world.current_time
                if args.tip_trace:
                    _log_tip(t)
                if step % log_every == 0:
                    _log_state(t)
                    _record_segments(t)

            t = world.current_time
            _log_state(t)
            _record_segments(t)
        else:
            carb.log_warn("[rope] running with GUI — close the window to exit")
            while simulation_app.is_running():
                world.step(render=True)
                t = world.current_time
                if args.tip_trace:
                    _log_tip(t)
                log_interval = log_every * args.dt
                if t - _last_log_t >= log_interval:
                    _log_state(t)
                    _record_segments(t)
                    _last_log_t = t
    finally:
        if _csv_file is not None:
            _csv_file.close()
            carb.log_warn(f"[rope] segment CSV closed: {args.segment_csv}")


if __name__ == "__main__":
    main()
