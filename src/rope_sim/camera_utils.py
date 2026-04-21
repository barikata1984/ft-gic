"""Camera placement utilities for Isaac Sim offscreen recording.

Provides make_camera() which encapsulates the full setup sequence:
  1. look-at quaternion from position + target (world +X forward, +Z up)
  2. Camera prim creation
  3. world.reset() + initialize() + set_world_pose()
  4. warm-up renders so get_rgba() returns valid data immediately after

Usage:
    from rope_sim.camera_utils import make_camera

    cam = make_camera(
        stage, world,
        prim_path="/World/CamFront",
        position=[3.5, 0.0, 1.2],
        target=[0.0, 0.0, 0.4],
        fps=30,
        resolution=(1280, 720),
    )
    # After world.reset() has been called inside make_camera:
    rgba = cam.get_rgba()  # always valid after make_camera returns
"""
from __future__ import annotations

import math

import numpy as np


def _lookat_quaternion(
    position: np.ndarray,
    target: np.ndarray,
    world_up: np.ndarray | None = None,
) -> np.ndarray:
    """Compute look-at quaternion (w, x, y, z) for Isaac Sim world convention.

    Isaac Sim Camera world convention: +X forward, +Z up.
    Builds orthonormal frame [fwd | -right | up], converts to quaternion.
    """
    if world_up is None:
        world_up = np.array([0.0, 0.0, 1.0])

    fwd = np.asarray(target, float) - np.asarray(position, float)
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, world_up)
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)

    R = np.stack([fwd, -right, up], axis=1)  # columns: fwd, left, up
    tr = R[0, 0] + R[1, 1] + R[2, 2]

    if tr > 0:
        s = 0.5 / math.sqrt(tr + 1.0)
        qw = 0.25 / s
        qx = (R[2, 1] - R[1, 2]) * s
        qy = (R[0, 2] - R[2, 0]) * s
        qz = (R[1, 0] - R[0, 1]) * s
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = 2.0 * math.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2])
        qw = (R[2, 1] - R[1, 2]) / s;  qx = 0.25 * s
        qy = (R[0, 1] + R[1, 0]) / s;  qz = (R[0, 2] + R[2, 0]) / s
    elif R[1, 1] > R[2, 2]:
        s = 2.0 * math.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2])
        qw = (R[0, 2] - R[2, 0]) / s;  qx = (R[0, 1] + R[1, 0]) / s
        qy = 0.25 * s;                  qz = (R[1, 2] + R[2, 1]) / s
    else:
        s = 2.0 * math.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1])
        qw = (R[1, 0] - R[0, 1]) / s;  qx = (R[0, 2] + R[2, 0]) / s
        qy = (R[1, 2] + R[2, 1]) / s;  qz = 0.25 * s

    return np.array([qw, qx, qy, qz], dtype=float)


def sphere_camera_positions(
    radius: float = 3.59,
    target: list[float] | None = None,
    n_equator: int = 4,
    n_upper: int = 2,
) -> list[np.ndarray]:
    """Return camera positions distributed on a sphere of given radius.

    Layout: n_equator cameras on the equatorial ring at target height,
    n_upper cameras on an upper ring at elevation 45°.
    All positions are offset so the sphere center coincides with target.

    Args:
        radius: Sphere radius [m].
        target: Look-at target (sphere center) in world space. Defaults to [0,0,0.4].
        n_equator: Number of cameras on the equatorial ring.
        n_upper: Number of cameras on the 45° elevation ring.

    Returns:
        List of position arrays, length = n_equator + n_upper.
    """
    if target is None:
        target = [0.0, 0.0, 0.4]
    cx, cy, cz = target
    positions = []

    # Equatorial ring at elevation 0° (same Z as target)
    for i in range(n_equator):
        az = 2.0 * math.pi * i / n_equator
        positions.append(np.array([cx + radius * math.cos(az),
                                   cy + radius * math.sin(az),
                                   cz]))

    # Upper ring at elevation 45°
    el = math.pi / 4.0
    r_h = radius * math.cos(el)
    z_off = radius * math.sin(el)
    for i in range(n_upper):
        az = 2.0 * math.pi * i / n_upper + math.pi / n_upper  # offset so not overlapping equator
        positions.append(np.array([cx + r_h * math.cos(az),
                                   cy + r_h * math.sin(az),
                                   cz + z_off]))

    return positions


def make_cameras(
    world,
    prim_paths: list[str],
    positions: list[list[float] | np.ndarray],
    target: list[float] | np.ndarray,
    fps: int = 30,
    resolution: tuple[int, int] = (1280, 720),
    warmup_frames: int = 15,
) -> "list[Camera]":  # noqa: F821
    """Create and initialize multiple cameras in one world.reset() call.

    All cameras share the same target point. world.reset() is called once.

    Args:
        world: isaacsim.core.api.World instance.
        prim_paths: USD prim paths, one per camera.
        positions: World-space positions, one per camera.
        target: Common look-at target for all cameras.
        fps: Capture frequency.
        resolution: (width, height) in pixels.
        warmup_frames: Render steps before get_rgba() is valid.

    Returns:
        List of initialized Camera instances (same order as prim_paths).
    """
    from isaacsim.sensors.camera import Camera

    tgt = np.asarray(target, dtype=float)
    cameras = []

    for path, pos_raw in zip(prim_paths, positions):
        pos = np.asarray(pos_raw, dtype=float)
        orientation = _lookat_quaternion(pos, tgt)
        cam = Camera(prim_path=path, position=pos, frequency=fps, resolution=resolution)
        cameras.append((cam, pos, orientation))

    world.reset()

    initialized = []
    for cam, pos, orientation in cameras:
        cam.initialize()
        cam.set_world_pose(position=pos, orientation=orientation, camera_axes="world")
        initialized.append(cam)

    for _ in range(warmup_frames):
        world.step(render=True)

    return initialized


def make_camera(
    world,
    prim_path: str,
    position: list[float] | np.ndarray,
    target: list[float] | np.ndarray,
    fps: int = 30,
    resolution: tuple[int, int] = (1280, 720),
    warmup_frames: int = 15,
) -> "Camera":  # noqa: F821
    """Create, initialize, and orient a Camera prim.

    Calls world.reset() internally. Call this after all scene prims are built
    but before the main simulation loop.

    Args:
        world: isaacsim.core.api.World instance.
        prim_path: USD path for the camera prim (e.g. "/World/CamFront").
        position: Camera position in world space [x, y, z].
        target: Point the camera looks at in world space [x, y, z].
        fps: Capture frequency passed to Camera constructor.
        resolution: (width, height) in pixels.
        warmup_frames: Number of render steps before get_rgba() is valid.

    Returns:
        Initialized isaacsim.sensors.camera.Camera instance.
    """
    from isaacsim.sensors.camera import Camera

    pos = np.asarray(position, dtype=float)
    tgt = np.asarray(target, dtype=float)
    orientation = _lookat_quaternion(pos, tgt)

    camera = Camera(
        prim_path=prim_path,
        position=pos,
        frequency=fps,
        resolution=resolution,
    )

    world.reset()
    camera.initialize()
    camera.set_world_pose(position=pos, orientation=orientation, camera_axes="world")

    for _ in range(warmup_frames):
        world.step(render=True)

    return camera
