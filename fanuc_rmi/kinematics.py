"""
Kinematics utilities for converting between joint angles and Cartesian pose.

This module uses IKPy + a URDF model to:
- Forward kinematics (FK): joints -> X/Y/Z/W/P/R
- Inverse kinematics (IK): X/Y/Z/W/P/R -> joints

Notes:
- Units: positions are assumed in the same units as the URDF (often meters).
- Orientation: W/P/R are treated as roll/pitch/yaw in degrees (ZYX order).
- Joint keys must be ordered and named as J1, J2, J3, ... matching the URDF joint order.
"""

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from ikpy.chain import Chain

import numpy as np

VALID_TYPES = {"cartesian", "joint"}

def _get_chain(urdf_path: Path) -> "Chain":
    """Load and return an IKPy chain for the given URDF path."""
    if Chain is None:
        raise RuntimeError("ikpy is required for kinematics. Install with: pip install ikpy")
    return Chain.from_urdf_file(str(urdf_path))


def _active_indices(chain: "Chain") -> List[int]:
    """Return indices in the IKPy joint vector that correspond to active joints."""
    return [i for i, active in enumerate(chain.active_links_mask) if active]


def _extract_joint_values(joint_dict: Dict[str, Any]) -> List[float]:
    """Extract J1/J2/... values from a dict into a sorted list."""
    indexed: List[Tuple[int, float]] = []
    for key, value in joint_dict.items():
        if not isinstance(key, str):
            continue
        if key.startswith(("J", "j")):
            try:
                idx = int(key[1:])
            except ValueError:
                continue
            indexed.append((idx, float(value)))
    return [value for _, value in sorted(indexed, key=lambda item: item[0])]


def _joint_values_from_dict(joint_dict: Dict[str, Any]) -> List[float]:
    """Get joint values in ascending J index order (J1, J2, J3...)."""
    return _extract_joint_values(joint_dict)


def _build_joint_vector(chain: "Chain", joint_dict: Optional[Dict[str, Any]]) -> List[float]:
    """Build IKPy joint vector (length = len(chain.links)) from a J1..J* dict."""
    joint_vector = [0.0 for _ in chain.links]
    if not joint_dict:
        return joint_vector
    active = _active_indices(chain)
    values = _joint_values_from_dict(joint_dict)
    for index, value in zip(active, values):
        joint_vector[index] = float(value)
    return joint_vector


def _vector_to_joint_dict(chain: "Chain", joint_vector: Sequence[float]) -> Dict[str, float]:
    """Convert an IKPy joint vector back into a J1..J* dict."""
    active = _active_indices(chain)
    values = [float(joint_vector[i]) for i in active]
    return {f"J{i + 1}": value for i, value in enumerate(values)}


def _wpr_to_matrix(w: float, p: float, r: float) -> List[List[float]]:
    """Convert roll/pitch/yaw in degrees (W/P/R) to a 3x3 rotation matrix."""
    rx = math.radians(w)
    ry = math.radians(p)
    rz = math.radians(r)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    return [
        [cz * cy, cz * sy * sx - sz * cx, cz * sy * cx + sz * sx],
        [sz * cy, sz * sy * sx + cz * cx, sz * sy * cx - cz * sx],
        [-sy, cy * sx, cy * cx],
    ]


def _matrix_to_wpr(rotation: Sequence[Sequence[float]]) -> Tuple[float, float, float]:
    """Convert a 3x3 rotation matrix to roll/pitch/yaw in degrees (W/P/R)."""
    r00, r01, r02 = rotation[0]
    r10, r11, r12 = rotation[1]
    r20, r21, r22 = rotation[2]
    sy = math.sqrt(r00 * r00 + r10 * r10)
    if sy < 1e-9:
        w = math.degrees(math.atan2(-r12, r11))
        p = math.degrees(math.atan2(-r20, sy))
        r = 0.0
    else:
        w = math.degrees(math.atan2(r21, r22))
        p = math.degrees(math.atan2(-r20, sy))
        r = math.degrees(math.atan2(r10, r00))
    return w, p, r


def _frame_from_pose(position: Sequence[float], rotation: Optional[Sequence[Sequence[float]]]) -> Any:
    """Build a 4x4 homogeneous transform from position + rotation."""
    frame = [
        [1.0, 0.0, 0.0, float(position[0])],
        [0.0, 1.0, 0.0, float(position[1])],
        [0.0, 0.0, 1.0, float(position[2])],
        [0.0, 0.0, 0.0, 1.0],
    ]
    if rotation is not None:
        for i in range(3):
            for j in range(3):
                frame[i][j] = float(rotation[i][j])
    if np is not None:
        return np.array(frame, dtype=float)
    return frame


def _extract_rotation(frame: Any) -> Sequence[Sequence[float]]:
    """Extract a 3x3 rotation matrix from a 4x4 frame (numpy or list)."""
    try:
        return frame[:3, :3]
    except Exception:
        return [row[:3] for row in frame[:3]]


def _inverse_kinematics(chain: "Chain", target_position: Sequence[float], target_frame: Optional[Any], initial_position: Optional[Sequence[float]]):
    """Call IKPy with the best available API based on version and inputs."""
    if target_frame is not None and hasattr(chain, "inverse_kinematics_frame"):
        try:
            return chain.inverse_kinematics_frame(target_frame, initial_position=initial_position)
        except TypeError:
            return chain.inverse_kinematics_frame(target_frame)
    rotation = _extract_rotation(target_frame) if target_frame is not None else None
    try:
        if rotation is not None:
            return chain.inverse_kinematics(target_position=target_position, target_orientation=rotation, orientation_mode="all", initial_position=initial_position)
        return chain.inverse_kinematics(target_position=target_position, initial_position=initial_position)
    except TypeError:
        if rotation is not None:
            try:
                return chain.inverse_kinematics(target_position, rotation)
            except TypeError:
                return chain.inverse_kinematics(target_position)
        return chain.inverse_kinematics(target_position)


def convert_coordinates(data: Dict[str, Any], robot_model_urdf_path: str, from_type: str, to_type: str, seed: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convert between Cartesian and joint coordinates.

    Args:
        data: Input coordinates (cartesian dict or joint dict). Missing W/P/R default to 0.0.
        robot_model_urdf_path: Full path to a URDF file.
        from_type: "cartesian" or "joint".
        to_type: "joint" or "cartesian".
        seed: Optional joint seed for IK (dict of joint values).
    """
    if from_type not in VALID_TYPES:
        raise ValueError(f"from_type must be one of {sorted(VALID_TYPES)}")
    if to_type not in VALID_TYPES:
        raise ValueError(f"to_type must be one of {sorted(VALID_TYPES)}")
    if from_type == to_type:
        return dict(data)

    urdf_path = Path(robot_model_urdf_path)
    if not urdf_path.exists():
        raise FileNotFoundError(f"URDF not found at path: {urdf_path}")
    if urdf_path.suffix.lower() != ".urdf":
        raise ValueError(f"URDF path must end with .urdf: {urdf_path}")

    # Parse the URDF for this conversion call.
    chain = _get_chain(urdf_path)
    if from_type == "joint" and to_type == "cartesian":
        # FK: joints -> 4x4 transform -> XYZ + W/P/R.
        joint_vector = _build_joint_vector(chain, data)
        frame = chain.forward_kinematics(joint_vector)
        x, y, z = float(frame[0][3]), float(frame[1][3]), float(frame[2][3])
        w, p, r = _matrix_to_wpr(_extract_rotation(frame))
        return {"X": x, "Y": y, "Z": z, "W": w, "P": p, "R": r}

    if from_type == "cartesian" and to_type == "joint":
        # IK: XYZ + W/P/R -> joint vector -> joint dict.
        x = float(data.get("X", data.get("x", 0.0)))
        y = float(data.get("Y", data.get("y", 0.0)))
        z = float(data.get("Z", data.get("z", 0.0)))
        w = float(data.get("W", data.get("w", 0.0)))
        p = float(data.get("P", data.get("p", 0.0)))
        r = float(data.get("R", data.get("r", 0.0)))
        rotation = _wpr_to_matrix(w, p, r)
        target_frame = _frame_from_pose([x, y, z], rotation)
        # Seed helps IK choose the intended solution when multiple exist.
        initial_position = _build_joint_vector(chain, seed) if seed else None
        joints = _inverse_kinematics(chain, [x, y, z], target_frame, initial_position)
        return _vector_to_joint_dict(chain, joints)

    return dict(data)
