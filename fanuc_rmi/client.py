import time

from .config import load_config
from .connection import SocketJsonReader, connect_with_retry, send_command
from .motions import linear_relative, linear_absolute, joint_relative, joint_absolute
from .pose_reader import request_current_position, read_cartesian_coordinates, read_joint_coordinates


class RobotClient:
    def __init__(
        self,
        host: str = "192.168.1.22",
        startup_port: int = 16001,
        main_port: int = 16002,
        connect_timeout: float = 5.0,
        socket_timeout: float = 5.0,
        reader_timeout: float = 15.0,
        attempts: int = 5,
        retry_delay: float = 0.5,
        startup_pause: float = 0.25,
    ):
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

    @classmethod
    def from_config(cls, path: str = "config.toml"):
        config = load_config(path)

        controller_cfg = config.get("controller", {})
        connection_cfg = config.get("connection", {})
        timing_cfg = config.get("timing", {})

        return cls(
            host=controller_cfg.get("host", "192.168.1.22"),
            startup_port=controller_cfg.get("startup_port", 16001),
            main_port=controller_cfg.get("main_port", 16002),
            connect_timeout=connection_cfg.get("connect_timeout", 5.0),
            socket_timeout=connection_cfg.get("socket_timeout", 5.0),
            reader_timeout=connection_cfg.get("reader_timeout", 15.0),
            attempts=connection_cfg.get("attempts", 5),
            retry_delay=connection_cfg.get("retry_delay", 0.5),
            startup_pause=timing_cfg.get("startup_pause", 0.25),
        )

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
            response = send_command(self.client_socket, self.reader, command)
            print(response)

    def linear_relative(self, relative_displacement: dict, speed: float):
        linear_relative(self.client_socket, self.reader, relative_displacement, speed)

    def linear_absolute(self, absolute_position: dict, speed: float):
        linear_absolute(self.client_socket, self.reader, absolute_position, speed)

    def joint_relative(self, relative_displacement: dict, speed_percentage: float):
        joint_relative(self.client_socket, self.reader, relative_displacement, speed_percentage)

    def joint_absolute(self, absolute_position: dict, speed_percentage: float):
        joint_absolute(self.client_socket, self.reader, absolute_position, speed_percentage)

    def request_current_position(self):
        return request_current_position(self.client_socket, self.reader)

    def read_cartesian_coordinates(self, output_path: str = "./robot_position_cartesian.txt"):
        read_cartesian_coordinates(self.client_socket, self.reader, output_path=output_path)

    def read_joint_coordinates(self, output_path: str = "./robot_position_joint.txt"):
        read_joint_coordinates(self.client_socket, self.reader, output_path=output_path)

    def close(self):
        if self.client_socket:
            response = send_command(self.client_socket, self.reader, {"Communication": "FRC_Disconnect"})
            print(response)

            self.client_socket.close()
            print(f"- disconnected from port {self.main_port}")

            self.client_socket = None
            self.reader = None
