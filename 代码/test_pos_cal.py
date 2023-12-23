

import math
import matplotlib.pyplot as plt
import math

# --------------------------------------计算当前位置及航向角    
time_slot = 0.1
# b = 1303.304018485985
b = 100
def calculate_coordinates(last_moment_pos, last_moment_theta, wheel_angle, theta_direction, theta_vertical_direction, b):
    # 将角度转换为弧度
    theta_rad = math.radians(last_moment_theta)
    
    # 计算点 B 的经纬度坐标变化量
    delta_longitude = theta_direction * math.cos(theta_rad) / 111.32  # 每经度对应的距离约为111.32 km
    delta_latitude = theta_direction * math.sin(theta_rad) / (111.32 * math.cos(math.radians(last_moment_pos[1])))  # 每纬度对应的距离约为111.32 km
    
    # 计算点 B 的经纬度坐标
    b_longitude = last_moment_pos[0] + delta_longitude / b
    b_latitude = last_moment_pos[1] + delta_latitude / b
    
    # 计算 AB 的单位向量
    ab_unit_longitude = delta_longitude
    ab_unit_latitude = delta_latitude
    ab_magnitude = math.sqrt(ab_unit_longitude ** 2 + ab_unit_latitude ** 2)
    ab_unit_longitude /= ab_magnitude
    ab_unit_latitude /= ab_magnitude
    
    # 计算 BC 的单位向量，垂直于 AB
    bc_unit_longitude = -ab_unit_latitude  # 交换经纬度方向确保垂直性质
    bc_unit_latitude = ab_unit_longitude
    
    # 根据 fx 确定方向
    direction = 1 if wheel_angle > 0 else -1
    
    # 计算点 C 的经纬度坐标变化量
    delta_longitude_c = theta_vertical_direction * bc_unit_longitude / 111.32  # 每经度对应的距离约为111.32 km
    delta_latitude_c = theta_vertical_direction * bc_unit_latitude / (111.32 * math.cos(math.radians(b_latitude)))  # 每纬度对应的距离约为111.32 km
    
    # 计算点 C 的经纬度坐标
    c_longitude = b_longitude + direction * delta_longitude_c / b
    c_latitude = b_latitude + direction * delta_latitude_c / b
    
    return c_longitude, c_latitude


def calculate_next_pos_theta(last_moment_pos, last_moment_theta, speed, wheel_angle, wheel_base = 2.785, time_slot = 0.1):
    speed_m_per_s = speed * 1000 / 3600
    b = 1000
    if wheel_angle == 0:
        # 计算直行的距离
        distance = speed_m_per_s * time_slot
        theta_radian = math.radians(last_moment_theta)
        dx = distance * math.cos(theta_radian)
        dy = distance * math.sin(theta_radian)
        next_theta = last_moment_theta

        lat_to_km = 1 / 111
        lon_to_km = 1 / (111 * math.cos(math.radians(last_moment_pos[1])))
        delta_lon = dx * lat_to_km / b
        delta_lat = dy * lon_to_km / b
        next_pos = [last_moment_pos[0]+delta_lon, last_moment_pos[1]+delta_lat, 0]
    else:
        wheel_angle_radian = math.radians(wheel_angle)
        # Calculate radius of turn
        R = wheel_base / math.tan(abs(wheel_angle_radian))
        # Arc distance the vehicle traveled
        distance = speed_m_per_s * time_slot
        alpha = distance / R

        # The position change in vehicle's local frame
        theta_direction = R * math.sin(alpha)
        theta_vertical_direction = R * (1 - math.cos(alpha))

        # Convert the position change to global frame
        theta_radian = math.radians(last_moment_theta)

        # Calculate next moment theta
        next_theta = (last_moment_theta + math.degrees(alpha)) if wheel_angle > 0 else (last_moment_theta - math.degrees(alpha))
        next_theta %= 360

        # 计算位置
        next_pos = calculate_coordinates(last_moment_pos, last_moment_theta, wheel_angle, theta_direction, theta_vertical_direction, b)

    return next_pos, next_theta


def plot_vehicle_trajectory(initial_pos, initial_theta, speed, wheel_angle, time_slot, num_steps):
    positions = [initial_pos]
    thetas = [initial_theta]
    
    current_pos = initial_pos
    current_theta = initial_theta
    
    for _ in range(num_steps):
        next_pos, next_theta = calculate_next_pos_theta(current_pos, current_theta, speed, wheel_angle)
        print(next_theta)
        positions.append(next_pos)
        thetas.append(next_theta)
        
        current_pos = next_pos
        current_theta = next_theta
    
    x_values = [pos[0] for pos in positions]
    y_values = [pos[1] for pos in positions]
    print("delta_lat:", positions[-1][0] - initial_pos[0])
    print("delta_lon:", positions[-1][1] - initial_pos[1])
    # 使用相同的缩放比例
    max_range = max(max(x_values) - min(x_values), max(y_values) - min(y_values))
    plt.figure(figsize=(8, 8))  # 设置画布大小为正方形
    
    plt.plot(x_values, y_values, marker='o', label='Trajectory')
    plt.title('Vehicle Trajectory')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.grid(True)
    plt.axis('equal')  # 保持横纵坐标等比例
    
    # 在起点和终点标出不同的点
    plt.scatter(x_values[0], y_values[0], color='green', label='Start Point', s=100)
    plt.scatter(x_values[-1], y_values[-1], color='red', label='End Point', s=100)
    
    plt.legend()  # 显示图例
    plt.show()

# Example usage:
initial_position = [ 0, 0, 0 ]  # Set your initial position here
initial_angle = 0  # Set your initial angle here
vehicle_speed = 10  # Set your vehicle speed here
wheel_angle = 5  # Set your wheel angle here
time_step = 0.1  # Set your time slot here
num_iterations = 300  # Set the number of iterations/steps

plot_vehicle_trajectory(initial_position, initial_angle, vehicle_speed, wheel_angle, time_step, num_iterations)

