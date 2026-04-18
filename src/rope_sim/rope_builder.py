"""Builds a rope as a chain of rigid capsules connected by D6 joints."""
from __future__ import annotations

from dataclasses import dataclass

from pxr import Gf, Usd, UsdGeom, UsdPhysics


@dataclass
class RopeConfig:
    length: float = 0.6
    diameter: float = 0.01
    mass: float = 0.1
    segments: int = 25
    swing_limit_deg: float = 60.0
    anchor_height: float = 0.8
    color: tuple[float, float, float] = (0.8, 0.3, 0.1)


class RopeBuilder:
    """Creates a rope in a USD stage and returns the segment prims.

    Segment 0 is kinematic (the fixed anchor); segments 1..N-1 fall under gravity.
    Adjacent segments are connected by D6 joints that lock translation and limit swing.
    """

    def __init__(self, config: RopeConfig, stage: Usd.Stage, base_path: str = "/World/Rope") -> None:
        self._cfg = config
        self._stage = stage
        self._base_path = base_path
        self._segment_prims: list[Usd.Prim] = []

    @property
    def segment_prims(self) -> list[Usd.Prim]:
        return self._segment_prims

    def build(self) -> list[Usd.Prim]:
        cfg = self._cfg
        radius = cfg.diameter / 2.0
        seg_length = cfg.length / cfg.segments
        # USD Capsule height = cylindrical part only (hemispherical caps add radius each end)
        cyl_height = max(0.0, seg_length - 2.0 * radius)
        mass_per_seg = cfg.mass / cfg.segments

        for i in range(cfg.segments):
            center_z = cfg.anchor_height - seg_length * (i + 0.5)
            prim = self._create_segment(
                i, center_z, radius, cyl_height, mass_per_seg, kinematic=(i == 0)
            )
            self._segment_prims.append(prim)

        half_seg = seg_length / 2.0
        for i in range(cfg.segments - 1):
            self._add_d6_joint(i, half_seg)

        return self._segment_prims

    def _create_segment(
        self,
        index: int,
        center_z: float,
        radius: float,
        cyl_height: float,
        mass: float,
        kinematic: bool = False,
    ) -> Usd.Prim:
        path = f"{self._base_path}/Segment_{index:03d}"
        total_half = cyl_height / 2.0 + radius

        geom = UsdGeom.Capsule.Define(self._stage, path)
        geom.CreateRadiusAttr(radius)
        geom.CreateHeightAttr(cyl_height)
        geom.CreateAxisAttr("Z")
        geom.CreateExtentAttr(
            [Gf.Vec3f(-radius, -radius, -total_half), Gf.Vec3f(radius, radius, total_half)]
        )
        geom.CreateDisplayColorAttr().Set([Gf.Vec3f(*self._cfg.color)])
        geom.AddTranslateOp().Set(Gf.Vec3d(0.0, 0.0, center_z))

        prim = self._stage.GetPrimAtPath(path)
        UsdPhysics.CollisionAPI.Apply(prim)
        rb_api = UsdPhysics.RigidBodyAPI.Apply(prim)
        if kinematic:
            rb_api.CreateKinematicEnabledAttr(True)

        mass_api = UsdPhysics.MassAPI.Apply(prim)
        mass_api.CreateMassAttr(mass)

        return prim

    def _add_d6_joint(self, i: int, half_seg: float) -> None:
        """Connect segment i to segment i+1 with a SphericalJoint.

        SphericalJoint is a ball-and-socket: translation is inherently constrained at the
        pivot point; swing is limited by a cone; twist (around the rope axis) is free.
        D6 joints with two simultaneous swing limits trigger PhysX "double pyramid" errors.
        """
        path = f"{self._base_path}/Joint_{i:03d}"
        joint = UsdPhysics.SphericalJoint.Define(self._stage, path)

        joint.CreateBody0Rel().SetTargets([self._segment_prims[i].GetPath()])
        joint.CreateBody1Rel().SetTargets([self._segment_prims[i + 1].GetPath()])

        # Cone axis aligned with rope axis (Z); cone angles are half-angles in degrees
        joint.CreateAxisAttr("Z")
        joint.CreateConeAngle0LimitAttr(self._cfg.swing_limit_deg)
        joint.CreateConeAngle1LimitAttr(self._cfg.swing_limit_deg)

        # Joint frame: bottom endpoint of segment i == top endpoint of segment i+1
        joint.CreateLocalPos0Attr().Set(Gf.Vec3f(0.0, 0.0, -half_seg))
        joint.CreateLocalRot0Attr().Set(Gf.Quatf(1.0))
        joint.CreateLocalPos1Attr().Set(Gf.Vec3f(0.0, 0.0, half_seg))
        joint.CreateLocalRot1Attr().Set(Gf.Quatf(1.0))
