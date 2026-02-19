from pathlib import Path
from typing import Any, Dict, Optional

VALID_TYPES = {"cartesian", "joint"}


def convert_coordinates(data: Dict[str, Any], robot_model_urdf_path: str, from_type: str, to_type: str, *, config: Optional[Dict[str, Any]] = None, seed: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convert between Cartesian and joint coordinates.

    Args:
        data: Input coordinates (cartesian dict or joint dict).
        robot_model_urdf_path: Full path to a URDF file.
        from_type: "cartesian" or "joint".
        to_type: "joint" or "cartesian".
        config: Optional configuration (e.g., UTool/UFrame, flip, turns).
        seed: Optional joint seed for IK.
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
    raise NotImplementedError(
        "Kinematics conversion not implemented yet. "
        f"Resolved URDF: {urdf_path}. "
        "Next step: parse the URDF and implement FK/IK using the provided "
        "config/seed as needed."
    )
