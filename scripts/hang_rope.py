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

_G = 9.81  # m/s²


def _compute_joint_drive(
    youngs_modulus: float,
    poissons_ratio: float,
    rope_diameter: float,
    rope_length: float,
    rope_mass: float,
    segments: int,
    damping_ratio: float = 0.3,
) -> tuple[float, float]:
    """Compute D6 joint drive stiffness and damping for a solid circular DLO.

    Uses Euler-Bernoulli beam theory: k_bend = E · I / L_seg (SI, N·m/rad).

    The USD PhysX DriveAPI for angular drives is documented to measure angle
    in DEGREES (see PhysicsDriveAPI schema: "stiffness … mass·DIST²/degrees/s²",
    "targetPosition … if angular drive: degrees"). Empirically a single D6
    drive with stiffness attr S produces a restoring torque τ = S·(180/π)·θ
    for θ in radians, i.e. the effective SI stiffness is S · 180/π. To get an
    SI-correct k_bend we therefore must write   stiffness_attr = k_bend · π/180.
    The same conversion applies to the damping coefficient.
    """
    r = rope_diameter / 2.0
    seg_len = rope_length / segments
    m_seg = rope_mass / segments

    I = math.pi * r**4 / 4.0          # 2nd moment of area [m⁴]
    k_bend = youngs_modulus * I / seg_len  # SI bending stiffness [N·m/rad]

    # Rotational inertia of a segment swinging about its joint endpoint:
    # uniform rod about end, I = m · L_seg² / 3. This matches the small-angle
    # oscillation mode we want to damp.
    I_rot = m_seg * seg_len * seg_len / 3.0
    omega_n = math.sqrt(k_bend / max(I_rot, 1e-12))
    c_damp = 2.0 * damping_ratio * I_rot * omega_n   # SI damping [N·m·s/rad]

    # Reference: shear modulus / polar moment, kept for documentation purposes.
    _ = youngs_modulus / (2.0 * (1.0 + poissons_ratio))  # G [Pa]
    _ = math.pi * r**4 / 2.0  # J [m⁴]

    # Convert SI (per-rad) values to USD DriveAPI units (per-degree).
    DEG_PER_RAD = math.pi / 180.0
    return k_bend * DEG_PER_RAD, c_damp * DEG_PER_RAD


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
                      help="Young's modulus E of the rope material [Pa] (nylon ~1e9)")
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

    return p


def main() -> None:
    # parse_known_args: Isaac Sim's python.sh may inject extra flags
    args, _ = _build_parser().parse_known_args()

    # SimulationApp MUST be created before any other Isaac Sim / pxr imports
    from isaacsim import SimulationApp

    simulation_app = SimulationApp({"headless": args.headless})

    from isaacsim.core.api import World
    from pxr import UsdGeom

    from rope_sim.rope_builder import RopeBuilder, RopeConfig

    import carb

    k_bend, c_damp = _compute_joint_drive(
        youngs_modulus=args.youngs_modulus,
        poissons_ratio=args.poissons_ratio,
        rope_diameter=args.rope_diameter,
        rope_length=args.rope_length,
        rope_mass=args.rope_mass,
        segments=args.segments,
        damping_ratio=args.damping_ratio,
    )

    # Auto-adjust dt for numerical stability of the joint angular drive.
    # Stable explicit-ish integration requires omega_n * dt < ~1; use 0.5 (conservative).
    # The relevant rotational inertia is the segment swinging about its joint endpoint,
    # i.e. a uniform rod of length L_seg about one end: I_rot = m·L_seg²/3.
    r = args.rope_diameter / 2.0
    I_area = math.pi * r**4 / 4.0
    L_seg = args.rope_length / args.segments
    m_seg = args.rope_mass / args.segments
    I_rot = max(m_seg * L_seg * L_seg / 3.0, 1e-12)
    omega_n = math.sqrt((args.youngs_modulus * I_area / L_seg) / I_rot)

    dt_max = 0.5 / omega_n
    dt = min(args.dt, dt_max)
    if dt < args.dt:
        carb.log_warn(
            f"[rope] dt reduced from {args.dt:.4f}s to {dt:.6f}s for stability "
            f"(omega_n={omega_n:.1f} rad/s, dt_max={dt_max:.6f}s)"
        )
    # Use the (possibly reduced) dt for the rest of the run.
    args.dt = dt

    world = World(
        physics_dt=dt,
        rendering_dt=dt,
        stage_units_in_meters=1.0,
    )
    world.scene.add_default_ground_plane()

    stage = simulation_app.context.get_stage()
    UsdGeom.Xform.Define(stage, "/World/Rope")

    k_bend_si = k_bend / (math.pi / 180.0)  # SI value for display [N·m/rad]
    carb.log_warn(
        f"[rope] material: E={args.youngs_modulus:.3e} Pa, nu={args.poissons_ratio:.2f}, "
        f"zeta={args.damping_ratio:.2f} -> "
        f"k_bend={k_bend_si:.4e} N·m/rad (USD={k_bend:.4e} N·m/deg), "
        f"c_damp={c_damp:.4e} N·m·s/deg, "
        f"omega_n={omega_n:.1f} rad/s, dt={dt:.6f}s (dt_max={dt_max:.6f}s)"
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

    # Shift all segments so initial position matches the t=0 circle point (R, 0, z).
    # Without this, the first physics step teleports seg0 by R=circle_radius, sending
    # a shock through the rope that causes large transient oscillations.
    if args.circle_radius > 0.0 and not args.horizontal:
        from pxr import Gf, UsdGeom as _UG
        x0 = args.circle_radius  # cos(0) = 1
        for prim in builder.segment_prims:
            t_op = next(
                op for op in _UG.Xformable(prim).GetOrderedXformOps()
                if op.GetOpType() == _UG.XformOp.TypeTranslate
            )
            cur = t_op.Get()
            t_op.Set(Gf.Vec3d(cur[0] + x0, cur[1], cur[2]))

    world.reset()

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

    _run(simulation_app, world, builder, args)

    simulation_app.close()


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
    anchor_view = None

    if circle:
        # Separate view for seg0 so we can set its kinematic target each step.
        # set_world_poses(usd=False) writes directly to the PhysX kinematic target,
        # which gives PhysX velocity information (no infinite-velocity teleport).
        anchor_view = RigidPrimView(prim_paths_expr=seg_paths[0], reset_xform_properties=False)
        anchor_view.initialize()
        omega = 2.0 * math.pi / args.circle_period
        carb.log_warn(
            f"[rope] circular anchor: R={args.circle_radius}m, T={args.circle_period}s, "
            f"omega={omega:.3f} rad/s"
        )

    def _update_anchor(t: float) -> None:
        if not circle:
            return
        x = args.circle_radius * math.cos(omega * t)
        y = args.circle_radius * math.sin(omega * t)
        anchor_view.set_world_poses(
            positions=np.array([[x, y, anchor_center_z]], dtype=np.float32),
            usd=True,
        )

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
    try:
        if args.headless:
            num_steps = int(args.duration / args.dt)
            carb.log_warn(f"[rope] running {num_steps} steps ({args.duration:.1f}s) headless")
            for step in range(num_steps):
                _update_anchor(step * args.dt)
                world.step(render=False)
                if args.tip_trace:
                    _log_tip(step * args.dt)
                if step % log_every == 0:
                    _log_state(step * args.dt)
                    _record_segments(step * args.dt)

            _log_state(num_steps * args.dt)
            _record_segments(num_steps * args.dt)
        else:
            carb.log_warn("[rope] running with GUI — close the window to exit")
            step = 0
            while simulation_app.is_running():
                _update_anchor(step * args.dt)
                world.step(render=True)
                if args.tip_trace:
                    _log_tip(step * args.dt)
                if step % log_every == 0:
                    _log_state(step * args.dt)
                    _record_segments(step * args.dt)
                step += 1
    finally:
        if _csv_file is not None:
            _csv_file.close()
            carb.log_warn(f"[rope] segment CSV closed: {args.segment_csv}")


if __name__ == "__main__":
    main()
