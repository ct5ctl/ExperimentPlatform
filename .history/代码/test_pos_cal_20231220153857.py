
import math
import matplotlib.pyplot as plt

time_slot = 0.1
# --------------------------------------计算当前位置及航向角    
import math

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


# 模拟车辆运动并绘制轨迹图
def simulate_vehicle_motion():
    # 初始位置
    initial_pos = [0, 0, 0]  # 经度、纬度、高度
    initial_theta = 270  # 初始航向角度
    
    # 车辆参数
    wheel_base = 2.78  # 车辆轴距
    
    # 模拟车速和车轮角度的变化
    speeds = [50] * 10  # 模拟1000个0.1秒内速度恒定为50 km/h
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