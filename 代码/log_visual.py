import matplotlib.pyplot as plt

# 读取 log.txt 文件并提取数据
file_path = '../log.txt'
positions = []

with open(file_path, 'r') as file:
    for line in file:
        data = line.split(', ')
        pos_str = data[0].split(': ')[1][1:-1]  # 提取位置数据，去除中括号
        pos = list(map(float, pos_str.split(', ')))[:2]  # 只取经纬度数据
        positions.append(pos)

# 提取经纬度数据
longitudes = [pos[0] for pos in positions]
latitudes = [pos[1] for pos in positions]

# 绘制轨迹图
plt.figure(figsize=(8, 6))
plt.plot(longitudes, latitudes, marker='o', linestyle='-', color='b')
plt.title('Car Trajectory')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.grid(True)
plt.show()
