import math
import carla
from transforms3d.euler import euler2quat, quat2euler
from modules.common_msgs.localization_msgs.pose_pb2 import Pose

def create_spawn_point(self, x, y, z, roll, pitch, yaw):
        spawn_point = Pose()
        spawn_point.position.x = x
        spawn_point.position.y = y
        spawn_point.position.z = z
        quat = euler2quat(math.radians(roll), math.radians(pitch), math.radians(yaw))

        spawn_point.orientation.qx = quat[1]
        spawn_point.orientation.qy = quat[2]
        spawn_point.orientation.qz = quat[3]
        spawn_point.orientation.qw = quat[0]
        return spawn_point

def cyber_point_to_carla_location(cyber_point):
    return carla.Location(
        cyber_point.x, cyber_point.y * -1, cyber_point.z
    )

def rpy_to_carla_rotation(roll, pitch, yaw):
    return carla.Rotation(
        roll=math.degrees(roll), pitch=-math.degrees(pitch), yaw=-math.degrees(yaw)
    )
    
def cyber_quaternion_to_carla_rotation(cyber_quaternion):
    roll, pitch, yaw = quat2euler(
        [
            cyber_quaternion.qw,
            cyber_quaternion.qx,
            cyber_quaternion.qy,
            cyber_quaternion.qz,
        ]
    )
    return rpy_to_carla_rotation(roll, pitch, yaw)

def cyber_pose_to_carla_transform(cyber_pose):
    """
    Convert a Cyber pose a carla transform.
    """
    return carla.Transform(
        cyber_point_to_carla_location(cyber_pose.position),
        cyber_quaternion_to_carla_rotation(cyber_pose.orientation),
    )

sp = carla.Transform(carla.Location(), carla.Rotation(pitch=0.000000, yaw=-88.685577, roll=0.000000))

sp_dict = {
            "x": sp.location.x, 
            "y": -sp.location.y, 
            "z": sp.location.z+1, 
            "roll": sp.rotation.roll, 
            "pitch": sp.rotation.pitch, 
            "yaw": sp.rotation.yaw
        }

spawn_point = create_spawn_point(
                sp_dict["x"],
                sp_dict["y"],
                sp_dict["z"],
                sp_dict["roll"],
                sp_dict["pitch"],
                sp_dict["yaw"]
            )

transform = cyber_pose_to_carla_transform(spawn_point)