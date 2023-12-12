
import math


time_slot = 0.1
# --------------------------------------计算当前位置及航向角    
def calculate_next_pos_theta(last_moment_pos, last_moment_theta, speed, wheel_angle, wheel_base):
    # 转换为弧度
    wheel_angle_rad = math.radians(wheel_angle)
    last_moment_theta_rad = math.radians(last_moment_theta)
    # 计算车辆行驶距离（单位：千米）
    distance = speed * time_slot / 3600  # 将小时转换为秒
    
    # 一度经度在地球表面上的大约距离（单位：千米）
    km_per_longitude_degree = 111

    # 一度纬度在地球表面上的大约距离（单位：千米）
    km_per_latitude_degree = 110
        
    if abs(wheel_angle_rad) > 0.001:  # 避免除以零错误
        # 转向角速度
        turning_radius = wheel_base / math.tan(wheel_angle_rad)

        # 计算转弯半径变化引起的车辆位置变化
        delta_theta = distance / turning_radius
        delta_longitude = math.degrees(delta_theta)  # 角度转换为经度变化
        delta_latitude = distance * math.cos(last_moment_pos[1] * math.pi / 180)  # 角度转换为纬度变化
    else:
        # 车辆直行时的位置变化（根据车辆行驶方向计算）
        delta_longitude = distance * math.cos(last_moment_theta_rad) / km_per_longitude_degree
        delta_latitude = distance * math.sin(last_moment_theta_rad) / km_per_latitude_degree
        delta_theta = 0

    # 计算下一时刻位置
    next_theta = last_moment_theta + math.degrees(delta_theta)
    # 确保航向角在[0, 360)范围内
    next_theta = (next_theta + 360) % 360
    
    # 计算下一时刻位置
    next_pos = [    
        last_moment_pos[0] + delta_longitude,
        last_moment_pos[1] + delta_latitude,
        last_moment_pos[2]  # 保持z轴不变
    ]

    return next_pos, next_theta


