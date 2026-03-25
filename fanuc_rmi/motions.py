from .connection import SocketJsonReader, send_command


def linear_relative(
    client_socket,
    reader: SocketJsonReader,
    relative_displacement: dict,
    speed: float,
    sequence_id: int = 1,
    uframe: int = 0,
    utool: int = 1,
):
    """Send a linear relative motion command."""
    
    data = {
        "Instruction": "FRC_LinearRelative",
        "SequenceID": sequence_id,
        "Configuration": {
            "UToolNumber": int(utool),
            "UFrameNumber": int(uframe),
            "Front": 1,
            "Up": 1,
            "Left": 0,
            "Flip": 0,
            "Turn4": 0,
            "Turn5": 0,
            "Turn6": 0,
        },
        "Position": relative_displacement,
        "SpeedType": "mmSec", "Speed": speed, "TermType": "FINE"
    }
    response = send_command(client_socket, reader, data)
    print(response)
    
    
def linear_absolute(
    client_socket,
    reader: SocketJsonReader,
    absolute_position: dict,
    speed: float,
    sequence_id: int = 1,
    uframe: int = 0,
    utool: int = 1,
):
    """Send a linear absolute motion command."""
    
    data = {
        "Instruction": "FRC_LinearMotion",
        "SequenceID": sequence_id,
        "Configuration": {
            "UToolNumber": int(utool),
            "UFrameNumber": int(uframe),
            "Front": 1,
            "Up": 1,
            "Left": 0,
            "Flip": 0,
            "Turn4": 0,
            "Turn5": 0,
            "Turn6": 0,
        },
        "Position": absolute_position,
        "SpeedType": "mmSec", "Speed": speed, "TermType": "FINE", "TermValue": 100
    }
    response = send_command(client_socket, reader, data)
    print(response)
    
def joint_relative(
    client_socket,
    reader: SocketJsonReader,
    relative_displacement: dict,
    speed_percentage: float,
    sequence_id: int = 1,
    uframe: int = 1,
    utool: int = 1,
):
    """Send a joint relative motion command."""
    _ = (uframe, utool)  # Joint-space command; frame/tool are accepted for API consistency.

    data = {
        "Instruction": "FRC_JointRelativeJRep",
        "SequenceID": sequence_id,
        "JointAngle": relative_displacement,
        "SpeedType": "Percent", "Speed": speed_percentage, "TermType": "FINE"
    }
    response = send_command(client_socket, reader, data)
    print(response)

def joint_absolute(
    client_socket,
    reader: SocketJsonReader,
    absolute_position: dict,
    speed_percentage: float,
    sequence_id: int = 1,
    uframe: int = 0,
    utool: int = 1,
):
    """Send a joint absolute motion command."""

    _ = (uframe, utool)  # Joint-space command; frame/tool are accepted for API consistency.
    data = {
            "Instruction": "FRC_JointMotionJRep",
            "SequenceID": sequence_id,
            "JointAngle": absolute_position,
            "SpeedType": "Percent", "Speed": speed_percentage, "TermType": "FINE"
        }
    
    response = send_command(client_socket, reader, data)
    print(response)


def speed_override(client_socket, reader: SocketJsonReader, value: int):
    """Set the speed override percentage."""

    data = {"Command": "FRC_SetOverRide", "Value": value}
    response = send_command(client_socket, reader, data)
    print(response)


def wait_time(client_socket, reader: SocketJsonReader, seconds: float, sequence_id: int = 1):
    """Wait for the specified number of seconds."""

    data = {"Instruction": "FRC_WaitTime", "SequenceID": sequence_id, "Time": seconds}
    response = send_command(client_socket, reader, data)
    print(response)


def set_uframe(client_socket, reader: SocketJsonReader, frame_number: int, sequence_id: int = 1):
    """Queue a TP instruction that sets the active UFRAME_NUM."""
    data = {
        "Instruction": "FRC_SetUFrame",
        "SequenceID": int(sequence_id),
        "FrameNumber": int(frame_number),
    }
    response = send_command(client_socket, reader, data)
    print(response)
    return response


def set_utool(client_socket, reader: SocketJsonReader, tool_number: int, sequence_id: int = 1):
    """Queue a TP instruction that sets the active UTOOL_NUM."""
    data = {
        "Instruction": "FRC_SetUTool",
        "SequenceID": int(sequence_id),
        "ToolNumber": int(tool_number),
    }
    response = send_command(client_socket, reader, data)
    print(response)
    return response
