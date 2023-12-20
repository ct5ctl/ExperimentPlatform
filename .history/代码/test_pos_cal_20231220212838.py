

import math
import matplotlib.pyplot as plt
import math

# --------------------------------------计算当前位置及航向角    
time_slot = 0.1

def calculate_next_pos_theta(last_moment_pos, last_moment_theta, speed, wheel_angle, wheel_base = 2.875, time_slot = 0.1):
    speed_m_per_s = speed * 1000 / 3600

    # 如果wheel_angle等于0，表示车辆直行
    if wheel_angle == 0:
        # 计算直行的距离
        distance = speed_m_per_s * time_slot
        # 转换theta为弧度
        theta_radian = math.radians(last_moment_theta)
        dx = distance * math.sin(theta_radian)
        dy = distance * math.cos(theta_radian)
        next_theta = last_moment_theta
    else:
        # 转换wheel_angle为弧度
        wheel_angle_radian = math.radians(wheel_angle)
        # 计算以车辆为圆心的弧线半径R
        R = wheel_base / math.tan(abs(wheel_angle_radian))
        # 计算车辆实际行驶的弧长distance
        distance = speed_m_per_s * time_slot
        # 计算车辆经过的弧线对应圆心角alpha（弧度）
        alpha = distance / R
        # 计算经纬度变化
        dx = R * math.sin(alpha) if wheel_angle > 0 else -R * math.sin(alpha)
        dy = R * (1 - math.cos(alpha))
        # 计算下一时刻的theta
        next_theta = (last_moment_theta - math.degrees(alpha)) if wheel_angle > 0 else (last_moment_theta + math.degrees(alpha))
        # Ensure next_theta is within 0~360
        next_theta %= 360

    # 一个纬度上距离1km对应的角度变化
    lat_to_km = 1 / 111
    # 一个经度上距离1km对应的角度变化
    lon_to_km = 1 / (111 * math.cos(math.radians(last_moment_pos[1])))

    # 计算经纬度变化对应的角度变化
    delta_lon = dx * lat_to_km  / bet
    delta_lat = dy * lon_to_km  / alpha
    # 计算下一时刻的位置
    next_pos = [last_moment_pos[0]+delta_lon, last_moment_pos[1]+delta_lat, 0]

    return next_pos, next_theta


def plot_vehicle_trajectory(initial_pos, initial_theta, speed, wheel_angle, time_slot, num_steps):
    positions = [initial_pos]
    thetas = [initial_theta]
    
    current_pos = initial_pos
    current_theta = initial_theta
    
    for _ in range(num_steps):
        next_pos, next_theta = calculate_next_pos_theta(current_pos, current_theta, speed, wheel_angle)
        positions.append(next_pos)
        thetas.append(next_theta)
        
        current_pos = next_pos
        current_theta = next_theta
    
    x_values = [pos[0] for pos in positions]
    y_values = [pos[1] for pos in positions]
    print('positions: ', positions)
    
    plt.figure(figsize=(8, 6))
    plt.plot(x_values, y_values, marker='o')
    plt.title('Vehicle Trajectory')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.grid(True)
    plt.show()

# Example usage:
initial_position = [ 116.38553266, 39.90440998, 0 ]  # Set your initial position here
initial_angle = 270  # Set your initial angle here
vehicle_speed = 10  # Set your vehicle speed here
wheel_angle = 0  # Set your wheel angle here
time_step = 0.1  # Set your time slot here
num_iterations = 10  # Set the number of iterations/steps

plot_vehicle_trajectory(initial_position, initial_angle, vehicle_speed, wheel_angle, time_step, num_iterations)
