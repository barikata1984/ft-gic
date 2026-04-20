"""Quick camera-placement checker: renders a few frames at key swing angles and saves as PNG.

Usage:
    /isaac-sim/python.sh scripts/_check_camera.py [--cam-dist D] [--cam-z Z]
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def _compute_joint_drive(rope_diameter, rope_length, rope_mass, segments,
                          youngs_modulus=1e9, fill_factor=0.3, damping_ratio=0.3):
    r = rope_diameter / 2.0
    seg_len = rope_length / segments
    m_seg = rope_mass / segments
    I_eff = math.pi * r**4 / 4.0 * fill_factor
    k_bend = youngs_modulus * I_eff / seg_len
    I_rot = m_seg * seg_len * seg_len / 3.0
    omega_n = math.sqrt(k_bend / max(I_rot, 1e-12))
    c_damp = 2.0 * damping_ratio * I_rot * omega_n
    DEG = math.pi / 180.0
    return k_bend * DEG, c_damp * DEG


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cam-dist", type=float, default=2.0)
    p.add_argument("--cam-z",   type=float, default=0.9)
    p.add_argument("--cam-y",   type=float, default=-0.5)
    p.add_argument("--target-z", type=float, default=0.4)
    p.add_argument("--swing-amplitude", type=float, default=math.pi / 4)
    p.add_argument("--width",  type=int, default=1280)
    p.add_argument("--height", type=int, default=720)
    args, _ = p.parse_known_args()

    from isaacsim import SimulationApp
    app = SimulationApp({"headless": True, "renderer": "RayTracedLighting"})

    import carb
    import cv2
    import numpy as np
    from isaacsim.core.api import World
    from isaacsim.sensors.camera import Camera
    from pxr import Gf, UsdGeom, UsdLux, UsdPhysics

    from rope_sim.rope_builder import RopeBuilder, RopeConfig

    rope_length = 0.6
    anchor_height = rope_length + 0.1   # 0.7 m
    segments = 25
    k_bend, c_damp = _compute_joint_drive(0.01, rope_length, 0.1, segments)

    L_seg = rope_length / segments
    m_seg = 0.1 / segments
    I_eff = math.pi * 0.005**4 / 4.0 * 0.3
    omega_n = math.sqrt((1e9 * I_eff / L_seg) / max(m_seg * L_seg**2 / 3.0, 1e-12))
    dt = min(1/60, 0.5 / omega_n)
    carb.log_warn(f"[check] dt={dt:.6f}s  omega_n={omega_n:.1f} rad/s")

    world = World(physics_dt=dt, rendering_dt=1/30, stage_units_in_meters=1.0)
    stage = app.context.get_stage()

    # ── Minimal ground: physics plane only, no visual wall ──────────────────
    # Instead of add_default_ground_plane() which adds a decorative vertical panel,
    # define a pure collision plane at z=0.
    ground_path = "/World/GroundPlane"
    UsdGeom.Xform.Define(stage, ground_path)
    ground_prim = stage.GetPrimAtPath(ground_path)
    UsdPhysics.CollisionAPI.Apply(ground_prim)
    plane_geom = UsdGeom.Plane.Define(stage, ground_path + "/CollisionPlane")
    plane_geom.CreateAxisAttr("Z")
    plane_geom.CreatePurposeAttr(UsdGeom.Tokens.guide)   # invisible
    UsdPhysics.CollisionAPI.Apply(stage.GetPrimAtPath(ground_path + "/CollisionPlane"))

    UsdGeom.Xform.Define(stage, "/World/Rope")

    # ── Lighting ─────────────────────────────────────────────────────────────
    dome = UsdLux.DomeLight.Define(stage, "/World/DomeLight")
    dome.CreateIntensityAttr(800.0)
    dist_light = UsdLux.DistantLight.Define(stage, "/World/KeyLight")
    dist_light.CreateIntensityAttr(4000.0)
    dist_light.CreateAngleAttr(0.53)
    UsdGeom.Xformable(dist_light.GetPrim()).AddRotateXYZOp().Set(Gf.Vec3f(-60.0, 30.0, 0.0))

    # ── Rope ─────────────────────────────────────────────────────────────────
    cfg = RopeConfig(length=rope_length, diameter=0.01, mass=0.1, segments=segments,
                     swing_limit_deg=60.0, anchor_height=anchor_height,
                     joint_stiffness=k_bend, joint_damping=c_damp)
    builder = RopeBuilder(cfg, stage)
    builder.build()

    # ── Camera ───────────────────────────────────────────────────────────────
    cam_pos    = np.array([args.cam_dist, args.cam_y, args.cam_z])
    cam_target = np.array([0.0, 0.0, args.target_z])

    # Look-at in Isaac Sim World convention (+X forward, +Z up).
    fwd = cam_target - cam_pos;  fwd /= np.linalg.norm(fwd)
    world_up = np.array([0.0, 0.0, 1.0])
    right = np.cross(fwd, world_up);  right /= np.linalg.norm(right)
    up    = np.cross(right, fwd)
    R = np.stack([fwd, -right, up], axis=1)
    tr = R[0,0]+R[1,1]+R[2,2]
    if tr > 0:
        s=0.5/math.sqrt(tr+1); qw=0.25/s; qx=(R[2,1]-R[1,2])*s; qy=(R[0,2]-R[2,0])*s; qz=(R[1,0]-R[0,1])*s
    elif R[0,0]>R[1,1] and R[0,0]>R[2,2]:
        s=2*math.sqrt(1+R[0,0]-R[1,1]-R[2,2]); qw=(R[2,1]-R[1,2])/s; qx=0.25*s; qy=(R[0,1]+R[1,0])/s; qz=(R[0,2]+R[2,0])/s
    elif R[1,1]>R[2,2]:
        s=2*math.sqrt(1+R[1,1]-R[0,0]-R[2,2]); qw=(R[0,2]-R[2,0])/s; qx=(R[0,1]+R[1,0])/s; qy=0.25*s; qz=(R[1,2]+R[2,1])/s
    else:
        s=2*math.sqrt(1+R[2,2]-R[0,0]-R[1,1]); qw=(R[1,0]-R[0,1])/s; qx=(R[0,2]+R[2,0])/s; qy=(R[1,2]+R[2,1])/s; qz=0.25*s
    cam_orientation = np.array([qw, qx, qy, qz], dtype=float)
    carb.log_warn(f"[check] cam_pos={cam_pos}  fwd={fwd}  quat={cam_orientation}")

    camera = Camera(prim_path="/World/RecordCam",
                    position=cam_pos,
                    frequency=30,
                    resolution=(args.width, args.height))
    world.reset()
    camera.initialize()
    camera.set_world_pose(position=cam_pos, orientation=cam_orientation, camera_axes="world")

    # ── Anchor rotation op ───────────────────────────────────────────────────
    _rot_x_op = UsdGeom.Xformable(builder.segment_prims[0]).AddRotateXOp()
    amp_deg = math.degrees(args.swing_amplitude)

    debug_dir = Path(__file__).resolve().parents[1] / "debug"
    debug_dir.mkdir(exist_ok=True)

    # Warm up camera (~15 renders needed before get_rgba() returns non-None)
    for _ in range(15):
        world.step(render=True)

    # Settle for 1.0 s at each angle before snapping
    settle_steps = max(1, int(1.0 / dt))
    carb.log_warn(f"[check] settle_steps={settle_steps} per pose")

    snap_angles_deg = [0.0, amp_deg, -amp_deg]
    snap_names      = ["neutral", "plus45", "minus45"]

    for idx, (angle_deg, name) in enumerate(zip(snap_angles_deg, snap_names)):
        _rot_x_op.Set(angle_deg)
        for _ in range(settle_steps):
            world.step(render=False)
        world.step(render=True)
        rgba = camera.get_rgba()
        if rgba is not None and rgba.size > 0:
            img = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2BGR)
            tag = f"d{args.cam_dist:.1f}_y{args.cam_y:.1f}_z{args.cam_z:.1f}_tz{args.target_z:.1f}"
            fname = debug_dir / f"_check_{idx:02d}_{name}_{tag}.png"
            cv2.imwrite(str(fname), img)
            carb.log_warn(f"[check] saved {fname}")
        else:
            carb.log_warn(f"[check] no frame at pose {name}")

    app.close()


if __name__ == "__main__":
    main()
