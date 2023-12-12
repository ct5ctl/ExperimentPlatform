
import math
import matplotlib.pyplot as plt

time_slot = 0.1
# --------------------------------------计算当前位置及航向角    
import math

def calculate_next_pos_theta(last_moment_pos, last_moment_theta, speed, wheel_angle, wheel_base, time_slot=0.1):
    print("speed: ", speed)
    print("wheel_angle: ", wheel_angle)
    # 将速度转换为米每秒
    speed_mps = speed * 1000 / 3600  # 转换为米/秒
    
    # 转向角度换算成弧度
    wheel_angle_rad = math.radians(wheel_angle)
    
    # 计算车辆行驶距离
    distance = speed_mps * time_slot
    print('distance: ', distance)
    
    # 假设特斯拉 Model 3 的转弯半径是轮胎转角的函数
    turning_radius = wheel_base / math.tan(wheel_angle_rad)
    
    if abs(wheel_angle_rad) > 0.001:  # 避免除以零错误
        # 转弯时车辆行驶的弧长
        arc_length = abs(distance / turning_radius)
        print('arc_length: ', arc_length)
        
        # 计算车辆朝向角的变化量
        delta_theta = arc_length * math.cos(last_moment_theta) * math.copysign(1, wheel_angle_rad)
        print('delta_theta: ', delta_theta)
        
        # 计算下一时刻位置的经纬度变化量
        delta_longitude = arc_length * math.sin(last_moment_theta)
        delta_latitude = arc_length * math.cos(last_moment_theta)
        
        print('delta_longitude: ', delta_longitude)
        print('delta_latitude: ', delta_latitude)
        
        # 计算下一时刻位置
        next_pos = [
            last_moment_pos[0] + delta_longitude,
            last_moment_pos[1] + delta_latitude,
            last_moment_pos[2]  # z轴保持不变
        ]
    else:
        # 车辆直行时的位置变化
        delta_longitude = distance * math.sin(last_moment_theta)
        delta_latitude = distance * math.cos(last_moment_theta)
        
        # 计算下一时刻位置
        next_pos = [
            last_moment_pos[0] + delta_longitude,
            last_moment_pos[1] + delta_latitude,
            last_moment_pos[2]  # z轴保持不变
        ]
        
        delta_theta = 0  # 车辆直行，朝向角不变
    
    # 计算下一时刻朝向角
    next_theta = (last_moment_theta + delta_theta) % (2 * math.pi)  # 保证角度在0~2π之间
    
    return next_pos, next_theta



# 模拟车辆运动并绘制轨迹图
def simulate_vehicle_motion():
    # 初始位置
    initial_pos = [0, 0, 0]  # 经度、纬度、高度
    initial_theta = 90  # 初始航向角度
    
    # 车辆参数
    wheel_base = 2.5  # 车辆轴距
    
    # 模拟车速和车轮角度的变化
    speeds = [50] * 100  # 模拟1000个0.1秒内速度恒定为50 km/h
    wheel_angles = [10] * 100  # 模拟1000个0.1秒内车轮角度恒定为10度
    
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