from fanuc_rmi.connection import MAX_RMI_BUFFER

from .connection import SocketJsonReader, send_command, read_packet

from typing import Literal
import numpy as np
from collections import deque

def linear_relative(
    client_socket,
    reader: SocketJsonReader,
    relative_displacement: dict,
    speed: float,
    sequence_id: int = 1,
    uframe: int = 1,
    utool: int = 1,
    term_type: Literal["FINE", "CNT"] = "FINE",
    term_value: int = 100,
):
    """Send a linear relative motion command and return the response (blocking)."""
    
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
        "SpeedType": "mmSec",
        "Speed": speed,
        "TermType": term_type,
        "TermValue": term_value
    }
    send_command(client_socket, data)
    response = read_packet(reader)
    print(response)
    
    
def linear_absolute(
    client_socket,
    reader: SocketJsonReader,
    absolute_position: dict,
    speed: float,
    sequence_id: int = 1,
    uframe: int = 1,
    utool: int = 1,
    term_type: Literal["FINE", "CNT"] = "FINE",
    term_value: int = 100,
):
    """Send a linear absolute motion command and return the response (blocking)."""
    
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
        "SpeedType": "mmSec",
        "Speed": speed,
        "TermType": term_type,
        "TermValue": term_value
    }
    send_command(client_socket, data)
    response = read_packet(reader)
    print(response)

def make_joint_relative_packet(
    relative_displacement: dict,
    speed_percentage: float,
    sequence_id: int = 1,
    term_type: Literal["FINE", "CNT"] = "FINE",
    term_value: int = 100,
) -> dict:
    """Create a joint relative motion command packet."""

    return {
        "Instruction": "FRC_JointRelativeJRep",
        "SequenceID": sequence_id,
        "JointAngle": relative_displacement,
        "SpeedType": "Percent",
        "Speed": speed_percentage,
        "TermType": term_type,
        "TermValue": term_value
    }

    
def joint_relative(
    client_socket,
    reader: SocketJsonReader,
    relative_displacement: dict,
    speed_percentage: float,
    sequence_id: int = 1,
    term_type: Literal["FINE", "CNT"] = "FINE",
    term_value: int = 100,
):
    """Send a joint relative motion command and return the response (blocking)."""

    data = make_joint_relative_packet(
        relative_displacement,
        speed_percentage,
        sequence_id,
        term_type,
        term_value,
    )

    send_command(client_socket, data)
    response = read_packet(reader)
    print(response)


def make_joint_absolute_packet(
    absolute_position: dict,
    speed_percentage: float,
    sequence_id: int = 1,
    term_type: Literal["FINE", "CNT"] = "FINE",
    term_value: int = 100,
) -> dict:
    """Create a joint absolute motion command packet."""

    return {
        "Instruction": "FRC_JointMotionJRep",
        "SequenceID": sequence_id,
        "JointAngle": absolute_position,
        "SpeedType": "Percent",
        "Speed": speed_percentage,
        "TermType": term_type,
        "TermValue": term_value
    }


def joint_absolute(
    client_socket,
    reader: SocketJsonReader,
    absolute_position: dict,
    speed_percentage: float,
    sequence_id: int = 1,
    term_type: Literal["FINE", "CNT"] = "FINE",
    term_value: int = 100,
):
    """Send a joint absolute motion command and return the response (blocking)."""

    data = make_joint_absolute_packet(
        absolute_position,
        speed_percentage,
        sequence_id,
        term_type,
        term_value,
    )
    
    send_command(client_socket, data)
    response = read_packet(reader)
    print(response)

def joint_absolute_trajectory(
    client_socket,
    reader: SocketJsonReader,
    qs: np.ndarray,
    speed_percentage: float,
    start_sequence_id: int = 1,
    term_value: int = 100,
) -> list[dict]:
    """
    Send joint motion commands to the robot and return the responses (non-blocking).

    Parameters
    ----------
    client_socket: socket.socket
        The socket to send the command to.
    reader: SocketJsonReader
        The reader to read the response from.
    qs: np.ndarray of shape (n_points, n_joints)
        The absolute joint coordinates to move to.
    speed_percentage: float
        The speed percentage to use for the motion.
    start_sequence_id: int
        The sequence ID to start the motion from.
    term_value: int
        The term value used for CNT termination.

    Returns
    -------
    list[dict]
        The list of responses from the robot.
    """
    n = qs.shape[0]

    outstanding = deque()
    next_to_send = 0
    responses = []

    def send_one(i: int):
        term_type: Literal["FINE", "CNT"] = "FINE" if i == n - 1 else "CNT"
        packet = make_joint_absolute_packet(
            absolute_position={f"J{j+1}": qs[next_to_send, j] for j in range(qs.shape[1])},
            speed_percentage=speed_percentage,
            sequence_id=start_sequence_id + next_to_send,
            term_type=term_type,
            term_value=term_value,
        )
        send_command(client_socket, packet)
        outstanding.append(i + 1)

    # Fill buffer with first few coordinates
    initial_fill = min(MAX_RMI_BUFFER, n)
    for _ in range(initial_fill):
        send_one(next_to_send)
        next_to_send += 1

    # For each completed instruction, send a new one
    while outstanding:
        response = read_packet(reader)
        responses.append(response)

        returned_seq = response.get("SequenceID")
        if returned_seq is not None:
            outstanding.popleft()

        if next_to_send < n:
            send_one(next_to_send)
            next_to_send += 1

    return responses


def speed_override(client_socket, reader: SocketJsonReader, value: int):
    """Set the speed override percentage."""

    data = {"Command": "FRC_SetOverRide", "Value": value}
    send_command(client_socket, data)
    response = read_packet(reader)
    print(response)


def wait_time(client_socket, reader: SocketJsonReader, seconds: float, sequence_id: int = 1):
    """Wait for the specified number of seconds."""

    data = {"Instruction": "FRC_WaitTime", "SequenceID": sequence_id, "Time": seconds}
    send_command(client_socket, data)
    response = read_packet(reader)
    print(response)


def set_uframe(client_socket, reader: SocketJsonReader, frame_number: int, sequence_id: int = 1):
    """Queue a TP instruction that sets the active UFRAME_NUM."""
    data = {
        "Instruction": "FRC_SetUFrame",
        "SequenceID": int(sequence_id),
        "FrameNumber": int(frame_number),
    }
    send_command(client_socket, data)
    response = read_packet(reader)
    print(response)
    return response


def set_utool(client_socket, reader: SocketJsonReader, tool_number: int, sequence_id: int = 1):
    """Queue a TP instruction that sets the active UTOOL_NUM."""
    data = {
        "Instruction": "FRC_SetUTool",
        "SequenceID": int(sequence_id),
        "ToolNumber": int(tool_number),
    }
    send_command(client_socket, data)
    response = read_packet(reader)
    print(response)
    return response
