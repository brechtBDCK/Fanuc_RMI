import time
from typing import Literal

from .connection import SocketJsonReader, connect_with_retry, send_command, read_packet
from .motions import (
    linear_relative,
    linear_absolute,
    joint_relative,
    joint_absolute,
    speed_override,
    wait_time,
    set_uframe,
    set_utool,
)
from .pose_reader import (
    read_cartesian_coordinates,
    read_joint_coordinates,
    get_uframe_utool,
    set_uframe_utool,
    read_uframe_data,
    write_uframe_data,
    read_utool_data,
    write_utool_data,
    read_error,
    read_din,
    write_dout,
)


class RobotClient:
    def __init__(self, host: str = "192.168.1.22", startup_port: int = 16001, main_port: int = 16002, connect_timeout: float = 5.0, socket_timeout: float = 60.0, reader_timeout: float = 60.0, attempts: int = 5, retry_delay: float = 0.5, startup_pause: float = 0.25):
        self.host = host
        self.startup_port = startup_port
        self.main_port = main_port
        self.connect_timeout = connect_timeout
        self.socket_timeout = socket_timeout
        self.reader_timeout = reader_timeout
        self.attempts = attempts
        self.retry_delay = retry_delay
        self.startup_pause = startup_pause

        self.client_socket = None
        self.reader = None

    def connect(self):
        print("- started rmi client...")

        startup_socket = connect_with_retry(
            self.host,
            self.startup_port,
            attempts=self.attempts,
            delay=self.retry_delay,
            connect_timeout=self.connect_timeout,
            socket_timeout=self.socket_timeout,
        )
        startup_reader = SocketJsonReader(startup_socket, timeout=self.reader_timeout)
        print(f"- connected to startup port {self.startup_port}")

        send_command(startup_socket, {"Communication": "FRC_Connect"})
        response = read_packet(startup_reader)
        print(response)

        if "Port" in response:
            self.main_port = int(response["Port"])

        startup_socket.close()
        print(f"- disconnected from startup port {self.startup_port}")

        time.sleep(self.startup_pause)  # brief pause to let the controller finish spinning up the next port

        self.client_socket = connect_with_retry(
            self.host,
            self.main_port,
            attempts=self.attempts,
            delay=self.retry_delay,
            connect_timeout=self.connect_timeout,
            socket_timeout=self.socket_timeout,
        )
        self.reader = SocketJsonReader(self.client_socket, timeout=self.reader_timeout)
        print(f"- connected to port {self.main_port}")

    def initialize(self, uframe: int = 0, utool: int = 1):
        commands = [
            {"Command": "FRC_Reset"},
            {"Command": "FRC_Initialize"},
        ]

        for command in commands:
            if self.client_socket is None or self.reader is None:
                raise RuntimeError("Client socket or reader is not connected.")
            send_command(self.client_socket, command)
            response = read_packet(self.reader)
            print(response)
        self.set_uframe_utool(uframe=uframe, utool=utool)

    def linear_relative(self, relative_displacement: dict, speed: float, sequence_id: int = 1, uframe: int = 0, utool: int = 1):
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        linear_relative(
            self.client_socket,
            self.reader,
            relative_displacement,
            speed,
            sequence_id,
            uframe=uframe,
            utool=utool,
        )

    def linear_absolute(self, absolute_position: dict, speed: float, sequence_id: int = 1, uframe: int = 0, utool: int = 1):
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        linear_absolute(
            self.client_socket,
            self.reader,
            absolute_position,
            speed,
            sequence_id,
            uframe=uframe,
            utool=utool,
        )

    def joint_relative(self, relative_displacement: dict, speed_percentage: float, sequence_id: int = 1, term_type: Literal["FINE", "CNT"] = "FINE", term_value: int = 100):
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        joint_relative(
            self.client_socket,
            self.reader,
            relative_displacement,
            speed_percentage,
            sequence_id,
        )

    def joint_absolute(self, absolute_position: dict, speed_percentage: float, sequence_id: int = 1, term_type: Literal["FINE", "CNT"] = "FINE", term_value: int = 100):
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        joint_absolute(
            self.client_socket,
            self.reader,
            absolute_position,
            speed_percentage,
            sequence_id,
        )

    def speed_override(self, value: int):
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        speed_override(self.client_socket, self.reader, value)

    def wait_time(self, seconds: float, sequence_id: int = 1):
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        wait_time(self.client_socket, self.reader, seconds, sequence_id)

    def set_uframe(self, frame_number: int, sequence_id: int = 1) -> dict:
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        return set_uframe(self.client_socket, self.reader, frame_number, sequence_id)

    def set_utool(self, tool_number: int, sequence_id: int = 1) -> dict:
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        return set_utool(self.client_socket, self.reader, tool_number, sequence_id)

    def abort(self):
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        send_command(self.client_socket, {"Command": "FRC_Abort"})
        response = read_packet(self.reader)
        print(response)
        return response

    def read_cartesian_coordinates(self, output_path: str = "./robot_position_cartesian.jsonl"):
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        return read_cartesian_coordinates(self.client_socket, self.reader, output_path=output_path)

    def read_joint_coordinates(self, output_path: str = "./robot_position_joint.jsonl"):
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        return read_joint_coordinates(self.client_socket, self.reader, output_path=output_path)

    def get_uframe_utool(self) -> dict:
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        return get_uframe_utool(self.client_socket, self.reader)

    def set_uframe_utool(self, uframe: int, utool: int) -> dict:
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        return set_uframe_utool(self.client_socket, self.reader, uframe, utool)

    def read_uframe_data(self, frame_number: int) -> dict:
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        return read_uframe_data(self.client_socket, self.reader, frame_number)

    def write_uframe_data(self, frame_number: int, frame: dict) -> dict:
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        return write_uframe_data(self.client_socket, self.reader, frame_number, frame)

    def read_utool_data(self, tool_number: int) -> dict:
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        return read_utool_data(self.client_socket, self.reader, tool_number)

    def write_utool_data(self, tool_number: int, frame: dict) -> dict:
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        return write_utool_data(self.client_socket, self.reader, tool_number, frame)

    def read_error(self, response_prev_command) -> dict:
        if self.client_socket is None or self.reader is None or response_prev_command is None:
            # Return an empty dict to satisfy the return type
            return {}
        result = read_error(self.client_socket, self.reader, response_prev_command)
        if result is None:
            return {}
        return result

    def read_din(self, port_number: int) -> dict:
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        return read_din(self.client_socket, self.reader, port_number)

    def write_dout(self, port_number: int, port_value: str | bool) -> dict:
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        return write_dout(self.client_socket, self.reader, port_number, port_value)

    def close(self):
        if self.client_socket and self.reader:
            send_command(self.client_socket, {"Communication": "FRC_Disconnect"})
            response = read_packet(self.reader)
            print(response)

            self.client_socket.close()
            print(f"- disconnected from port {self.main_port}")

            self.client_socket = None
            self.reader = None
