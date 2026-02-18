from .connection import SocketJsonReader, send_command


def linear_relative(
    client_socket,
    reader: SocketJsonReader,
    relative_displacement: dict,
    speed: float,
    sequence_id: int = 1,
):
    """Send a linear relative motion command."""
    
    data = {
        "Instruction": "FRC_LinearRelative",
        "SequenceID": sequence_id,
        "Configuration": {
            "UToolNumber": 1, "UFrameNumber": 0, "Front": 1, "Up": 1, "Left": 0, "Flip": 0,
            "Turn4": 0, "Turn5": 0, "Turn6": 0
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
):
    """Send a linear absolute motion command."""
    
    data = {
        "Instruction": "FRC_LinearMotion",
        "SequenceID": sequence_id,
        "Configuration": {
            "UToolNumber": 1, "UFrameNumber": 0, "Front": 1, "Up": 1, "Left": 0, "Flip": 0,
            "Turn4": 0, "Turn5": 0, "Turn6": 0
        },
        "Position": absolute_position,
        "SpeedType": "mmSec", "Speed": speed, "TermType": "FINE"
    }
    response = send_command(client_socket, reader, data)
    print(response)
    
def joint_relative(
    client_socket,
    reader: SocketJsonReader,
    relative_displacement: dict,
    speed_percentage: float,
    sequence_id: int = 1,
):
    """Send a joint relative motion command."""
    
    data = {
        "Instruction": "FRC_JointRelativeJRep",
        "SequenceID": sequence_id,
        "Configuration": {
            "UToolNumber": 1, "UFrameNumber": 0, "Front": 1, "Up": 1, "Left": 0, "Flip": 0,
            "Turn4": 0, "Turn5": 0, "Turn6": 0
        },
        "Position": relative_displacement,
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
):
    """Send a joint absolute motion command."""

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


def wait_time(
    client_socket,
    reader: SocketJsonReader,
    seconds: float,
    sequence_id: int = 1,
):
    """Wait for the specified number of seconds."""

    data = {"Instruction": "FRC_WaitTime", "SequenceID": sequence_id, "Time": seconds}
    response = send_command(client_socket, reader, data)
    print(response)
