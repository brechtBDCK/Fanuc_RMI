import json
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


def read_cartesian_coordinates(client_socket, reader: SocketJsonReader, output_path: str = "./robot_position_cartesian.jsonl"):
    """Send a command to read the robot's Cartesian position and return full packet."""
    data = {"Command": "FRC_ReadCartesianPosition"}
    response = send_command(client_socket, reader, data)

    print(response)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

    # Write the full returned packet as one untouched JSON line.
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(response, ensure_ascii=True, sort_keys=False) + "\n")

    position = response.get("Position", {})
    if not position:
        print("No position data available.")
    return response

def read_joint_coordinates(client_socket, reader: SocketJsonReader, output_path: str = "./robot_position_joint.jsonl"):
    """Send a command to read the robot's joint angles and return full packet."""
    data = {"Command": "FRC_ReadJointAngles"}
    response = send_command(client_socket, reader, data)
    print(response)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

    # Write the full returned packet as one untouched JSON line.
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(response, ensure_ascii=True, sort_keys=False) + "\n")

    joints = response.get("JointAngle") or response.get("Joints") or {}
    if not joints:
        print("No joint data available.")
    return response


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
