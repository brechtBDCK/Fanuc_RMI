# FANUC RMI Client

Python client for FANUC RMI with reusable functions (no CLI entrypoint).

**Install (pip)**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fanuc-rmi
```

**Create Client + Connect**
```python
from fanuc_rmi import RobotClient

# create client (no network calls yet)
robot = RobotClient(
    host="192.168.1.22",
    startup_port=16001,
    main_port=16002,
    connect_timeout=5.0,
    socket_timeout=100.0,
    reader_timeout=100.0,
    attempts=5,
    retry_delay=0.5,
    startup_pause=0.25,
)

robot.connect()            # returns None
robot.initialize(uframe=0, utool=1)  # returns None
```

**Speed Override**
```python
# set speed override (controller-specific range)
robot.speed_override(50)  # returns None
```

**Linear Relative Motion**
```python
# move relative to current pose (mm / deg)
relative_displacement = {"X": 100, "Y": 0, "Z": 0, "W": 0, "P": 0, "R": 0}
robot.linear_relative(relative_displacement, speed=500, sequence_id=1)  # mm/sec, returns None
```

**Linear Absolute Motion**
```python
# move to absolute pose (mm / deg)
absolute_position = {"X": 491.320, "Y": -507.016, "Z": 223.397, "W": -179.577, "P": 52.380, "R": -93.233}
robot.linear_absolute(absolute_position, speed=300, sequence_id=2)  # mm/sec, returns None
```

**Joint Relative Motion**
```python
# move joints relative to current (deg)
relative_joints = {"J0": 0, "J1": 0, "J2": 0, "J3": 0, "J4": 0, "J5": 0, "J6": 0, "J7": 0, "J8": 0, "J9": 0}
robot.joint_relative(relative_joints, speed_percentage=40, sequence_id=3)  # returns None
```

**Joint Absolute Motion**
```python
# move to absolute joint angles (deg)
absolute_joints = {"J1": 63.252, "J2": 31.488, "J3": -35.602, "J4": 18.504, "J5": -101.313, "J6": 108.650, "J7": 0.000, "J8": 0.000, "J9": 0.000}
robot.joint_absolute(absolute_joints, speed_percentage=40, sequence_id=4)  # returns None
```

**Read Cartesian Position (writes file)**
```python
robot.read_cartesian_coordinates()  # returns None
# writes to ./robot_position_cartesian.txt (auto-created)
```

**Read Joint Angles (writes file)**
```python
robot.read_joint_coordinates()  # returns None
# writes to ./robot_position_joint.txt (auto-created)
```


**Disconnect**
```python
robot.close()  # returns None
```

**Output Files**
- `robot_position_cartesian.txt`: created automatically when reading Cartesian poses
- `robot_position_joint.txt`: created automatically when reading joint poses

**Notes**
- Requires Python 3.11+.
- If you cloned the repo, `main.py` is a runnable example.
- For back-to-back moves, increment `sequence_id` to preserve ordering.
