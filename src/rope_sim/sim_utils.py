"""Simulation utility functions shared across rope scripts."""

from __future__ import annotations

import math


def compute_joint_drive(
    youngs_modulus: float,
    rope_diameter: float,
    rope_length: float,
    rope_mass: float,
    segments: int,
    damping_ratio: float = 0.3,
    fill_factor: float = 0.3,
) -> tuple[float, float]:
    """Compute D6 joint drive stiffness and damping for a twisted/braided rope.

    Returns (stiffness, damping) in USD DriveAPI units (per-degree), converted
    from SI (per-radian) via DEG_PER_RAD = pi/180.
    """
    r = rope_diameter / 2.0
    seg_len = rope_length / segments
    m_seg = rope_mass / segments

    I_eff = math.pi * r**4 / 4.0 * fill_factor
    k_bend = youngs_modulus * I_eff / seg_len

    I_rot = m_seg * seg_len * seg_len / 3.0
    omega_n = math.sqrt(k_bend / max(I_rot, 1e-12))
    c_damp = 2.0 * damping_ratio * I_rot * omega_n

    DEG_PER_RAD = math.pi / 180.0
    return k_bend * DEG_PER_RAD, c_damp * DEG_PER_RAD


def clamp_dt(
    dt: float,
    youngs_modulus: float,
    rope_diameter: float,
    rope_length: float,
    rope_mass: float,
    segments: int,
    fill_factor: float = 0.3,
    label: str = "rope",
) -> float:
    """Return dt clamped to 0.5/omega_n for numerical stability of the joint drive.

    Logs a warning via carb if dt is reduced.
    """
    import carb

    r = rope_diameter / 2.0
    I_eff = math.pi * r**4 / 4.0 * fill_factor
    L_seg = rope_length / segments
    m_seg = rope_mass / segments
    I_rot = max(m_seg * L_seg * L_seg / 3.0, 1e-12)
    omega_n = math.sqrt((youngs_modulus * I_eff / L_seg) / I_rot)
    dt_max = 0.5 / omega_n
    if dt > dt_max:
        carb.log_warn(
            f"[{label}] dt reduced {dt:.4f}→{dt_max:.6f}s "
            f"(omega_n={omega_n:.1f} rad/s)"
        )
        return dt_max
    return dt
