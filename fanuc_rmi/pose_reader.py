from pathlib import Path
from .connection import SocketJsonReader, send_command

FRAME_KEYS = ("X", "Y", "Z", "W", "P", "R")


def _normalize_frame_data(frame: dict, *, require_all_keys: bool) -> dict:
    if not isinstance(frame, dict):
        raise TypeError(f"Frame must be a dict, got {type(frame).__name__}")

    missing = [key for key in FRAME_KEYS if key not in frame]
    if require_all_keys and missing:
        missing_txt = ", ".join(missing)
        raise ValueError(f"Frame is missing required keys: {missing_txt}")

    return {key: float(frame.get(key, 0.0)) for key in FRAME_KEYS}


def read_cartesian_coordinates(client_socket, reader: SocketJsonReader, output_path: str = "./robot_position_cartesian.txt"):
    """Send a command to read the robot's Cartesian position and return it."""
    data = {"Command": "FRC_ReadCartesianPosition"}
    response = send_command(client_socket, reader, data)

    print(response)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

    # Extract position data
    position = response.get("Position", {})
    if position:
        position_data = {key: float(position.get(key, 0.0)) for key in ("X", "Y", "Z", "W", "P", "R")}
        # Format the position data
        formatted_position = (
            f"X: {position_data['X']:.3f}, Y: {position_data['Y']:.3f}, Z: {position_data['Z']:.3f}, "
            f"W: {position_data['W']:.3f}, P: {position_data['P']:.3f}, R: {position_data['R']:.3f}"
        )

        # Append to the text file with a pose number
        try:
            with path.open("r", encoding="utf-8") as file:
                lines = file.readlines()
                pose_count = sum(1 for line in lines if line.startswith("Pose #")) + 1
        except FileNotFoundError:
            pose_count = 1

        with path.open("a", encoding="utf-8") as file:
            file.write(f"Pose #{pose_count}:")
            file.write(formatted_position + "\n")

        print(f"Position data appended to {path.name} as Pose #{pose_count}")
        return position_data
    else:
        print("No position data available.")
        return {}

def read_joint_coordinates(client_socket, reader: SocketJsonReader, output_path: str = "./robot_position_joint.txt"):
    """Send a command to read the robot's joint angles and return them."""
    data = {"Command": "FRC_ReadJointAngles"}
    response = send_command(client_socket, reader, data)
    print(response)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

    # Extract joint data
    joints = response.get("JointAngle") or response.get("Joints") or {}
    if joints:
        # Format the joint data
        ordered_keys = [f"J{i}" for i in range(0, 10)]
        ordered_items = [(key, float(joints[key])) for key in ordered_keys if key in joints]
        if ordered_items:
            joint_data = {key: value for key, value in ordered_items}
            parts = [f"{key}: {value:.3f}" for key, value in ordered_items]
        else:
            joint_data = {key: float(value) for key, value in joints.items()}
            parts = [f"{key}: {value:.3f}" for key, value in joint_data.items()]
        formatted_joints = ", ".join(parts)

        # Append to the text file with a pose number
        try:
            with path.open("r", encoding="utf-8") as file:
                lines = file.readlines()
                pose_count = sum(1 for line in lines if line.startswith("Pose #")) + 1
        except FileNotFoundError:
            pose_count = 1

        with path.open("a", encoding="utf-8") as file:
            file.write(f"Pose #{pose_count}:")
            file.write(formatted_joints + "\n")

        print(f"Joint data appended to {path.name} as Pose #{pose_count}")
        return joint_data
    else:
        print("No joint data available.")
        return {}


def get_uframe_utool(client_socket, reader: SocketJsonReader) -> dict:
    """Read the controller's currently active user frame/tool numbers."""
    data = {"Command": "FRC_GetUFrameUTool"}
    response = send_command(client_socket, reader, data)
    print(response)

    error_id = int(response.get("ErrorID", -1))
    if error_id != 0:
        return {"ErrorID": error_id, "UFrameNumber": None, "UToolNumber": None}

    uframe = response.get("UFrameNumber")
    utool = response.get("UToolNumber")
    return {"ErrorID": error_id, "UFrameNumber": uframe, "UToolNumber": utool}


def read_uframe_data(client_socket, reader: SocketJsonReader, frame_number: int) -> dict:
    """Read FANUC user frame data and return X/Y/Z/W/P/R."""
    data = {"Command": "FRC_ReadUFrameData", "FrameNumber": frame_number}
    response = send_command(client_socket, reader, data)
    print(response)

    return _normalize_frame_data(response.get("Frame", {}), require_all_keys=False)


def write_uframe_data(client_socket, reader: SocketJsonReader, frame_number: int, frame: dict) -> dict:
    """Write FANUC user frame data. Frame must contain X/Y/Z/W/P/R."""
    frame_payload = _normalize_frame_data(frame, require_all_keys=True)

    data = {
        "Command": "FRC_WriteUFrameData",
        "FrameNumber": frame_number,
        "Frame": frame_payload,
    }
    response = send_command(client_socket, reader, data)
    print(response)
    return response


def read_utool_data(client_socket, reader: SocketJsonReader, tool_number: int) -> dict:
    """Read FANUC user tool data and return X/Y/Z/W/P/R."""
    data = {"Command": "FRC_ReadUToolData", "ToolNumber": tool_number}
    response = send_command(client_socket, reader, data)
    print(response)

    return _normalize_frame_data(response.get("Frame", {}), require_all_keys=False)


def write_utool_data(client_socket, reader: SocketJsonReader, tool_number: int, frame: dict) -> dict:
    """Write FANUC user tool data. Frame must contain X/Y/Z/W/P/R."""
    frame_payload = _normalize_frame_data(frame, require_all_keys=True)

    data = {
        "Command": "FRC_WriteUToolData",
        "ToolNumber": tool_number,
        "Frame": frame_payload,
    }
    response = send_command(client_socket, reader, data)
    print(response)
    return response
