

import math
import matplotlib.pyplot as plt
import math

time_slot = 0.1
# --------------------------------------计算当前位置及航向角    


def calculate_next_pos_theta(last_moment_pos, last_moment_theta, speed, wheel_angle, wheel_base = 2.785):
    # 转换角度为弧度
    radian_theta = math.radians(last_moment_theta)
    radian_wheel_angle = math.radians(wheel_angle)

    # Calculate angular speed
    angular_speed = speed / wheel_base * math.tan(radian_wheel_angle)

    # 计算下一时刻的theta
    next_theta = last_moment_theta + math.degrees(angular_speed * time_slot)

    # 标准化theta到0-360度
    next_theta %= 360

    # 转换速度为m/s
    speed_m_per_s = speed / 3.6

    # 使用公式 dx = vt * cos(theta) 和 dy = vt * sin(theta) 计算下一位置
    dsp_x = speed_m_per_s * time_slot * math.cos(radian_theta)
    dsp_y = speed_m_per_s * time_slot * math.sin(radian_theta)

    # 地球半径（单位：千米） 经度116.38553266纬度39.90440998附近的地球半径
    earth_radius_km = 6371.01

    # 计算经纬度度数（注意要将半径乘以2pi转换为千米）
    ds_longitude = dsp_x / (2 * math.pi * earth_radius_km) * 360
    ds_latitude = dsp_y / (2 * math.pi * earth_radius_km) * 360

    # 计算下一时刻的位置
    next_pos = [last_moment_pos[0] + ds_longitude, last_moment_pos[1] + ds_latitude, 0]

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
    
    plt.figure(figsize=(8, 6))
    plt.plot(x_values, y_values, marker='o')
    plt.title('Vehicle Trajectory')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.grid(True)
    plt.show()

# Example usage:
initial_position = [0, 0, 0]  # Set your initial position here
initial_angle = 45  # Set your initial angle here
vehicle_speed = 10  # Set your vehicle speed here
wheel_angle = 30  # Set your wheel angle here
time_step = 0.1  # Set your time slot here
num_iterations = 100  # Set the number of iterations/steps

plot_vehicle_trajectory(initial_position, initial_angle, vehicle_speed, wheel_angle, time_step, num_iterations)
