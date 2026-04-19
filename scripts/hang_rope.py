"""Simulate a rope hanging from a fixed anchor under gravity.

With --circle-radius > 0, the anchor traces a horizontal circle.

Run via the provided shell scripts, which set PYTHONPATH and use
/isaac-sim/python.sh as the interpreter.

Headed:   scripts/run_gui.sh [options]
Headless: scripts/run_headless.sh [options]
"""
from __future__ import annotations

import argparse
import sys


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

    world = World(
        physics_dt=args.dt,
        rendering_dt=args.dt,
        stage_units_in_meters=1.0,
    )
    world.scene.add_default_ground_plane()

    stage = simulation_app.context.get_stage()
    UsdGeom.Xform.Define(stage, "/World/Rope")

    cfg = RopeConfig(
        length=args.rope_length,
        diameter=args.rope_diameter,
        mass=args.rope_mass,
        segments=args.segments,
        swing_limit_deg=args.swing_limit,
        anchor_height=args.anchor_height,
    )
    builder = RopeBuilder(cfg, stage)
    builder.build()

    world.reset()

    _run(simulation_app, world, builder, args)

    simulation_app.close()


def _run(simulation_app, world, builder, args) -> None:
    import math

    import carb
    from pxr import Gf, UsdGeom

    tip_prim = builder.segment_prims[-1]

    def _tip_pos():
        # 毎回新規 XformCache を生成してステール読み取りを防ぐ
        return UsdGeom.XformCache().GetLocalToWorldTransform(tip_prim).ExtractTranslation()

    # Anchor circular motion setup
    circle = args.circle_radius > 0.0
    if circle:
        anchor_prim = builder.segment_prims[0]
        # Retrieve the translate XformOp created in RopeBuilder._create_segment
        anchor_translate_op = next(
            op for op in UsdGeom.Xformable(anchor_prim).GetOrderedXformOps()
            if op.GetOpType() == UsdGeom.XformOp.TypeTranslate
        )
        omega = 2.0 * math.pi / args.circle_period
        seg_length = args.rope_length / args.segments
        anchor_center_z = args.anchor_height - seg_length / 2.0
        carb.log_warn(
            f"[rope] circular anchor: R={args.circle_radius}m, T={args.circle_period}s"
        )

    def _update_anchor(t: float) -> None:
        if not circle:
            return
        x = args.circle_radius * math.cos(omega * t)
        y = args.circle_radius * math.sin(omega * t)
        anchor_translate_op.Set(Gf.Vec3d(x, y, anchor_center_z))

    if args.headless:
        num_steps = int(args.duration / args.dt)
        carb.log_warn(f"[rope] running {num_steps} steps ({args.duration:.1f}s) headless")
        for step in range(num_steps):
            _update_anchor(step * args.dt)
            world.step(render=False)
            if step % 60 == 0:
                pos = _tip_pos()
                elapsed = step * args.dt
                carb.log_warn(
                    f"[rope] t={elapsed:5.2f}s  tip=({pos[0]:+.4f}, {pos[1]:+.4f}, {pos[2]:+.4f}) m"
                )

        pos = _tip_pos()
        carb.log_warn(f"[rope] final tip: ({pos[0]:+.4f}, {pos[1]:+.4f}, {pos[2]:+.4f}) m")
    else:
        carb.log_warn("[rope] running with GUI — close the window to exit")
        step = 0
        while simulation_app.is_running():
            _update_anchor(step * args.dt)
            world.step(render=True)
            step += 1


if __name__ == "__main__":
    main()
