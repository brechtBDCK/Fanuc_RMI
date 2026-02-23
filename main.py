from fanuc_rmi import RobotClient

def main():
    robot = RobotClient(host = "192.168.1.22",startup_port = 16001, main_port = 16002)
    robot.connect()
    robot.initialize(uframe=0, utool=1)
    robot.get_uframe_utool()
    robot.speed_override(20)  # Set speed override to 20% (can be adjusted as needed)

    # Optional: Linear relative motion
    # relative_displacement = {"X": 100, "Y": 0, "Z": 0, "W": 0, "P": 0, "R": 0} #manually set the relative displacements
    # robot.linear_relative(relative_displacement, speed=500, sequence_id=1, uframe= 0, utool = 1) #speed is in mm/s
    
    # Optional: Linear absolute motion
    # absolute_position = {'X': 262.799, 'Y': -250.636, 'Z': 540.085, 'W': -90.025, 'P': -81.432, 'R': -104.742} #manually set the absolute position
    # robot.linear_absolute(absolute_position, speed=300, sequence_id=1, uframe= 0, utool = 1)
    
    # Optional: Joint relative motion
    # relative_position = {"J0": 0, "J1": 0, "J2": 0, "J3": 0, "J4": 0, "J5": 0, "J6": 0, "J7": 0, "J8": 0, "J9": 0} #manually set the relative joint angles
    # robot.joint_relative(relative_position, speed_percentage=40, sequence_id=1, uframe= 0, utool = 1) #speed is percentage
    
    # Optional: Joint absolute motion
    absolute_position_1 = {'J1': 0.0, 'J2': 0, 'J3': 0, 'J4': 0, 'J5': 0, 'J6': 0, "J7": 0.000, "J8": 0.000, "J9": 0.000} #manually set the absolute joint angles
    robot.joint_absolute(absolute_position_1, speed_percentage=40, sequence_id=1, uframe= 0, utool = 1) #speed is percentage
    # robot.wait_time(5, sequence_id=2) #wait for 5 seconds before sending the next command
    # absolute_position_2 = {"J1": 12.648, "J2": 59.326, "J3": -2.001, "J4": 2.868, "J5": -133.750, "J6": 103.221, "J7": 0.000, "J8": 0.000, "J9": 0.000} #manually set the absolute joint angles
    # robot.joint_absolute(absolute_position_2, speed_percentage=80, sequence_id=3, uframe= 0, utool = 1) #speed is percentage
    
    # Optional: Read coordinates
    cartesian = robot.read_cartesian_coordinates() # saves to txt file and returns a dict
    joints = robot.read_joint_coordinates() # saves to txt file and returns a dict
    print("Cartesian coordinates:", cartesian)
    print("Joint coordinates:", joints)

    
    robot.close()


if __name__ == "__main__":
    main()
