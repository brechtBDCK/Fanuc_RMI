from fanuc_rmi import RobotClient

def main():
    client = RobotClient(host = "192.168.1.22",startup_port = 16001, main_port = 16002)
    client.connect()
    client.initialize(uframe=0, utool=1)
    client.speed_override(40)  # Set speed override to 40% (can be adjusted as needed)

    # Optional: Linear relative motion
    # relative_displacement = {"X": 100, "Y": 0, "Z": 0, "W": 0, "P": 0, "R": 0} #manually set the relative displacements
    # client.linear_relative(relative_displacement, speed=500, sequence_id=1) #speed is in mm/s
    
    # Optional: Linear absolute motion
    # absolute_position = {"X": 491.320, "Y": -507.016, "Z": 223.397, "W": -179.577, "P": 52.380, "R": -93.233} #manually set the absolute position
    # client.linear_absolute(absolute_position, speed=300, sequence_id=2)
    
    # Optional: Joint relative motion
    # relative_position = {"J0": 0, "J1": 0, "J2": 0, "J3": 0, "J4": 0, "J5": 0, "J6": 0, "J7": 0, "J8": 0, "J9": 0} #manually set the relative joint angles
    # client.joint_relative(relative_position, speed_percentage=40, sequence_id=3) #speed is percentage
    
    # Optional: Joint absolute motion
    absolute_position_1 = {"J1": 1.534, "J2": -70.678, "J3": 31.539, "J4": -163.759, "J5": 76.388, "J6": 224.917, "J7": 0.000, "J8": 0.000, "J9": 0.000} #manually set the absolute joint angles
    client.joint_absolute(absolute_position_1, speed_percentage=80, sequence_id=1) #speed is percentage
    absolute_position_2 = {"J1": 12.648, "J2": 59.326, "J3": -2.001, "J4": 2.868, "J5": -133.750, "J6": 103.221, "J7": 0.000, "J8": 0.000, "J9": 0.000} #manually set the absolute joint angles
    client.joint_absolute(absolute_position_2, speed_percentage=80, sequence_id=2) #speed is percentage
    
    # Optional: Read coordinates
    # client.read_cartesian_coordinates()
    # client.read_joint_coordinates()

    client.close()


if __name__ == "__main__":
    main()
