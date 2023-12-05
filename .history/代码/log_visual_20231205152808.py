import matplotlib.pyplot as plt

file_path = 'log.txt'
positions = []

with open(file_path, 'r') as file:
    for line in file:
        data = line.split(', ')
        print(data)  # 打印每一行数据，检查格式是否正确

        # 尝试解析每一行的位置信息
        try:
            pos_str = data[1].split(': ')[1][1:-1]
            print(pos_str)
            pos = pos_str.split(', ')
            # print(pos)
            pos_float = [float(coord) for coord in pos]
            # print(pos_float)
            positions.append(pos_float)
        except (IndexError, ValueError) as e:
            print(f"Error parsing line: {line.strip()}")

x_coords = [pos[0] for pos in positions]
y_coords = [pos[1] for pos in positions]

plt.figure(figsize=(8, 6))
plt.plot(x_coords, y_coords, marker='o', linestyle='-', color='b')
plt.title('Car Trajectory')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.grid(True)
plt.show()
