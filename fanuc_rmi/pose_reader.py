import json
from pathlib import Path
from .connection import SocketJsonReader, send_command, read_packet

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
    send_command(client_socket, data)
    response = read_packet(reader)

    print(response)
    read_error(client_socket, reader, response)

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
    send_command(client_socket, data)
    response = read_packet(reader)
    print(response)
    read_error(client_socket, reader, response)

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
    send_command(client_socket, data)
    response = read_packet(reader)
    print(response)
    read_error(client_socket, reader, response)

    uframe = response.get("UFrameNumber")
    utool = response.get("UToolNumber")
    return {"UFrameNumber": uframe, "UToolNumber": utool}


def set_uframe_utool(client_socket, reader: SocketJsonReader, uframe_number: int, utool_number: int) -> dict:
    """Set the controller's currently active user frame/tool numbers."""
    data = {
        "Command": "FRC_SetUFrameUTool",
        "UFrameNumber": int(uframe_number),
        "UToolNumber": int(utool_number),
    }
    send_command(client_socket, data)
    response = read_packet(reader)
    print(response)
    read_error(client_socket, reader, response)

    return {"UFrameNumber": int(uframe_number),"UToolNumber": int(utool_number)}


def read_uframe_data(client_socket, reader: SocketJsonReader, frame_number: int) -> dict:
    """Read FANUC user frame data and return X/Y/Z/W/P/R."""
    data = {"Command": "FRC_ReadUFrameData", "FrameNumber": frame_number}
    send_command(client_socket, data)
    response = read_packet(reader)
    print(response)
    read_error(client_socket, reader, response)

    return _normalize_frame_data(response.get("Frame", {}), require_all_keys=False)


def write_uframe_data(client_socket, reader: SocketJsonReader, frame_number: int, frame: dict) -> dict:
    """Write FANUC user frame data. Frame must contain X/Y/Z/W/P/R."""
    frame_payload = _normalize_frame_data(frame, require_all_keys=True)

    data = {
        "Command": "FRC_WriteUFrameData",
        "FrameNumber": frame_number,
        "Frame": frame_payload,
    }
    send_command(client_socket, data)
    response = read_packet(reader)
    print(response)
    read_error(client_socket, reader, response)

    return response


def read_utool_data(client_socket, reader: SocketJsonReader, tool_number: int) -> dict:
    """Read FANUC user tool data and return X/Y/Z/W/P/R."""
    data = {"Command": "FRC_ReadUToolData", "ToolNumber": tool_number}
    send_command(client_socket, data)
    response = read_packet(reader)
    print(response)
    read_error(client_socket, reader, response)

    return _normalize_frame_data(response.get("Frame", {}), require_all_keys=False)


def write_utool_data(client_socket, reader: SocketJsonReader, tool_number: int, frame: dict) -> dict:
    """Write FANUC user tool data. Frame must contain X/Y/Z/W/P/R."""
    frame_payload = _normalize_frame_data(frame, require_all_keys=True)

    data = {
        "Command": "FRC_WriteUToolData",
        "ToolNumber": tool_number,
        "Frame": frame_payload,
    }
    send_command(client_socket, data)
    response = read_packet(reader)
    print(response)
    read_error(client_socket, reader, response)
    return response


def read_error(client_socket, reader: SocketJsonReader, response_prev_command):
    """Read the controller's most recent error packet."""
    error_id = int(response_prev_command.get("ErrorID", -1))
    if error_id == 0:
        return None

    data = {"Command": "FRC_ReadError"}
    response_read_error = send_command(client_socket, reader, data)
    print(response_read_error)
    return response_read_error


def read_din(client_socket, reader: SocketJsonReader, port_number: int) -> dict:
    """Read a digital input port and return the controller response packet."""
    data = {
        "Command": "FRC_ReadDIN",
        "PortNumber": int(port_number),
    }
    response = send_command(client_socket, reader, data)
    print(response)
    read_error(client_socket, reader, response)
    return response


def write_dout(client_socket, reader: SocketJsonReader, port_number: int, port_value: str | bool) -> dict:
    """Write a digital output port. Port value must be ON/OFF or a bool."""
    if isinstance(port_value, bool):
        normalized_value = "ON" if port_value else "OFF"
    else:
        normalized_value = str(port_value).strip().upper()

    if normalized_value not in {"ON", "OFF"}:
        raise ValueError("Port value must be 'ON', 'OFF', True, or False")

    data = {
        "Command": "FRC_WriteDOUT",
        "PortNumber": int(port_number),
        "PortValue": normalized_value,
    }
    response = send_command(client_socket, reader, data)
    print(response)
    read_error(client_socket, reader, response)

    return response
