# FANUC RMI Client

Simple Python client for FANUC RMI with a small CLI and reusable functions.

**Install (pip)**
1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install fanuc-rmi`


**Basic Use (RobotClient)**
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

**Functions**
- `RobotClient.connect()` / `RobotClient.close()`
- `RobotClient.initialize(uframe=0, utool=1)`

**Motions (RobotClient)**
- `linear_relative(relative_displacement, speed)` — `relative_displacement` has `X, Y, Z, W, P, R` (mm/deg); `speed` is mm/s.
- `linear_absolute(absolute_position, speed)` — `absolute_position` has `X, Y, Z, W, P, R`; `speed` is mm/s.
- `joint_relative(relative_displacement, speed_percentage)` — `relative_displacement` has `J0..J9`; `speed_percentage` is % of max.
- `joint_absolute(absolute_position, speed_percentage)` — `absolute_position` has `J1..J9`; `speed_percentage` is % of max.

**Reads (RobotClient)**
- `read_cartesian_coordinates(output_path="./robot_position_cartesian.txt")` — appends a formatted Cartesian pose line; file auto-created.
- `read_joint_coordinates(output_path="./robot_position_joint.txt")` — appends a formatted joint pose line; file auto-created.
- `request_current_position()` — returns the raw response dict.


**Notes**
- Requires Python 3.11+.
- `robot_position_cartesian.txt` and `robot_position_joint.txt` are created automatically when you read positions.
