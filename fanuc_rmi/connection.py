import json
import socket
import time
from typing import Optional


class SocketJsonReader:
    """Accumulate bytes from the socket until a CRLF-terminated JSON message arrives."""

    def __init__(self, sock: socket.socket, timeout: float = 15.0):
        self.sock = sock
        self.buffer = bytearray()
        self.sock.settimeout(timeout)

    def read_json(self):
        while True:
            newline_index = self._find_newline()
            if newline_index != -1:
                raw = bytes(self.buffer[:newline_index])
                del self.buffer[: newline_index + 2]  # remove CRLF
                raw_str = raw.decode("ascii").strip()
                if not raw_str:
                    continue
                return json.loads(raw_str)
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("Robot controller closed the connection unexpectedly")
            self.buffer.extend(chunk)

    def _find_newline(self) -> int:
        buf = self.buffer
        for i in range(len(buf) - 1):
            if buf[i] == 13 and buf[i + 1] == 10:  # CRLF
                return i
        return -1


def send_command(client_socket: socket.socket, reader: SocketJsonReader, data):
    """Send a command to the robot and return the response."""
    json_data = json.dumps(data) + "\r\n"
    client_socket.sendall(json_data.encode("ascii"))
    return reader.read_json()


def connect_with_retry(host: str, port: int, attempts: int = 5, delay: float = 0.5, connect_timeout: float = 5.0, socket_timeout: float = 5.0) -> socket.socket:
    """Retry connecting to the controller to avoid racing its startup."""
    last_error: Optional[Exception] = None
    for attempt in range(1, attempts + 1):
        try:
            sock = socket.create_connection((host, port), timeout=connect_timeout)
            sock.settimeout(socket_timeout)
            return sock
        except OSError as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(delay)
    raise RuntimeError(f"Unable to connect to {host}:{port} after {attempts} attempts") from last_error

