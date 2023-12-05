import matplotlib.pyplot as plt

# 读取文件
file_path = 'log.txt'
positions = []

with open(file_path, 'r') as file:
    for line in file:
        # 解析每一行数据，提取位置信息
        data = line.split(', ')
        pos_str = data[0].split(': ')[1][1:-1]  # 提取位置数据字符串
        pos = pos_str.split(', ')
        pos_float = [float(coord) for coord in pos]  # 将位置数据转换为浮点数
        positions.append(pos_float)

# 提取x和y坐标
x_coords = [pos[0] for pos in positions]
y_coords = [pos[1] for pos in positions]

# 绘制轨迹图
plt.figure(figsize=(8, 6))
plt.plot(x_coords, y_coords, marker='o', linestyle='-', color='b')
plt.title('Car Trajectory')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.grid(True)
plt.show()
