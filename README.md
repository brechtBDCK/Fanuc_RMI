# fanuc-rmi

Python client for FANUC RMI over TCP sockets. Tested on a CRX10i-A/L

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

robot = RobotClient(host="192.168.1.22")
robot.connect()

try:
    robot.initialize(uframe=1, utool=1)
    robot.speed_override(20) #speed percentage of the movement
    robot.read_joint_coordinates()

    #go to home position.
    robot.joint_absolute({"J1": 0, "J2": 0, "J3": 0, "J4": 0, "J5": 0, "J6": 0},speed_percentage=40,sequence_id=1)

finally:
    robot.close()
```

## RobotClient

`RobotClient` is the main API. It manages the startup socket, runtime socket, JSON reader, command sending, and disconnect.

Constructor parameters:

- `host="192.168.1.22"`: controller IP/host.
- `startup_port=16001`: port used for `FRC_Connect`.
- `main_port=16002`: runtime port, overwritten when `FRC_Connect` returns `Port`.
- `connect_timeout=5.0`: TCP connect timeout.
- `socket_timeout=60.0`: socket read/write timeout after connect.
- `reader_timeout=60.0`: JSON reader timeout.
- `attempts=5`: connection retry count.
- `retry_delay=0.5`: delay between connection attempts.
- `startup_pause=0.25`: pause between startup disconnect and runtime connect.


## Motion Instruction Functions

Motion calls enqueue FANUC RMI instructions unless noted otherwise. Use increasing
`sequence_id` values when mixing moves, waits, and frame/tool changes.

| Function                                                                                    | RMI instruction | Payload                                          | Speed     |
|---------------------------------------------------------------------------------------------| --- |--------------------------------------------------|-----------|
| `linear_relative(relative_displacement, speed, sequence_id=1, uframe=0, utool=1)`           | `FRC_LinearRelative` | Relative pose with `X`, `Y`, `Z`, `W`, `P`, `R`  | `mmSec`   |
| `linear_absolute(absolute_position, speed, sequence_id=1, uframe=0, utool=1)`               | `FRC_LinearMotion` | Absolute pose with `X`, `Y`, `Z`, `W`, `P`, `R`  | `mmSec`   |
| `joint_relative(relative_displacement, speed_percentage, sequence_id=1, uframe=1, utool=1)` | `FRC_JointRelativeJRep` | Relative joints with `J1` through `J9` as needed | `Percent` |
| `joint_absolute(absolute_position, speed_percentage, sequence_id=1, uframe=1, utool=1)`     | `FRC_JointMotionJRep` | Absolute joints with `J1` through `J9` as needed | `Percent` |
| `joint_absolute_trajectory(qs, speed_percentage, start_sequence_id=1, term_value=100)`      | `FRC_JointMotionJRep` | Absolute joints over points of the trajectory    | `Percent` |


| Function | RMI instruction | Behavior |
| --- | --- | --- |
| `speed_override(value)` | `FRC_SetOverRide` | Sets controller speed override percentage immediately. |
| `wait_time(seconds, sequence_id=1)` | `FRC_WaitTime` | Queues a timed wait in the instruction stream. |
| `set_uframe(frame_number, sequence_id=1)` | `FRC_SetUFrame` | Queues user-frame selection in the instruction stream. |
| `set_utool(tool_number, sequence_id=1)` | `FRC_SetUTool` | Queues tool-frame selection in the instruction stream. |

## Read/Write Functions

Read/write calls send controller requests directly and return the controller
response or normalized data, depending on the function.

| Function | RMI instruction | Returns / writes |
| --- | --- | --- |
| `read_cartesian_coordinates(output_path="./robot_position_cartesian.jsonl")` | `FRC_ReadCartesianPosition` | Full response packet; appends packet to JSONL. |
| `read_joint_coordinates(output_path="./robot_position_joint.jsonl")` | `FRC_ReadJointAngles` | Full response packet; appends packet to JSONL. |
| `get_uframe_utool()` | `FRC_GetUFrameUTool` | `{"UFrameNumber": ..., "UToolNumber": ...}` |
| `set_uframe_utool(uframe, utool)` | `FRC_SetUFrameUTool` | Selected frame/tool numbers after immediate controller update. |
| `read_uframe_data(frame_number)` | `FRC_ReadUFrameData` | Normalized frame data as `X`, `Y`, `Z`, `W`, `P`, `R` floats. |
| `write_uframe_data(frame_number, frame)` | `FRC_WriteUFrameData` | Writes frame data; `frame` must include `X`, `Y`, `Z`, `W`, `P`, `R`. |
| `read_utool_data(tool_number)` | `FRC_ReadUToolData` | Normalized tool data as `X`, `Y`, `Z`, `W`, `P`, `R` floats. |
| `write_utool_data(tool_number, frame)` | `FRC_WriteUToolData` | Writes tool data; `frame` must include `X`, `Y`, `Z`, `W`, `P`, `R`. |
| `read_error(response_prev_command)` | `FRC_ReadError` | Error packet when `ErrorID` is nonzero; otherwise `{}`. |
| `read_din(port_number)` | `FRC_ReadDIN` | Full digital-input response packet. |
| `write_dout(port_number, port_value)` | `FRC_WriteDOUT` | Writes digital output; accepts `"ON"`, `"OFF"`, `True`, or `False`. |


## Example code: Motion 

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
    uframe=1,
    utool=1,
)

# linear absolute (mm / deg)
robot.linear_absolute(
    {"X": 540, "Y": -150, "Z": 500, "W": -170, "P": 0, "R": 165},
    speed=150,
    sequence_id=3,
    uframe=1,
    utool=1,
)

# joint relative (deg)
robot.joint_relative(
    {"J1": 0, "J2": 0, "J3": 0, "J4": 0, "J5": 0, "J6": 0},
    speed_percentage=20,
    sequence_id=4,
)

# joint absolute (deg)
robot.joint_absolute(
    {"J1": 0, "J2": 0, "J3": 0, "J4": 0, "J5": 0, "J6": 0},
    speed_percentage=20,
    sequence_id=5,
)

# Joint trajectory (deg)
qs = np.array([[0, 0, 0, 0, 0, 0],
               [10, 0, 0, 0, 0, 0], 
               [20, 0, 10, 0, 0, 0]])
robot.joint_absolute_trajectory(
    qs,
    speed_percentage=20,
    start_sequence_id=6,
    term_value=100,
)
```

Motion notes:

- `linear_*` commands include `Configuration` with `UFrameNumber`, `UToolNumber`, `Front`, `Up`, `Left`, `Flip`, `Turn4`, `Turn5`, and `Turn6`.
- `joint_*` commands use joint-space payloads (`JointAngle`) and ignore frame/tool arguments. Those arguments exist only for API consistency.
- Default linear frame/tool is `uframe=0`, `utool=1`.
- Default `RobotClient` joint frame/tool arguments are `uframe=1`, `utool=1`, but they are ignored by the payload.
- `joint_absolute_trajectory` sends a series of `FRC_JointMotionJRep` instructions with `SequenceID` values starting at `start_sequence_id` and incrementing by 1 for each point. It sends a `term_type` of `CNT` for every point, except for the last point in the trajectory. The last point's `term_type` is `FINE`.

## Example code: Frame/Tool Selection

Immediate controller selection:

```python
robot.set_uframe_utool(uframe=1, utool=1)
```

Use this only when robot motion is stopped.

Queued TP instructions in the instruction stream:

```python
sid = 1

robot.linear_absolute(pose0, speed=150, sequence_id=sid, uframe=1, utool=1)
sid += 1

robot.set_uframe(frame_number=1, sequence_id=sid)
sid += 1
robot.set_utool(tool_number=1, sequence_id=sid)
sid += 1

robot.linear_absolute(pose1, speed=150, sequence_id=sid, uframe=1, utool=1)
```

For mixed-frame jobs, use strictly increasing `SequenceID` values for all queued instructions and moves.

## Example code: Read/Write 

```python
# current pose/joints, also appended to JSONL files
cartesian_packet = robot.read_cartesian_coordinates()
joint_packet = robot.read_joint_coordinates()

# custom output paths
robot.read_cartesian_coordinates(output_path="./logs/cartesian.jsonl")
robot.read_joint_coordinates(output_path="./logs/joints.jsonl")

# active frame/tool selection
active = robot.get_uframe_utool()
robot.set_uframe_utool(uframe=1, utool=1)

# frame/tool records
uframe_1 = robot.read_uframe_data(1)
utool_1 = robot.read_utool_data(1)

robot.write_uframe_data(2, {"X": 0, "Y": 0, "Z": 0, "W": 0, "P": 0, "R": 0})
robot.write_utool_data(3, {"X": 10, "Y": 0, "Z": 120, "W": 0, "P": 0, "R": 0})

# digital I/O
din_packet = robot.read_din(81)
robot.write_dout(1, "ON")
robot.wait_time(5, sequence_id=1)
robot.write_dout(1, False)

# read error for a response packet
error_packet = robot.read_error(din_packet)
```

Validation notes:

- `write_uframe_data(...)` and `write_utool_data(...)` require all keys: `X`, `Y`, `Z`, `W`, `P`, `R`.
- Frame/tool read functions fill missing controller frame values with `0.0`.
- `write_dout(...)` requires `"ON"`, `"OFF"`, `True`, or `False`.
- Read functions call `FRC_ReadError` internally when the returned packet has nonzero `ErrorID`, but they return the original response packet.


## Numbering caveat

- `UFRAME` selection supports `0..9`. However, frame 0 is an internal fanuc frame and should not be used. **Instead, always start at UFRAME 1.**
- `UFRAME 0` is the controller world/default frame, and is NOT to be used by the user
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


## Extra functionality

Run the configuration visualizer:

```bash
python3 configuration_visualization.py
```

`configuration_visualization.py` provides a Tkinter GUI for FANUC configuration bits:

- Toggle `Front`, `Up`, `Left`, and `Flip`.
- Adjust `Turn4`, `Turn5`, and `Turn6`.
- View generated RMI `Configuration` JSON.
- Load the latest `Configuration` from `robot_position_cartesian.jsonl` or another JSONL path.
- Reset values to defaults.

The repository also includes:

- `main.py`: small runnable example for connect, initialize, DIN read, DOUT write, wait, and close.
- `Documentation/`: bundled FANUC manuals and error code PDF references.
- `robot_models/crx10ial/`: CRX-10iA/L URDF and mesh files.

