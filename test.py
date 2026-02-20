import numpy as np
from fanuc_rmi import RobotClient
from ikpy.chain import Chain

# =======================
# Config
# =======================
URDF_PATH = "/home/bdck/PROJECTS_WSL/Fanuc_RMI/robot_models/crx10ial/crx10ial.urdf"
WPR_ORDER = "XYZ"

# URDF fixed joint: base_link -> base has xyz="0 0 0.245" (meters)
T_BASELINK_TO_BASE = np.eye(4)
T_BASELINK_TO_BASE[2, 3] = 0.245  # +245mm in Z

# =======================
# Math helpers
# =======================
def rot_x(a):
    ca, sa = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0],
                     [0, ca, -sa],
                     [0, sa, ca]])

def rot_y(a):
    ca, sa = np.cos(a), np.sin(a)
    return np.array([[ca, 0, sa],
                     [0, 1, 0],
                     [-sa, 0, ca]])

def rot_z(a):
    ca, sa = np.cos(a), np.sin(a)
    return np.array([[ca, -sa, 0],
                     [sa, ca, 0],
                     [0, 0, 1]])

def wpr_to_R(w_deg, p_deg, r_deg, order="XYZ"):
    """
    FANUC pose gives W,P,R in degrees.
    This function assumes W->X, P->Y, R->Z rotations applied in 'order'.
    """
    w, p, r = np.deg2rad([w_deg, p_deg, r_deg])
    mats = {"X": rot_x, "Y": rot_y, "Z": rot_z}
    angles = {"X": w, "Y": p, "Z": r}

    Rm = np.eye(3)
    for ax in order:
        Rm = Rm @ mats[ax](angles[ax])
    return Rm

def pose_to_T_mm_deg(pose, order="XYZ"):
    """pose: {'X','Y','Z' in mm, 'W','P','R' in deg} -> 4x4 in meters."""
    T = np.eye(4)
    T[:3, 3] = np.array([pose["X"], pose["Y"], pose["Z"]]) / 1000.0
    T[:3, :3] = wpr_to_R(pose["W"], pose["P"], pose["R"], order=order)
    return T

def T_to_xyz_mm(T):
    xyz = T[:3, 3] * 1000.0
    return {"X": float(xyz[0]), "Y": float(xyz[1]), "Z": float(xyz[2])}

def xyz_error_mm(a_xyz, b_xyz):
    dx = a_xyz["X"] - b_xyz["X"]
    dy = a_xyz["Y"] - b_xyz["Y"]
    dz = a_xyz["Z"] - b_xyz["Z"]
    return {"dX": dx, "dY": dy, "dZ": dz, "norm": float(np.sqrt(dx*dx + dy*dy + dz*dz))}

def q_from_j6(chain, j6_deg):
    """
    Build IKPy joint vector q (len(chain.links)).
    Assumes the 6 revolute joints are at indices 1..6 in chain.links.
    """
    q = np.zeros(len(chain.links))
    if len(chain.links) < 7:
        raise RuntimeError(f"Chain too short (len={len(chain.links)}). Check URDF/base_elements.")
    q[1:7] = np.deg2rad([j6_deg["J1"], j6_deg["J2"], j6_deg["J3"], j6_deg["J4"], j6_deg["J5"], j6_deg["J6"]])
    return q

def set_active_non_fixed(chain):
    """Avoid IKPy warnings by making only non-fixed joints active."""
    chain.active_links_mask = np.array([lk.joint_type != "fixed" for lk in chain.links], dtype=bool)

# =======================
# Main
# =======================
def main():
    # ---- read robot once ----
    robot = RobotClient(host="192.168.1.22", startup_port=16001, main_port=16002)
    robot.connect()
    robot.initialize(uframe=0, utool=1)
    robot.speed_override(20)

    cart_orig = robot.read_cartesian_coordinates()
    joints_orig = robot.read_joint_coordinates()

    robot.close()

    # Normalize dicts
    cart6 = {k: float(cart_orig[k]) for k in ["X", "Y", "Z", "W", "P", "R"]}
    j6 = {f"J{i}": float(joints_orig[f"J{i}"]) for i in range(1, 7)}

    # ---- load chain rooted at base_link ----
    chain = Chain.from_urdf_file(
        URDF_PATH,
        base_elements=["base_link"],
        base_element_type="link",
    )
    set_active_non_fixed(chain)

    # ---- IK: Cartesian -> joints ----
    T_target = pose_to_T_mm_deg(cart6, order=WPR_ORDER)
    q0 = q_from_j6(chain, j6)

    # This exists in your IKPy install (you used it earlier)
    q_ik = chain.inverse_kinematics_frame(target=T_target, initial_position=q0)

    joints_from_cart = {f"J{i}": float(np.rad2deg(q_ik[i])) for i in range(1, 7)}

    # ---- FK: joints -> Cartesian (from ORIGINAL joints) ----
    q_fk_orig = q_from_j6(chain, j6)
    T_fk_orig = chain.forward_kinematics(q_fk_orig)

    xyz_fk_base_link = T_to_xyz_mm(T_fk_orig)

    # Correct transform into URDF 'base' frame:
    # T_base->ee = inv(T_base_link->base) @ T_base_link->ee
    T_fk_in_base = np.linalg.inv(T_BASELINK_TO_BASE) @ T_fk_orig
    xyz_fk_base = T_to_xyz_mm(T_fk_in_base)

    # ---- FK(IK) sanity check ----
    T_fk_ik = chain.forward_kinematics(q_ik)
    xyz_fk_ik = T_to_xyz_mm(T_fk_ik)

    # ---- Optional: print per-link frames to locate flange/tool0 ----
    per_link_xyz = []
    try:
        fk_all = chain.forward_kinematics(q_fk_orig, full_kinematics=True)
        for i, (lk, T) in enumerate(zip(chain.links, fk_all)):
            per_link_xyz.append((i, lk.name, T_to_xyz_mm(T)))
    except TypeError:
        # Older IKPy
        pass

    # ---- Print summary at end ----
    print("\n===== ORIGINAL (from robot) =====")
    print("Cartesian:", cart6)
    print("Joints:", j6)

    print("\n===== CONVERTED =====")
    print("Cartesian -> Joint (IK):", joints_from_cart)
    print("Joint -> Cartesian FK (from ORIGINAL joints, base_link frame):", xyz_fk_base_link)
    print("Joint -> Cartesian FK (from ORIGINAL joints, in 'base' frame):", xyz_fk_base)

    print("\n===== CHECKS =====")
    target_xyz = {k: cart6[k] for k in ["X", "Y", "Z"]}
    print("FK(IK joints) XYZ:", xyz_fk_ik)
    print("Target XYZ:", target_xyz)
    print("Error FK(IK) vs target:", xyz_error_mm(xyz_fk_ik, target_xyz))
    print("Error FK(orig joints) vs target (base_link):", xyz_error_mm(xyz_fk_base_link, target_xyz))
    print("Error FK(orig joints) vs target (base):", xyz_error_mm(xyz_fk_base, target_xyz))

    if per_link_xyz:
        print("\n===== PER-LINK FK XYZ (base_link frame) =====")
        for i, name, xyz in per_link_xyz:
            print(f"{i:02d}  {name:20s}  {xyz}")

if __name__ == "__main__":
    main()
