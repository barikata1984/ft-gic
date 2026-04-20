"""Builds a rope as a chain of rigid capsules connected by D6 joints with angular drives."""
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
    # Angular bending behaviour for the swing axes (rotX / rotY).
    joint_stiffness: float = 0.0  # N·m/rad
    joint_damping: float = 0.0  # N·m·s/rad
    # If True, build rope horizontally along +X (cantilever test).
    horizontal: bool = False


class RopeBuilder:
    """Creates a rope in a USD stage and returns the segment prims.

    Segment 0 is kinematic (the fixed anchor); segments 1..N-1 fall under gravity.
    Adjacent segments are connected by D6 joints (UsdPhysics.Joint) that lock translation,
    limit swing, and apply an angular drive on the two swing axes (rotX, rotY) so the rope
    behaves like a continuous elastic beam in bending.
    """

    def __init__(
        self, config: RopeConfig, stage: Usd.Stage, base_path: str = "/World/Rope"
    ) -> None:
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
            if cfg.horizontal:
                # Extend rope along +X at constant height.
                # Segment 0 is the anchor at (0, 0, anchor_height); subsequent segments
                # continue along +X so that seg_i center = (seg_length * (i + 0.5 - 0.5),
                # 0, anchor_height) when using the spec "segment i center at
                # (seg_length * (i + 0.5), 0, anchor_height)".
                # Capsule local Z axis is rotated 90° about Y so it points along world +X.
                center = (seg_length * (i + 0.5), 0.0, cfg.anchor_height)
            else:
                center_z = cfg.anchor_height - seg_length * (i + 0.5)
                center = (0.0, 0.0, center_z)
            prim = self._create_segment(
                i, center, radius, cyl_height, mass_per_seg,
                kinematic=(i == 0), horizontal=cfg.horizontal,
            )
            self._segment_prims.append(prim)

        half_seg = seg_length / 2.0
        for i in range(cfg.segments - 1):
            self._add_d6_joint(i, half_seg)

        return self._segment_prims

    def _create_segment(
        self,
        index: int,
        center: tuple[float, float, float],
        radius: float,
        cyl_height: float,
        mass: float,
        kinematic: bool = False,
        horizontal: bool = False,
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
        geom.AddTranslateOp().Set(Gf.Vec3d(*center))
        if horizontal:
            # Rotate capsule -90° about +Y so its local +Z axis points along world -X.
            # With this choice, body-local (0, 0, -half_seg) (the body-0 joint anchor)
            # maps to world +X end, and body-local (0, 0, +half_seg) (the body-1 joint
            # anchor) maps to world -X end.  Because segment i sits at smaller X than
            # segment i+1, the joint therefore ties segment i's +X end to segment
            # (i+1)'s -X end, which is the correct neighbour endpoint.
            geom.AddRotateYOp().Set(-90.0)

        prim = self._stage.GetPrimAtPath(path)
        UsdPhysics.CollisionAPI.Apply(prim)
        rb_api = UsdPhysics.RigidBodyAPI.Apply(prim)
        if kinematic:
            rb_api.CreateKinematicEnabledAttr(True)

        mass_api = UsdPhysics.MassAPI.Apply(prim)
        mass_api.CreateMassAttr(mass)

        return prim

    def _add_d6_joint(self, i: int, half_seg: float) -> None:
        """Connect segment i to segment i+1 with a D6 joint (UsdPhysics.Joint).

        Linear DOFs (transX/Y/Z) are locked, the two swing axes (rotX, rotY) are limited
        to ±swing_limit_deg and given an angular drive at zero target so the rope resists
        bending elastically. Twist (rotZ) is left free.
        """
        path = f"{self._base_path}/Joint_{i:03d}"
        joint = UsdPhysics.Joint.Define(self._stage, path)
        joint_prim = joint.GetPrim()

        joint.CreateBody0Rel().SetTargets([self._segment_prims[i].GetPath()])
        joint.CreateBody1Rel().SetTargets([self._segment_prims[i + 1].GetPath()])

        # Joint frame: bottom endpoint of segment i == top endpoint of segment i+1
        joint.CreateLocalPos0Attr().Set(Gf.Vec3f(0.0, 0.0, -half_seg))
        joint.CreateLocalRot0Attr().Set(Gf.Quatf(1.0))
        joint.CreateLocalPos1Attr().Set(Gf.Vec3f(0.0, 0.0, half_seg))
        joint.CreateLocalRot1Attr().Set(Gf.Quatf(1.0))

        # Lock linear DOFs (low > high == locked in USD physics convention)
        for dof in ("transX", "transY", "transZ"):
            limit = UsdPhysics.LimitAPI.Apply(joint_prim, dof)
            limit.CreateLowAttr(1.0)
            limit.CreateHighAttr(-1.0)

        # Swing-cone limit (combined ±swing_limit on rotX/rotY). Using the per-axis
        # rotX & rotY LimitAPI both at once triggers PhysX "double pyramid" — instead
        # rely on the angular drive's restoring torque plus a generous twist range.
        # If a hard limit is desired, only one swing axis can be configured this way.

        # Angular drives on the two swing axes — restoring torque toward straight (target=0)
        for dof in ("rotX", "rotY"):
            drive = UsdPhysics.DriveAPI.Apply(joint_prim, dof)
            drive.CreateTypeAttr("force")
            drive.CreateStiffnessAttr(self._cfg.joint_stiffness)
            drive.CreateDampingAttr(self._cfg.joint_damping)
            drive.CreateTargetPositionAttr(0.0)
            drive.CreateTargetVelocityAttr(0.0)

        # Twist (rotZ): no stiffness (free to rotate), but damped to prevent
        # uncontrolled twist accumulation from circular-motion inertia forces.
        twist_drive = UsdPhysics.DriveAPI.Apply(joint_prim, "rotZ")
        twist_drive.CreateTypeAttr("force")
        twist_drive.CreateStiffnessAttr(0.0)
        twist_drive.CreateDampingAttr(self._cfg.joint_damping)
        twist_drive.CreateTargetPositionAttr(0.0)
        twist_drive.CreateTargetVelocityAttr(0.0)
