
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


# 模拟车辆运动并绘制轨迹图
def simulate_vehicle_motion():
    # 初始位置
    initial_pos = [0, 0, 0]  # 经度、纬度、高度
    initial_theta = 90  # 初始航向角度
    
    # 车辆参数
    wheel_base = 2.5  # 车辆轴距
    
    # 模拟车速和车轮角度的变化
    speeds = [50] * 1000  # 模拟1000个0.1秒内速度恒定为50 km/h
    wheel_angles = [10] * 1000  # 模拟1000个0.1秒内车轮角度恒定为10度
    
    # 初始化位置轨迹
    positions = [initial_pos]
    thetas = [initial_theta]
    
    for i in range(len(speeds)):
        # 计算下一个位置和航向角
        next_pos, next_theta = calculate_next_pos_theta(positions[-1], thetas[-1], speeds[i], wheel_angles[i], wheel_base)
        
        # 将计算得到的位置和角度加入轨迹列表中
        positions.append(next_pos)
        thetas.append(next_theta)
    
    # 绘制轨迹图
    longitude = [pos[0] for pos in positions]
    latitude = [pos[1] for pos in positions]
    
    plt.figure(figsize=(8, 6))
    plt.plot(longitude, latitude)
    plt.title('Vehicle Trajectory')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True)
    plt.show()

# 运行模拟并绘制轨迹图
simulate_vehicle_motion()