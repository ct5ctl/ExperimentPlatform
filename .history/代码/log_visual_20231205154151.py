import re
import matplotlib.pyplot as plt

# 读取文件
file_path = 'log.txt'
data = []
with open(file_path, 'r') as file:
    lines = file.readlines()
    for line in lines:
        # 使用正则表达式提取数字和浮点数
        nums = re.findall(r"[-+]?\d+\.\d+|[-+]?\d+", line)
        pos = [float(nums[i]) for i in range(3)]
        theta = float(nums[3])
        data.append({'pos': pos, 'theta': theta})

# 提取位置和朝向数据
positions = [d['pos'] for d in data]
thetas = [d['theta'] for d in data]

# 绘制轨迹图
plt.figure(figsize=(8, 6))
x = [pos[0] for pos in positions]
y = [pos[1] for pos in positions]
plt.plot(x, y, marker='o', linestyle='-', color='b')
plt.scatter(x[0], y[0], marker='o', color='g', label='Start')
plt.scatter(x[-1], y[-1], marker='o', color='r', label='End')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Car Trajectory')
plt.legend()
plt.grid(True)
plt.show()
