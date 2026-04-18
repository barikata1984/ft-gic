"""Simulate a rope hanging from a fixed anchor under gravity.

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
    import carb
    from pxr import UsdGeom

    tip_prim = builder.segment_prims[-1]
    xform_cache = UsdGeom.XformCache()

    def _tip_pos():
        xf = xform_cache.GetLocalToWorldTransform(tip_prim)
        return xf.ExtractTranslation()

    if args.headless:
        num_steps = int(args.duration / args.dt)
        carb.log_warn(f"[rope] running {num_steps} steps ({args.duration:.1f}s) headless")
        for step in range(num_steps):
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
        while simulation_app.is_running():
            world.step(render=True)


if __name__ == "__main__":
    main()
