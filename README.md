# fanuc-rmi

Python client for FANUC RMI over TCP sockets.

## Requirements

- Python `>=3.11`
- FANUC controller with RMI option enabled
- Network access from this machine to the controller

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fanuc-rmi
```

## Quick Start

```python
from fanuc_rmi import RobotClient

robot = RobotClient(host="192.168.1.22", startup_port=16001, main_port=16002)
robot.connect()
robot.initialize(uframe=0, utool=1)

print(robot.get_uframe_utool())

robot.close()
```

## Core Behavior

- `initialize(uframe, utool)` sends:
  - `FRC_Reset`
  - `FRC_Initialize`
  - `FRC_SetUFrameUTool`
- Motion calls (`linear_*`, `joint_relative`) include `Configuration.UFrameNumber` / `UToolNumber` in each packet.
- Defaults in motion APIs are `uframe=0`, `utool=1`.

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
)
```

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

## Read APIs

```python
# current pose/joints (also appended to JSONL files)
cartesian = robot.read_cartesian_coordinates()  # ./robot_position_cartesian.jsonl
joints = robot.read_joint_coordinates()         # ./robot_position_joint.jsonl

# active selection
active = robot.get_uframe_utool()

# frame/tool records
uframe_1 = robot.read_uframe_data(1)
utool_1 = robot.read_utool_data(1)

robot.write_uframe_data(2, {"X": 0, "Y": 0, "Z": 0, "W": 0, "P": 0, "R": 0})
robot.write_utool_data(3, {"X": 10, "Y": 0, "Z": 120, "W": 0, "P": 0, "R": 0})
```

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

## Extras

`configuration_visualization.py` provides a GUI to inspect and visualize FANUC configuration bits (`Front/Up/Left/Flip`, `Turn4/5/6`), including loading the latest packet from `robot_position_cartesian.jsonl`.
