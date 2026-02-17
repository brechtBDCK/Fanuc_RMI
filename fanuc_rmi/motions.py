from .connection import SocketJsonReader, send_command


def linear_relative(client_socket, reader: SocketJsonReader, relative_displacement: dict, speed: float):
    """Send a linear relative motion command."""
    
    data = {
        "Instruction": "FRC_LinearRelative",
        "SequenceID": 1,
        "Configuration": {
            "UToolNumber": 1, "UFrameNumber": 0, "Front": 1, "Up": 1, "Left": 0, "Flip": 0,
            "Turn4": 0, "Turn5": 0, "Turn6": 0
        },
        "Position": relative_displacement,
        "SpeedType": "mmSec", "Speed": speed, "TermType": "FINE"
    }
    response = send_command(client_socket, reader, data)
    print(response)
    
    
def linear_absolute(client_socket, reader: SocketJsonReader, absolute_position: dict, speed: float):
    """Send a linear absolute motion command."""
    
    data = {
        "Instruction": "FRC_LinearMotion",
        "SequenceID": 1,
        "Configuration": {
            "UToolNumber": 1, "UFrameNumber": 0, "Front": 1, "Up": 1, "Left": 0, "Flip": 0,
            "Turn4": 0, "Turn5": 0, "Turn6": 0
        },
        "Position": absolute_position,
        "SpeedType": "mmSec", "Speed": speed, "TermType": "FINE"
    }
    response = send_command(client_socket, reader, data)
    print(response)
    
def joint_relative(client_socket, reader: SocketJsonReader, relative_displacement: dict, speed_percentage: float):
    """Send a joint relative motion command."""
    
    data = {
        "Instruction": "FRC_JointRelativeJRep",
        "SequenceID": 1,
        "Configuration": {
            "UToolNumber": 1, "UFrameNumber": 0, "Front": 1, "Up": 1, "Left": 0, "Flip": 0,
            "Turn4": 0, "Turn5": 0, "Turn6": 0
        },
        "Position": relative_displacement,
        "SpeedType": "Percent", "Speed": speed_percentage, "TermType": "FINE"
    }
    response = send_command(client_socket, reader, data)
    print(response)

def joint_absolute(client_socket, reader: SocketJsonReader, absolute_position: dict, speed_percentage: float):
    """Send a joint absolute motion command."""

    data = {
            "Instruction": "FRC_JointMotionJRep",
            "SequenceID": 1,
            "JointAngle": absolute_position,
            "SpeedType": "Percent", "Speed": speed_percentage, "TermType": "FINE"
        }
    
    response = send_command(client_socket, reader, data)
    print(response)
