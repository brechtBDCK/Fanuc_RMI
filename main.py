import json
import re

from fanuc_rmi import RobotClient


robot = RobotClient(host="192.168.1.22", startup_port=16001, main_port=16002)
robot.connect()
robot.initialize(uframe=0, utool=1)
robot.speed_override(20)

cartesian = robot.read_cartesian_coordinates()  # Read current pose after each command to verify execution
cartesian["Z"] += 100  # Move up by 100mm
print(cartesian)
# robot.joint_absolute({"J1": 0, "J2": 0, "J3": 0, "J4": 0, "J5": 0, "J6": 0}, speed_percentage=10, sequence_id=1, uframe=0, utool=1)
robot.close()
