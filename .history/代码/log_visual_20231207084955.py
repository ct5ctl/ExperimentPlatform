import re
import matplotlib.pyplot as plt
import numpy as np

# 读取文件
file_path = 'log_20231207_0846.txt'
data = []
with open(file_path, 'r') as file:
    lines = file.readlines()
    for line in lines:
        nums = re.findall(r"[-+]?\d+\.\d+|[-+]?\d+", line)
        pos = [float(nums[i]) for i in range(3)]
        theta = float(nums[3])
        data.append({'pos': pos, 'theta': theta})

# 提取位置和朝向数据
positions = [d['pos'] for d in data]
thetas = [d['theta'] for d in data]

print('positions: ', positions)
print('thetas: ', thetas)

# 绘制轨迹图
plt.figure(figsize=(8, 6))
x = [pos[0] for pos in positions]
y = [pos[1] for pos in positions]
plt.plot(x, y, marker='o', linestyle='-', color='b')
plt.scatter(x[0], y[0], marker='o', color='g', label='Start')
plt.scatter(x[-1], y[-1], marker='o', color='r', label='End')

# 添加航向箭头
for i in range(len(positions)):
    pos = positions[i]
    theta = thetas[i]
    dx = np.cos(np.deg2rad(theta))  # 计算箭头的x方向增量
    dy = np.sin(np.deg2rad(theta))  # 计算箭头的y方向增量
    plt.arrow(pos[0], pos[1], dx, dy, head_width=0.2, head_length=0.3, fc='orange', ec='orange')

plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Car Trajectory with Heading')
plt.legend()
plt.grid(True)
plt.show()
