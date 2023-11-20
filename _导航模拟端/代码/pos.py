import numpy as np
import matplotlib.pyplot as plt

# 时间间隔
time_interval = 0.1  # 时间间隔为0.1秒

# 速度数据（假设这是你的速度列表）
# speed_data = [10, 12, 15, 18, 20]  # 单位：m/s
speed_data = [10, 12, 15, 18, 20]  # 单位：m/s
# 转角数据（假设这是你的转角列表，单位可能是度）
angle_data = [5, 8, 10, 12, 15]  # 单位：度

# 起始位置
start_x = 0
start_y = 0

# 将角度转换为弧度
angle_data_rad = np.radians(angle_data)  # 转换为弧度

# 计算位移（速度 * 时间间隔）
displacement = np.multiply(speed_data, time_interval)

# 考虑转角对位移的影响，修正位移方向
displacement_x = np.multiply(displacement, np.cos(angle_data_rad))
displacement_y = np.multiply(displacement, np.sin(angle_data_rad))

# 计算车辆在每个时间点的累计位移
position_x = np.cumsum(displacement_x)
position_y = np.cumsum(displacement_y)

# 起始位置加到每个时间点的位移上
position_x += start_x
position_y += start_y

# 最终位置是最后一个累计位移点的位置
final_position = (position_x[-1], position_y[-1])
print("车辆最终位置:", final_position)




# 绘制轨迹图
plt.figure(figsize=(8, 6))
plt.plot(position_x, position_y, marker='o', linestyle='-', color='b')
plt.title('车辆轨迹')
plt.xlabel('X 轴位置')
plt.ylabel('Y 轴位置')
plt.grid(True)
plt.show()
