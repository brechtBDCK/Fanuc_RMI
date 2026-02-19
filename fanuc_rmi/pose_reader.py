from pathlib import Path

from .connection import SocketJsonReader, send_command


def read_cartesian_coordinates(client_socket, reader: SocketJsonReader, output_path: str = "./robot_position_cartesian.txt"):
    """Send a command to read the robot's Cartesian position and return it."""
    data = {"Command": "FRC_ReadCartesianPosition"}
    response = send_command(client_socket, reader, data)

    print(response)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

    # Extract position data
    position = response.get("Position", {})
    if position:
        position_data = {key: float(position.get(key, 0.0)) for key in ("X", "Y", "Z", "W", "P", "R")}
        # Format the position data
        formatted_position = (
            f"X: {position_data['X']:.3f}, Y: {position_data['Y']:.3f}, Z: {position_data['Z']:.3f}, "
            f"W: {position_data['W']:.3f}, P: {position_data['P']:.3f}, R: {position_data['R']:.3f}"
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
        return position_data
    else:
        print("No position data available.")
        return {}

def read_joint_coordinates(client_socket, reader: SocketJsonReader, output_path: str = "./robot_position_joint.txt"):
    """Send a command to read the robot's joint angles and return them."""
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
        ordered_items = [(key, float(joints[key])) for key in ordered_keys if key in joints]
        if ordered_items:
            joint_data = {key: value for key, value in ordered_items}
            parts = [f"{key}: {value:.3f}" for key, value in ordered_items]
        else:
            joint_data = {key: float(value) for key, value in joints.items()}
            parts = [f"{key}: {value:.3f}" for key, value in joint_data.items()]
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
        return joint_data
    else:
        print("No joint data available.")
        return {}
