from pathlib import Path

from .connection import SocketJsonReader, send_command


def request_current_position(client_socket, reader: SocketJsonReader) -> dict:
    """Request the current Cartesian position from the robot."""
    data = {"Command": "FRC_ReadCartesianPosition"}
    return send_command(client_socket, reader, data)


def read_cartesian_coordinates(client_socket, reader: SocketJsonReader, output_path: str = "./robot_position_cartesian.txt"):
    """Send a command to read the robot's Cartesian position."""
    response = request_current_position(client_socket, reader)
    print(response)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

    # Extract position data
    position = response.get("Position", {})
    if position:
        # Format the position data
        formatted_position = (
            f"X: {position.get('X', 0):.3f}, Y: {position.get('Y', 0):.3f}, Z: {position.get('Z', 0):.3f}, "
            f"W: {position.get('W', 0):.3f}, P: {position.get('P', 0):.3f}, R: {position.get('R', 0):.3f}"
        )

        # Append to the text file with a pose number
        try:
            with path.open("r", encoding="utf-8") as file:
                lines = file.readlines()
                pose_count = sum(1 for line in lines if line.startswith("Pose #")) + 1
        except FileNotFoundError:
            pose_count = 1

        with path.open("a", encoding="utf-8") as file:
            file.write(f"Pose #{pose_count}:")
            file.write(formatted_position + "\n")

        print(f"Position data appended to {path.name} as Pose #{pose_count}")
    else:
        print("No position data available.")

def read_joint_coordinates(client_socket, reader: SocketJsonReader, output_path: str = "./robot_position_joint.txt"):
    """Send a command to read the robot's joint angles."""
    data = {"Command": "FRC_ReadJointAngles"}
    response = send_command(client_socket, reader, data)
    print(response)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

    # Extract joint data
    joints = response.get("JointAngle") or response.get("Joints") or {}
    if joints:
        # Format the joint data
        ordered_keys = [f"J{i}" for i in range(0, 10)]
        parts = [f"{key}: {float(joints[key]):.3f}" for key in ordered_keys if key in joints]
        if not parts:
            parts = [f"{key}: {float(value):.3f}" for key, value in joints.items()]
        formatted_joints = ", ".join(parts)

        # Append to the text file with a pose number
        try:
            with path.open("r", encoding="utf-8") as file:
                lines = file.readlines()
                pose_count = sum(1 for line in lines if line.startswith("Pose #")) + 1
        except FileNotFoundError:
            pose_count = 1

        with path.open("a", encoding="utf-8") as file:
            file.write(f"Pose #{pose_count}:")
            file.write(formatted_joints + "\n")

        print(f"Joint data appended to {path.name} as Pose #{pose_count}")
    else:
        print("No joint data available.")
    
