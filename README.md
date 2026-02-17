# FANUC RMI Client

Simple Python client for FANUC RMI with a small CLI and reusable functions.

**Quick Start**
1. `git clone <your-repo-url>`
2. `cd ROBOT_fanuc_leuven`
3. `python3 -m venv .venv`
4. `source .venv/bin/activate`
5. `pip install -r requirements.txt`
6. Edit `config.toml` and set `controller.host` to your robot IP.
7. Run `fanuc-rmi` or `python main.py`

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

**Using From Another Project (Option A)**
1. Make sure you have this repo on disk (clone or copy).
2. Install it into your other project’s venv:
   `pip install -e /path/to/ROBOT_fanuc_leuven`
3. Import and use:
```python
from fanuc_rmi import RobotClient
```

**Install Directly From Git**
If the repo is hosted, another person can install it with:
`pip install git+<your-repo-url>`

**Lower-Level Imports**
You can also import specific functions if you prefer:
```python
from fanuc_rmi import joint_absolute, linear_relative
```

**Notes**
- Requires Python 3.11+ (uses `tomllib`).
- `fanuc-rmi` runs `main.py` as the CLI.
- If install fails, run `pip install -U pip setuptools wheel` and try again.
