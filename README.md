# FANUC RMI Client

Python client for FANUC RMI with reusable functions.

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

active = robot.get_uframe_utool()

robot.close()
```

## Motion Commands

All motion methods accept `uframe` and `utool` arguments (defaults are `1` and `1`).

```python
# set speed override (controller-specific range)
robot.speed_override(50)

# wait in seconds (uses sequence_id for ordering)
robot.wait_time(2.5, sequence_id=5)

# linear relative motion (mm / deg)
relative_displacement = {"X": 100, "Y": 0, "Z": 0, "W": 0, "P": 0, "R": 0}
robot.linear_relative(relative_displacement, speed=500, sequence_id=1, uframe=1, utool=1)

# linear absolute motion (mm / deg)
absolute_position = {
    "X": 491.320, "Y": -507.016, "Z": 223.397,
    "W": -179.577, "P": 52.380, "R": -93.233,
}
robot.linear_absolute(absolute_position, speed=300, sequence_id=2, uframe=1, utool=1)

# joint relative motion (deg)
relative_joints = {"J1": 0, "J2": 0, "J3": 0, "J4": 0, "J5": 0, "J6": 0, "J7": 0, "J8": 0, "J9": 0}
robot.joint_relative(relative_joints, speed_percentage=40, sequence_id=3, uframe=1, utool=1)

# joint absolute motion (deg)
absolute_joints = {
    "J1": 63.252, "J2": 31.488, "J3": -35.602,
    "J4": 18.504, "J5": -101.313, "J6": 108.650,
    "J7": 0.000, "J8": 0.000, "J9": 0.000,
}
robot.joint_absolute(absolute_joints, speed_percentage=40, sequence_id=4, uframe=1, utool=1)
```

## Read APIs

```python
# current pose (also appends to local jsonl files)
cartesian = robot.read_cartesian_coordinates()  # ./robot_position_cartesian.jsonl
joints = robot.read_joint_coordinates()         # ./robot_position_joint.jsonl

# active frame/tool selection on controller
active = robot.get_uframe_utool()

# frame/tool data records
uframe_1 = robot.read_uframe_data(1)
utool_1 = robot.read_utool_data(1)

robot.write_uframe_data(2, {"X": 0, "Y": 0, "Z": 0, "W": 0, "P": 0, "R": 0})
robot.write_utool_data(3, {"X": 10, "Y": 0, "Z": 120, "W": 0, "P": 0, "R": 0})
```

## UFRAME / UTOOL Numbering

- `UFRAME` selection supports `0..9`.
- `UFRAME 0` is the controller default/world frame (valid to select/use).
- `FRC_ReadUFrameData` / `FRC_WriteUFrameData` should use `1..9`. Using `0` may return an error.
- `UTOOL` selection is `1..9` on this setup.
- No practical `UTOOL 0` is used in this project.

## Notes

- Requires Python 3.11+.
- `main.py` is a runnable example script.
