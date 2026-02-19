# FANUC RMI Client

Python client for FANUC RMI with reusable functions (no CLI entrypoint).

**Install (pip)**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fanuc-rmi
```

**Robot URDF files**
Large datasets can be found here: `https://github.com/Daniella1/urdf_files_dataset?tab=readme-ov-file`

**Quick Start**
```python
from fanuc_rmi import RobotClient

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

robot.connect()
robot.initialize(uframe=0, utool=1)

# Do work...

robot.close()
```

**Motion Commands**
```python
# set speed override (controller-specific range)
robot.speed_override(50)

# wait in seconds (uses sequence_id for ordering)
robot.wait_time(2.5, sequence_id=5)

# linear relative motion (mm / deg)
relative_displacement = {"X": 100, "Y": 0, "Z": 0, "W": 0, "P": 0, "R": 0}
robot.linear_relative(relative_displacement, speed=500, sequence_id=1)

# linear absolute motion (mm / deg)
absolute_position = {"X": 491.320, "Y": -507.016, "Z": 223.397, "W": -179.577, "P": 52.380, "R": -93.233}
robot.linear_absolute(absolute_position, speed=300, sequence_id=2)

# joint relative motion (deg)
relative_joints = {"J0": 0, "J1": 0, "J2": 0, "J3": 0, "J4": 0, "J5": 0, "J6": 0, "J7": 0, "J8": 0, "J9": 0}
robot.joint_relative(relative_joints, speed_percentage=40, sequence_id=3)

# joint absolute motion (deg)
absolute_joints = {"J1": 63.252, "J2": 31.488, "J3": -35.602, "J4": 18.504, "J5": -101.313, "J6": 108.650, "J7": 0.000, "J8": 0.000, "J9": 0.000}
robot.joint_absolute(absolute_joints, speed_percentage=40, sequence_id=4)
```

**Read Positions (writes file + returns dict)**
```python
cartesian = robot.read_cartesian_coordinates()
# writes to ./robot_position_cartesian.txt

joints = robot.read_joint_coordinates()
# writes to ./robot_position_joint.txt
```

**Coordinate Conversion (IKPy)**
```python
urdf_path = "robot_models/crx10ial/crx10ial.urdf"
cartesian = robot.read_cartesian_coordinates()
joints = robot.convert_coordinates(cartesian, robot_model_urdf_path=urdf_path, from_type="cartesian", to_type="joint")

cartesian_again = robot.convert_coordinates(joints, robot_model_urdf_path=urdf_path, from_type="joint", to_type="cartesian")
```

**Output Files**
- `robot_position_cartesian.txt`: created automatically when reading Cartesian poses
- `robot_position_joint.txt`: created automatically when reading joint poses

**Notes**
- Requires Python 3.11+.
- `convert_coordinates` requires `ikpy` (`pip install ikpy`).
- Coordinate conversion always uses W/P/R. Provide W/P/R in your input dicts (missing values default to `0.0`).
- Joint dicts must use ascending `J` keys (`J1`, `J2`, `J3`, ...). The function assumes that order matches the URDF joint order.
- URDF units are often meters. If your robot reports millimeters, you may need to scale values before conversion.
- If you cloned the repo, `main.py` is a runnable example.
- For back-to-back moves, increment `sequence_id` to preserve ordering.
