# FANUC RMI Client

Python client for FANUC RMI with reusable functions (no CLI entrypoint).

**Install (pip)**
1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install fanuc-rmi`

**Quick Start**
```python
from fanuc_rmi import RobotClient

client = RobotClient(
    host="192.168.1.22",
    socket_timeout=100.0,
    reader_timeout=100.0,
)

client.connect()
client.initialize(uframe=0, utool=1)

absolute_position = {"J1": 63.252, "J2": 31.488, "J3": -35.602, "J4": 18.504, "J5": -101.313, "J6": 108.650, "J7": 0.000, "J8": 0.000, "J9": 0.000}
client.joint_absolute(absolute_position, speed_percentage=40)

client.close()
```

**Configuration (RobotClient args)**
- `host`: controller IP address
- `startup_port`: startup port, default `16001`
- `main_port`: main port, default `16002`
- `connect_timeout`: seconds for TCP connect
- `socket_timeout`: seconds for socket ops
- `reader_timeout`: seconds to wait for a JSON response
- `attempts`: number of retry attempts
- `retry_delay`: seconds between retries
- `startup_pause`: seconds between startup and main connections

**API Overview**
- `RobotClient(...)`: create a client, no network calls; returns a client instance
- `RobotClient.connect()`: connects to startup, sends `FRC_Connect`, then connects to main; prints responses; returns `None`
- `RobotClient.initialize(uframe=0, utool=1)`: sends `FRC_Reset`, `FRC_Initialize`, `FRC_SetUFrameUTool`; prints responses; returns `None`
- `RobotClient.close()`: sends `FRC_Disconnect` and closes sockets; returns `None`

**Motions (RobotClient)**
- `linear_relative(relative_displacement, speed)`: linear move relative to current pose; `X, Y, Z, W, P, R` (mm/deg); `speed` in mm/s; returns `None`
- `linear_absolute(absolute_position, speed)`: linear move to absolute pose; `X, Y, Z, W, P, R`; `speed` in mm/s; returns `None`
- `joint_relative(relative_displacement, speed_percentage)`: joint move relative; `J0..J9`; `speed_percentage` is % of max; returns `None`
- `joint_absolute(absolute_position, speed_percentage)`: joint move to absolute; `J1..J9`; `speed_percentage` is % of max; returns `None`

**Reads (RobotClient)**
- `read_cartesian_coordinates(output_path="./robot_position_cartesian.txt")`: sends `FRC_ReadCartesianPosition`, prints response, appends formatted pose line; returns `None`
- `read_joint_coordinates(output_path="./robot_position_joint.txt")`: sends `FRC_ReadJointAngles`, prints response, appends formatted joint line; returns `None`
- `request_current_position()`: sends `FRC_ReadCartesianPosition` and returns the raw response dict

**Output Files**
- `robot_position_cartesian.txt`: created automatically when reading Cartesian poses
- `robot_position_joint.txt`: created automatically when reading joint poses

**Notes**
- Requires Python 3.11+.
- If you cloned the repo, `main.py` is a runnable example.
