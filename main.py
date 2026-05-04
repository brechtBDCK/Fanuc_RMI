import json
import re

from fanuc_rmi import RobotClient


robot = RobotClient(host="192.168.1.22", startup_port=16001, main_port=16002)

robot.connect()
robot.initialize(uframe=1, utool=1) #uframe 1 is "universe"
robot.speed_override(20)

# robot.linear_absolute({"X": 540, "Y": -150, "Z": 500, "W": -170, "P": 0, "R": 165}, speed=150, sequence_id=1, uframe=1, utool=1)
# robot.joint_relative({"J1": -20, "J2": 0, "J3": 0, "J4": 0, "J5": 0, "J6": 0}, speed_percentage=40, sequence_id=1, uframe=1, utool=1)


# cartesian = robot.read_cartesian_coordinates()  # Read current pose after each command to verify execution
# cartesian["Position"]["Z"] += 100  # Move up by 100mm
# print(cartesian)

# robot.joint_absolute({"J1": 0, "J2": 0, "J3": 0, "J4": 0, "J5": 0, "J6": 0}, speed_percentage=40, sequence_id=1, uframe=1, utool=1)

# robot.read_din(81)  # Read digital input 1
# robot.write_dout(1, "ON")  # Set digital output RO-1 to True
# robot.wait_time(5,sequence_id=1)
# robot.write_dout(1, "OFF")  # Remember to put register to OFF after operation 
# robot.wait_time(2,sequence_id=2)

robot.close()
