import math

def calculate_coordinates(a, theta, fx, s, t):
    # 将角度转换为弧度
    theta_rad = math.radians(theta)
    
    # 计算点 B 的经纬度坐标变化量
    delta_longitude = s * math.cos(theta_rad) / 111.32  # 每经度对应的距离约为111.32 km
    delta_latitude = s * math.sin(theta_rad) / (111.32 * math.cos(math.radians(a[1])))  # 每纬度对应的距离约为111.32 km
    
    # 计算点 B 的经纬度坐标
    b_longitude = a[0] + delta_longitude
    b_latitude = a[1] + delta_latitude
    
    # 计算 AB 的单位向量
    ab_unit_longitude = delta_longitude
    ab_unit_latitude = delta_latitude
    ab_magnitude = math.sqrt(ab_unit_longitude ** 2 + ab_unit_latitude ** 2)
    ab_unit_longitude /= ab_magnitude
    ab_unit_latitude /= ab_magnitude
    
    # 计算 BC 的单位向量，垂直于 AB
    bc_unit_longitude = -ab_unit_latitude  # 交换经纬度方向确保垂直性质
    bc_unit_latitude = ab_unit_longitude
    
    # 根据 fx 确定方向
    direction = 1 if fx == 0 else -1
    
    # 计算点 C 的经纬度坐标变化量
    delta_longitude_c = t * bc_unit_longitude / 111.32  # 每经度对应的距离约为111.32 km
    delta_latitude_c = t * bc_unit_latitude / (111.32 * math.cos(math.radians(b_latitude)))  # 每纬度对应的距离约为111.32 km
    
    # 计算点 C 的经纬度坐标
    c_longitude = b_longitude + direction * delta_longitude_c
    c_latitude = b_latitude + direction * delta_latitude_c
    
    return c_longitude, c_latitude


# 示例输入值
point_a = [0, 0]  # A 点经纬度
theta = 90         # 航向角度，例如 45 度
fx = 0             # 方向控制参数，0 或 1
s = 50           # 从点 A 到点 B 的距离，单位 km
t = 0             # 从点 B 到点 C 的距离，单位 km

# 计算 c 点的经纬度坐标
c_longitude, c_latitude = calculate_coordinates(point_a, theta, fx, s, t)
print(f"c 点的经纬度坐标为: ({c_longitude}, {c_latitude})")
