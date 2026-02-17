from .client import RobotClient


def build_client(
    host: str = "192.168.1.22",
    startup_port: int = 16001,
    main_port: int = 16002,
    connect_timeout: float = 5.0,
    socket_timeout: float = 100.0,
    reader_timeout: float = 100.0,
    attempts: int = 5,
    retry_delay: float = 0.5,
    startup_pause: float = 0.25,
):
    return RobotClient(
        host=host,
        startup_port=startup_port,
        main_port=main_port,
        connect_timeout=connect_timeout,
        socket_timeout=socket_timeout,
        reader_timeout=reader_timeout,
        attempts=attempts,
        retry_delay=retry_delay,
        startup_pause=startup_pause,
    )
