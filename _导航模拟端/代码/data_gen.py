import random

# 速度数据范围
min_speed = 10
max_speed = 20

# 转角数据范围
min_angle = 5
max_angle = 15

# 生成长度为50的线性变化速度数据列表
speed_increment = (max_speed - min_speed) / 49  # 计算速度的线性增量
generated_speed_data = [min_speed + i * speed_increment for i in range(50)]

# 生成长度为50的线性变化转角数据列表
angle_increment = (max_angle - min_angle) / 49  # 计算转角的线性增量
generated_angle_data = [min_angle + i * angle_increment for i in range(50)]

# 添加随机波动
for i in range(50):
    # 随机生成一个[-0.5, 0.5]范围内的小数，用来对速度和转角进行微小的随机波动
    speed_noise = random.uniform(-1, 1)
    angle_noise = random.uniform(-0.5, 0.5)
    
    # 在线性变化的基础上加入随机波动
    generated_speed_data[i] += speed_noise
    generated_angle_data[i] += angle_noise


