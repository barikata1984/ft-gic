"""Empirically measure PhysX D6 angular-drive stiffness calibration.

Builds a minimal 2-segment rope (segment 0 kinematic, segment 1 free), disables
gravity, applies a small initial angular offset to segment 1, and records the
resulting free oscillation. The oscillation period gives the effective
rotational stiffness:

    ω² = k_effective / I_end
    k_effective = ω² · I_end    with  I_end = m·L²/3 + m·r²/4

This script prints the measured period, the derived k_effective, the
theoretical k_bend = E·I_area/L_seg, and the calibration ratio
C = k_effective / k_bend. The hypothesis being tested is that the USD Physics
DriveAPI interprets the stiffness attribute in units of N·m / degree (not rad),
so C should approximately equal 180/π ≈ 57.296.

Run:
    PYTHONPATH=/tmp/rope-rigid/src /isaac-sim/python.sh \
        scripts/calibrate_drive.py --stiffness 1.6357 --duration 1.0

Optional flags let you pass the raw stiffness directly (bypassing the
analytical formula) or try the "acceleration" drive type.
"""
from __future__ import annotations

import argparse
import math


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="D6 drive stiffness calibration test")
    p.add_argument("--youngs-modulus", type=float, default=1.0e9)
    p.add_argument("--poissons-ratio", type=float, default=0.35)
    p.add_argument("--rope-length", type=float, default=0.6)
    p.add_argument("--rope-diameter", type=float, default=0.01)
    p.add_argument("--rope-mass", type=float, default=0.1)
    p.add_argument("--segments", type=int, default=2)
    p.add_argument("--duration", type=float, default=1.0)
    p.add_argument("--initial-angle-deg", type=float, default=2.0,
                   help="Initial angle of the free segment about the joint [deg]")
    p.add_argument("--stiffness-override", type=float, default=None,
                   help="If set, use this drive stiffness directly instead of E·I/L_seg")
    p.add_argument("--drive-type", type=str, default="force",
                   choices=["force", "acceleration"])
    p.add_argument("--dt-safety", type=float, default=0.25,
                   help="Fraction of 1/ω_n used as physics dt")
    p.add_argument("--headless", action="store_true", default=True)
    return p


def main() -> None:
    args, _ = _build_parser().parse_known_args()

    from isaacsim import SimulationApp

    simulation_app = SimulationApp({"headless": True})

    import carb
    import numpy as np
    from isaacsim.core.api import World
    from pxr import Gf, UsdGeom, UsdPhysics

    # ── rope parameters ────────────────────────────────────────────────────
    r = args.rope_diameter / 2.0
    L_seg = args.rope_length / args.segments
    m_seg = args.rope_mass / args.segments
    I_area = math.pi * r**4 / 4.0
    k_bend = args.youngs_modulus * I_area / L_seg  # N·m/rad (SI)

    # Rotational inertia of a capsule about one end:
    #   uniform rod about end = m·L²/3
    #   plus small r² correction for the capsule body (negligible for thin rope)
    I_end = m_seg * L_seg * L_seg / 3.0 + m_seg * r * r / 4.0
    omega_n_analytic = math.sqrt(k_bend / I_end)
    T_analytic = 2.0 * math.pi / omega_n_analytic

    # Stability: use a conservatively small dt based on the predicted (degrees-based)
    # effective frequency, i.e. ω_eff ≈ sqrt(k_bend·(180/π)/I_end). We pick the
    # smaller of analytic or degree-scaled estimates to be safe.
    omega_eff_upper = omega_n_analytic * math.sqrt(180.0 / math.pi)
    dt = args.dt_safety / max(omega_eff_upper, 1.0)

    stiffness_to_use = args.stiffness_override if args.stiffness_override is not None else k_bend

    carb.log_warn(
        f"[calib] L_seg={L_seg:.4f} m, m_seg={m_seg:.5f} kg, r={r:.4f} m"
    )
    carb.log_warn(
        f"[calib] I_area={I_area:.3e} m^4, I_end={I_end:.3e} kg·m^2"
    )
    carb.log_warn(
        f"[calib] k_bend (E·I/L) = {k_bend:.6e} N·m/rad  (passed as drive stiffness = {stiffness_to_use:.6e})"
    )
    carb.log_warn(
        f"[calib] analytic ω_n = {omega_n_analytic:.3f} rad/s, T = {T_analytic*1000:.3f} ms"
    )
    carb.log_warn(
        f"[calib] dt = {dt*1e6:.2f} µs, duration = {args.duration:.3f} s, drive_type = {args.drive_type}"
    )

    # ── build minimal stage with gravity disabled ──────────────────────────
    world = World(physics_dt=dt, rendering_dt=dt, stage_units_in_meters=1.0)
    physics_ctx = world.get_physics_context()
    physics_ctx.set_gravity(0.0)  # gravity OFF for a clean oscillation test

    stage = simulation_app.context.get_stage()
    UsdGeom.Xform.Define(stage, "/World/Rope")

    # build segments (two capsules along +X)
    segments = []
    cyl_height = max(0.0, L_seg - 2.0 * r)
    for i in range(args.segments):
        path = f"/World/Rope/Segment_{i:03d}"
        geom = UsdGeom.Capsule.Define(stage, path)
        geom.CreateRadiusAttr(r)
        geom.CreateHeightAttr(cyl_height)
        geom.CreateAxisAttr("Z")
        geom.CreateExtentAttr(
            [Gf.Vec3f(-r, -r, -L_seg / 2.0), Gf.Vec3f(r, r, L_seg / 2.0)]
        )
        # capsule aligned with world +X by rotating about +Y by -90°
        geom.AddTranslateOp().Set(Gf.Vec3d(L_seg * (i + 0.5), 0.0, 0.0))
        geom.AddRotateYOp().Set(-90.0)

        prim = stage.GetPrimAtPath(path)
        UsdPhysics.CollisionAPI.Apply(prim)
        rb_api = UsdPhysics.RigidBodyAPI.Apply(prim)
        if i == 0:
            rb_api.CreateKinematicEnabledAttr(True)
        mass_api = UsdPhysics.MassAPI.Apply(prim)
        mass_api.CreateMassAttr(m_seg)
        segments.append(prim)

    # D6 joints between adjacent segments (same style as rope_builder)
    for i in range(args.segments - 1):
        jpath = f"/World/Rope/Joint_{i:03d}"
        joint = UsdPhysics.Joint.Define(stage, jpath)
        joint_prim = joint.GetPrim()
        joint.CreateBody0Rel().SetTargets([segments[i].GetPath()])
        joint.CreateBody1Rel().SetTargets([segments[i + 1].GetPath()])
        joint.CreateLocalPos0Attr().Set(Gf.Vec3f(0.0, 0.0, -L_seg / 2.0))
        joint.CreateLocalRot0Attr().Set(Gf.Quatf(1.0))
        joint.CreateLocalPos1Attr().Set(Gf.Vec3f(0.0, 0.0, L_seg / 2.0))
        joint.CreateLocalRot1Attr().Set(Gf.Quatf(1.0))
        for dof in ("transX", "transY", "transZ"):
            limit = UsdPhysics.LimitAPI.Apply(joint_prim, dof)
            limit.CreateLowAttr(1.0)
            limit.CreateHighAttr(-1.0)
        for dof in ("rotX", "rotY"):
            drive = UsdPhysics.DriveAPI.Apply(joint_prim, dof)
            drive.CreateTypeAttr(args.drive_type)
            drive.CreateStiffnessAttr(stiffness_to_use)
            drive.CreateDampingAttr(0.0)
            drive.CreateTargetPositionAttr(0.0)
            drive.CreateTargetVelocityAttr(0.0)

    world.reset()

    # Apply initial angular offset: rotate segment 1's position+orientation
    # about the joint between segments 0 and 1 by `initial_angle_deg` about Y axis.
    # Joint position = world end of segment 0 on +X side = (L_seg, 0, 0).
    theta0 = math.radians(args.initial_angle_deg)
    joint_world = np.array([L_seg, 0.0, 0.0])
    # segment 1 centre originally at (1.5·L_seg, 0, 0); after rotation about +Y by theta0
    # (RH rule: +Y rotation sends +X toward -Z), centre becomes
    #   joint + Ry(theta0) · (0.5·L_seg, 0, 0)
    seg1_centre_new = joint_world + np.array([
        0.5 * L_seg * math.cos(theta0),
        0.0,
        -0.5 * L_seg * math.sin(theta0),
    ])

    seg1_prim = segments[1]
    xform = UsdGeom.Xformable(seg1_prim)
    # Rebuild xform ops: translate to new centre, then rotate -90° about Y (align capsule
    # with world +X), then rotate extra theta0 about Y.
    xform.ClearXformOpOrder()
    xform.AddTranslateOp().Set(Gf.Vec3d(*seg1_centre_new))
    xform.AddRotateYOp().Set(-90.0 + math.degrees(theta0))

    carb.log_warn(
        f"[calib] seg1 moved to centre={seg1_centre_new}, theta0={args.initial_angle_deg:.3f} deg"
    )

    # ── simulate and record tip position each step ─────────────────────────
    tip_prim = segments[-1]
    # Tip = world +X end of segment 1 = centre + Ry(theta0)·(L_seg/2, 0, 0)
    # The tip z coordinate directly encodes sin(θ_tot)·L_seg (where θ_tot is the
    # total bend angle of segment 1 about Y relative to +X). We record all three
    # coords and later extract the angle from xz.

    n_steps = int(args.duration / dt)
    cache = UsdGeom.XformCache()
    log_stride = max(1, n_steps // 4000)  # keep ~4k samples

    times = []
    angles = []  # angle of segment 1 about Y (rad), derived from tip-relative-to-joint
    for step in range(n_steps):
        world.step(render=False)
        if step % log_stride == 0:
            cache = UsdGeom.XformCache()
            p_tip = np.array(cache.GetLocalToWorldTransform(tip_prim).ExtractTranslation())
            # tip is at +L_seg/2 along segment 1's local +Z axis (which, for capsule
            # aligned with world X by a −90° Y-rotation, maps to world −X before bend).
            # We measure the bend angle from the centre position instead: centre lies
            # at joint + 0.5·L_seg in direction (cos θ, 0, −sin θ). The world +Z component
            # of (centre - joint)/0.5·L_seg = −sin θ, x component = cos θ, so
            # θ = atan2(-(z_c - z_j), (x_c - x_j)).
            # Use centre (more robust than tip) — for a rigid capsule the two coincide
            # up to a sign, but we compute from prim translate op directly.
            # Simpler: ask USD for the prim's world transform and extract rotation.
            tm = cache.GetLocalToWorldTransform(tip_prim)
            trans = np.array(tm.ExtractTranslation())
            # Angle from joint to centre of seg1
            dx = trans[0] - joint_world[0]
            dz = trans[2] - joint_world[2]
            theta = math.atan2(-dz, dx)
            times.append(step * dt)
            angles.append(theta)

    times_np = np.array(times)
    angles_np = np.array(angles)

    # ── extract oscillation period from zero-crossings ─────────────────────
    # Subtract mean to remove any DC offset.
    a_centred = angles_np - angles_np.mean()
    # find sign changes
    signs = np.sign(a_centred)
    # ignore zeros
    signs[signs == 0] = 1
    crossings = np.where(np.diff(signs) != 0)[0]
    if len(crossings) >= 2:
        # Period = 2 × average gap between consecutive crossings
        gaps = np.diff(times_np[crossings])
        T_meas = 2.0 * float(np.mean(gaps))
    else:
        T_meas = float("nan")

    omega_meas = 2.0 * math.pi / T_meas if T_meas > 0 else float("nan")
    k_eff = (omega_meas ** 2) * I_end if T_meas > 0 else float("nan")

    carb.log_warn(
        f"[calib] zero-crossings detected: {len(crossings)} "
        f"(first 6 at t={times_np[crossings[:6]] if len(crossings) else []})"
    )
    carb.log_warn(
        f"[calib] measured T = {T_meas*1000:.3f} ms,  ω = {omega_meas:.3f} rad/s"
    )
    carb.log_warn(
        f"[calib] analytic T = {T_analytic*1000:.3f} ms,  ω = {omega_n_analytic:.3f} rad/s"
    )
    carb.log_warn(
        f"[calib] k_effective = {k_eff:.4e} N·m/rad  "
        f"(stiffness attr passed = {stiffness_to_use:.4e})"
    )
    if stiffness_to_use > 0 and not math.isnan(k_eff):
        ratio = k_eff / stiffness_to_use
        carb.log_warn(
            f"[calib] ratio k_effective/stiffness_attr = {ratio:.4f}  "
            f"(180/pi = {180.0/math.pi:.4f})"
        )

    # Print ASCII trace of the first 40 samples so we can visually verify oscillation.
    carb.log_warn("[calib] first 40 samples (t [ms], angle [deg]):")
    for t, a in zip(times_np[:40], angles_np[:40]):
        carb.log_warn(f"[calib]   t={t*1000:8.3f}  theta={math.degrees(a):+8.4f}")

    simulation_app.close()


if __name__ == "__main__":
    main()
