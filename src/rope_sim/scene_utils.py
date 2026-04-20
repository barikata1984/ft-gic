"""Scene construction utilities shared across rope scripts."""

from __future__ import annotations

from pxr import Gf, UsdGeom, UsdLux, UsdPhysics


def add_invisible_ground(stage) -> None:
    """Add a collision-only ground plane at z=0 with no visual geometry."""
    UsdGeom.Xform.Define(stage, "/World/GroundPlane")
    UsdPhysics.CollisionAPI.Apply(stage.GetPrimAtPath("/World/GroundPlane"))
    plane = UsdGeom.Plane.Define(stage, "/World/GroundPlane/CollisionPlane")
    plane.CreateAxisAttr("Z")
    plane.CreatePurposeAttr(UsdGeom.Tokens.guide)
    UsdPhysics.CollisionAPI.Apply(stage.GetPrimAtPath("/World/GroundPlane/CollisionPlane"))


def add_default_lighting(stage) -> None:
    """Add a dome fill light and a distant key light."""
    dome = UsdLux.DomeLight.Define(stage, "/World/DomeLight")
    dome.CreateIntensityAttr(800.0)
    key = UsdLux.DistantLight.Define(stage, "/World/KeyLight")
    key.CreateIntensityAttr(4000.0)
    key.CreateAngleAttr(0.53)
    UsdGeom.Xformable(key.GetPrim()).AddRotateXYZOp().Set(Gf.Vec3f(-60.0, 30.0, 0.0))


def setup_recording_world(simulation_app, physics_dt: float, fps: int):
    """Create World with physics/rendering dt, invisible ground, and default lighting.

    Returns (world, stage).
    """
    from isaacsim.core.api import World

    capture_dt = 1.0 / fps
    world = World(
        physics_dt=physics_dt,
        rendering_dt=capture_dt,
        stage_units_in_meters=1.0,
    )

    stage = simulation_app.context.get_stage()
    add_invisible_ground(stage)
    UsdGeom.Xform.Define(stage, "/World/Rope")
    add_default_lighting(stage)

    return world, stage
