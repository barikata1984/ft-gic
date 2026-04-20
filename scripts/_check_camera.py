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
    from pxr import UsdGeom

    from rope_sim.rope_builder import RopeBuilder, RopeConfig
    from rope_sim.scene_utils import add_default_lighting, add_invisible_ground
    from rope_sim.sim_utils import clamp_dt, compute_joint_drive

    rope_length = 0.6
    anchor_height = rope_length + 0.1   # 0.7 m
    segments = 25
    k_bend, c_damp = compute_joint_drive(0.01, rope_length, 0.1, segments)

    dt = clamp_dt(1 / 60, 1e9, 0.01, rope_length, 0.1, segments, label="check")
    carb.log_warn(f"[check] dt={dt:.6f}s")

    world = World(physics_dt=dt, rendering_dt=1/30, stage_units_in_meters=1.0)
    stage = app.context.get_stage()

    add_invisible_ground(stage)
    UsdGeom.Xform.Define(stage, "/World/Rope")
    add_default_lighting(stage)

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
