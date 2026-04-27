# fanuc-rmi

Python client for FANUC RMI over TCP sockets.

## Requirements

- Python `>=3.11`
- FANUC controller with RMI option enabled
- Network access from this machine to the controller

## Install

From PyPI:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fanuc-rmi
```

From this repository:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Quick Start

```python
from fanuc_rmi import RobotClient

robot = RobotClient(host="192.168.1.22")
robot.connect()

try:
    robot.initialize(uframe=0, utool=1)
    print(robot.get_uframe_utool())
finally:
    robot.close()
```

## Connection Lifecycle

- `connect()` does a two-step handshake:
  - Connects to startup port (`16001` by default)
  - Sends `FRC_Connect`
  - Reads the runtime port from the response (`Port`) and reconnects there
- `close()` sends `FRC_Disconnect` and closes the runtime socket.
- `abort()` sends `FRC_Abort`.

## RobotClient Parameters

`RobotClient(...)` supports:

- `host="192.168.1.22"`
- `startup_port=16001`
- `main_port=16002` (updated automatically from startup handshake if controller returns `Port`)
- `connect_timeout=5.0`
- `socket_timeout=60.0`
- `reader_timeout=60.0`
- `attempts=5`
- `retry_delay=0.5`
- `startup_pause=0.25`

## Initialization Behavior

`initialize(uframe, utool)` sends:

1. `FRC_Reset`
2. `FRC_Initialize`
3. `FRC_SetUFrameUTool`

## Motion APIs

```python
# speed override
robot.speed_override(20)

# sequence-ordered wait
robot.wait_time(0.5, sequence_id=1)

# linear relative (mm / deg)
robot.linear_relative(
    {"X": 10, "Y": 0, "Z": 0, "W": 0, "P": 0, "R": 0},
    speed=150,
    sequence_id=2,
    uframe=0,
    utool=1,
)

# linear absolute (mm / deg)
robot.linear_absolute(
    {"X": 540, "Y": -150, "Z": 500, "W": -170, "P": 0, "R": 165},
    speed=150,
    sequence_id=3,
    uframe=0,
    utool=1,
)

# joint relative (deg)
robot.joint_relative(
    {"J1": 0, "J2": 0, "J3": 0, "J4": 0, "J5": 0, "J6": 0, "J7": 0, "J8": 0, "J9": 0},
    speed_percentage=20,
    sequence_id=4,
    uframe=0,
    utool=1,
)

# joint absolute (deg)
robot.joint_absolute(
    {"J1": 0, "J2": 0, "J3": 0, "J4": 0, "J5": 0, "J6": 0},
    speed_percentage=20,
    sequence_id=5,
    uframe=0,  # accepted for API consistency
    utool=1,   # accepted for API consistency
)
```

Notes:

- Motion defaults are `uframe=0`, `utool=1`.
- `linear_*` include frame/tool inside `Configuration`.
- `joint_relative` and `joint_absolute` use joint-space payload (`JointAngle`) and do not include `Configuration`.

## Frame/Tool Selection

There are two ways to set frame/tool values:

1. Immediate controller selection command:

```python
robot.set_uframe_utool(uframe=1, utool=1)
```

Use this only when robot motion is stopped.

2. Queued TP instructions in the instruction stream:

```python
sid = 1

robot.linear_absolute(pose0, speed=150, sequence_id=sid, uframe=0, utool=1)
sid += 1

robot.set_uframe(frame_number=1, sequence_id=sid)
sid += 1
robot.set_utool(tool_number=1, sequence_id=sid)
sid += 1

robot.linear_absolute(pose1, speed=150, sequence_id=sid, uframe=1, utool=1)
```

For mixed-frame jobs, use strictly increasing `SequenceID` values for all queued instructions and moves.

## Read/Write APIs

```python
# current pose/joints (also appended to JSONL files)
cartesian_packet = robot.read_cartesian_coordinates()  # ./robot_position_cartesian.jsonl
joint_packet = robot.read_joint_coordinates()          # ./robot_position_joint.jsonl

# custom output paths are supported
robot.read_cartesian_coordinates(output_path="./logs/cartesian.jsonl")
robot.read_joint_coordinates(output_path="./logs/joints.jsonl")

# active frame/tool selection
active = robot.get_uframe_utool()

# frame/tool records (normalized to X/Y/Z/W/P/R floats)
uframe_1 = robot.read_uframe_data(1)
utool_1 = robot.read_utool_data(1)

robot.write_uframe_data(2, {"X": 0, "Y": 0, "Z": 0, "W": 0, "P": 0, "R": 0})
robot.write_utool_data(3, {"X": 10, "Y": 0, "Z": 120, "W": 0, "P": 0, "R": 0})

# digital I/O
din_packet = robot.read_din(1)
robot.write_dout(1, "ON")   # also accepts True
robot.write_dout(1, "OFF")  # also accepts False

# latest controller error packet
error_packet = robot.read_error()
```

`write_uframe_data(...)` and `write_utool_data(...)` require all keys: `X`, `Y`, `Z`, `W`, `P`, `R`.
`write_dout(...)` requires `ON`/`OFF` or a bool.
`read_din(...)` adds `ControllerError` to the returned packet when the DIN response has nonzero `ErrorID`.

## Numbering Notes

- `UFRAME` selection supports `0..9`.
- `UFRAME 0` is the controller world/default frame.
- `FRC_ReadUFrameData` / `FRC_WriteUFrameData` are typically used with `1..9`.
- `UTOOL` on this setup is `1..9`.

## Troubleshooting

If you see `RMI_MOVE invalid frame number`:

- Confirm the frame exists and is valid on the controller.
- For runtime frame changes, queue `set_uframe` / `set_utool` before the move.
- Keep `SequenceID` monotonic across all packets.
- Do not call `set_uframe_utool` while motion is active.

If you see connection timeouts:

- Verify controller and PC are on reachable network/subnet.
- Increase `connect_timeout`, `socket_timeout`, `reader_timeout`, and `attempts`.
- Check whether the controller is returning a different runtime port during `FRC_Connect`.

## Extras

`configuration_visualization.py` provides a GUI to inspect and visualize FANUC configuration bits (`Front/Up/Left/Flip`, `Turn4/5/6`), including loading the latest packet from `robot_position_cartesian.jsonl`.
