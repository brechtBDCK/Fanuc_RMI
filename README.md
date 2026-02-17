# FANUC RMI Client

Simple Python client for FANUC RMI with a small CLI and reusable functions.

**Quick Start**
1. `git clone <this-repo-url>`
2. `cd Fanuc_RMI`
3. `python3 -m venv .venv`
4. `source .venv/bin/activate`
5. Edit `config.toml` and set `controller.host` to your robot IP.
6. Run `python main.py`

**Basic Use (RobotClient)**
```python
from fanuc_rmi import RobotClient

client = RobotClient.from_config("config.toml")
client.connect()
client.initialize(uframe=0, utool=1)

absolute_position = {"J1": 63.252, "J2": 31.488, "J3": -35.602, "J4": 18.504, "J5": -101.313, "J6": 108.650, "J7": 0.000, "J8": 0.000, "J9": 0.000}
client.joint_absolute(absolute_position, speed_percentage=40)

client.close()
```

**Using From Another Project (No Pip Install)**
1. Make sure you have this repo on disk (clone or copy).
2. Add it to `PYTHONPATH` for your session:
   `export PYTHONPATH=/path/to/Fanuc_RMI:$PYTHONPATH`
3. Import and use:
```python
from fanuc_rmi import RobotClient
```

**Lower-Level Imports**
You can also import specific functions if you prefer:
```python
from fanuc_rmi import joint_absolute, linear_relative
```

**Notes**
- Requires Python 3.11+ (uses `tomllib`).
- `main.py` runs the example.
- `robot_position_cartesian.txt` and `robot_position_joint.txt` are created automatically when you read positions.
