import time

from .connection import SocketJsonReader, connect_with_retry, send_command
from .motions import (
    linear_relative,
    linear_absolute,
    joint_relative,
    joint_absolute,
    speed_override,
    wait_time,
)
from .pose_reader import (
    read_cartesian_coordinates,
    read_joint_coordinates,
    get_uframe_utool,
    read_uframe_data,
    write_uframe_data,
    read_utool_data,
    write_utool_data,
)
from .kinematics import convert_coordinates


class RobotClient:
    def __init__(self, host: str = "192.168.1.22", startup_port: int = 16001, main_port: int = 16002, connect_timeout: float = 5.0, socket_timeout: float = 100.0, reader_timeout: float = 100.0, attempts: int = 5, retry_delay: float = 0.5, startup_pause: float = 0.25):
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

        response = send_command(startup_socket, startup_reader, {"Communication": "FRC_Connect"})
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
            {"Command": "FRC_SetUFrameUTool", "UFrameNumber": uframe, "UToolNumber": utool}
        ]

        for command in commands:
            if self.client_socket is None or self.reader is None:
                raise RuntimeError("Client socket or reader is not connected.")
            response = send_command(self.client_socket, self.reader, command)
            print(response)

    def linear_relative(self, relative_displacement: dict, speed: float, sequence_id: int = 1, uframe: int = 1, utool: int = 1):
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

    def linear_absolute(self, absolute_position: dict, speed: float, sequence_id: int = 1, uframe: int = 1, utool: int = 1):
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

    def joint_relative(self, relative_displacement: dict, speed_percentage: float, sequence_id: int = 1, uframe: int = 1, utool: int = 1):
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        joint_relative(
            self.client_socket,
            self.reader,
            relative_displacement,
            speed_percentage,
            sequence_id,
            uframe=uframe,
            utool=utool,
        )

    def joint_absolute(self, absolute_position: dict, speed_percentage: float, sequence_id: int = 1, uframe: int = 1, utool: int = 1):
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        joint_absolute(
            self.client_socket,
            self.reader,
            absolute_position,
            speed_percentage,
            sequence_id,
            uframe=uframe,
            utool=utool,
        )

    def speed_override(self, value: int):
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        speed_override(self.client_socket, self.reader, value)

    def wait_time(self, seconds: float, sequence_id: int = 1):
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        wait_time(self.client_socket, self.reader, seconds, sequence_id)

    def abort(self):
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        response = send_command(self.client_socket, self.reader, {"Command": "FRC_Abort"})
        print(response)
        return response

    def read_cartesian_coordinates(self, output_path: str = "./robot_position_cartesian.txt"):
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        return read_cartesian_coordinates(self.client_socket, self.reader, output_path=output_path)

    def read_joint_coordinates(self, output_path: str = "./robot_position_joint.txt"):
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        return read_joint_coordinates(self.client_socket, self.reader, output_path=output_path)

    def get_uframe_utool(self) -> dict:
        if self.client_socket is None or self.reader is None:
            raise RuntimeError("Client socket or reader is not connected.")
        return get_uframe_utool(self.client_socket, self.reader)

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


    def close(self):
        if self.client_socket and self.reader:
            response = send_command(self.client_socket, self.reader, {"Communication": "FRC_Disconnect"})
            print(response)

            self.client_socket.close()
            print(f"- disconnected from port {self.main_port}")

            self.client_socket = None
            self.reader = None
