import math
import time
import requests
import numpy as np
import asyncio
import websockets
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning



time_slot = 0.1
# 
class VehicleData:
    def __init__(self):
        self.pos_current = [ 116.38553266, 39.90440998, 0 ]  # 初始化为默认值
        self.theta_current = 270  # 初始化为默认值

    def update_data(self, pos, theta):
        self.pos_current = pos
        self.theta_current = theta

    def get_pos_current(self):
        return self.pos_current

    def get_theta_current(self):
        return self.theta_current
    
vehicle_data = VehicleData()

# def get_initial_pos_theta():
#     # TODO：后续需要从M1处获得
#     initial_pos = [ 116.38553266, 39.90440998, 0 ]
#     initial_theta = 270
#     return initial_pos, initial_theta

# 计算航向角
def calculate_next_pos_theta(last_moment_pos, last_moment_theta, speed, wheel_angle, wheel_base):
    # 转换为弧度
    wheel_angle_rad = math.radians(wheel_angle)
    last_moment_theta_rad = math.radians(last_moment_theta)
    # 计算车辆行驶距离
    distance = speed * time_slot
    
    
    if abs(wheel_angle_rad) > 0.001:  # 避免除以零错误
        # 转向角速度
        turning_radius = wheel_base / math.tan(wheel_angle_rad)

        # 计算转弯半径变化引起的车辆位置变化
        delta_theta = distance / turning_radius
        delta_x = turning_radius * (math.sin(last_moment_theta_rad + delta_theta) - math.sin(last_moment_theta_rad))
        delta_y = turning_radius * (math.cos(last_moment_theta_rad) - math.cos(last_moment_theta_rad + delta_theta))
    else:
        # 车辆直行时的位置变化
        delta_x = distance * math.cos(last_moment_theta_rad)
        delta_y = distance * math.sin(last_moment_theta_rad)
        delta_theta = 0

    # 计算下一时刻位置
    next_theta = last_moment_theta + math.degrees(delta_theta)
    # 确保航向角在[0, 360)范围内
    next_theta = (next_theta + 360) % 360
    
    # 计算下一时刻位置
    next_pos = [
        last_moment_pos[0] + delta_x,
        last_moment_pos[1] + delta_y,
        last_moment_pos[2]  # 保持z轴不变
    ]

    return next_pos, next_theta

# def pos_calculation(speed, wheel_angle, last_moment_pos, last_moment_theta, time_slot=1):
    if speed != 0:
        # 将速度转换为米每秒
        speed_mps = speed * 1000 / 3600

        # 角度转弧度
        wheel_angle_rad = math.radians(wheel_angle)
        last_moment_theta_rad = math.radians(last_moment_theta)

        # 计算车辆行驶距离
        distance = speed_mps * time_slot

        # 计算车辆位置变化
        delta_longitude = distance * math.sin(last_moment_theta_rad + wheel_angle_rad)
        delta_latitude = distance * math.cos(last_moment_theta_rad + wheel_angle_rad)

        # 计算下一时刻位置
        next_pos = [
            last_moment_pos[0] + (delta_longitude / (111320 * math.cos(last_moment_pos[1] * math.pi / 180))),
            last_moment_pos[1] + (delta_latitude / 110540),
            0  # z轴恒为0
        ]

        # 计算下一时刻航向角
        next_theta = last_moment_theta + math.degrees(wheel_angle_rad)
        # 确保航向角在[0, 360)范围内
        next_theta = (next_theta + 360) % 360
    else:
        # 若速度为零，则位置和航向角保持不变
        next_pos = last_moment_pos
        next_theta = last_moment_theta

    return next_pos, next_theta

def get_query_id():
    query_id_url = "https://192.168.8.125:9001/api/ipc/channel/calibrationSend?type=F6"
    print("请求queryId地址:", query_id_url)

    try:
        response = requests.get(query_id_url, verify=False)

        if response.status_code == 200:
            data = response.json()
            query_id = data.get('queryId')
            if query_id:
                return query_id
            else:
                print("未找到queryId")
                return None
        else:
            print("请求失败:", response.status_code)
            return None

    except requests.RequestException as e:
        print("请求异常:", e)
        return None

def get_sensor_data():
    query_id = get_query_id()
    if query_id is not None:
        sensor_data_url = f"https://192.168.8.125:9001/api/ipc/channel/getIpcLog?queryId={query_id}"
        print("请求传感器数据地址:", sensor_data_url)

        try:
            response = requests.get(sensor_data_url, verify=False)

            if response.status_code == 200:
                data = response.json()
                # 提取传感器数据
                info = data.get('info')
                if info:
                    steering_wheel_direction = info.get('SteeringWheelDirection')
                    steering_wheel_angle = info.get('SteeringWheelAngle')
                    throttle_depth = info.get('ThrottleDepth')
                    brake_depth = info.get('BrakeDepth')
                    speed = info.get('speed')
                    door_status = info.get('DoorStatus')

                    # 进一步处理传感器数据或返回
                    return {
                        'SteeringWheelDirection': steering_wheel_direction,
                        'SteeringWheelAngle': steering_wheel_angle,
                        'ThrottleDepth': throttle_depth,
                        'BrakeDepth': brake_depth,
                        'Speed': speed,
                        'DoorStatus': door_status
                    }
                else:
                    print("未找到传感器数据")
                    return None
            else:
                print("请求传感器数据失败:", response.status_code)
                return None

        except requests.RequestException as e:
            print("请求传感器数据异常:", e)
            return None
    else:
        print("未获取到queryId，无法请求传感器数据")
        return None




# 方向盘2车轮 转角映射    
def map_degree(steering_wheel_angle):
    # 映射范围
    steering_wheel_min = -360
    steering_wheel_max = 360
    wheel_min = -36
    wheel_max = 36

    # 线性映射公式
    steering_wheel_range = steering_wheel_max - steering_wheel_min
    wheel_range = wheel_max - wheel_min
    mapped_angle = (((steering_wheel_angle - steering_wheel_min) * wheel_range) / steering_wheel_range) + wheel_min

    return mapped_angle

    
# 处理传感器数据，并发送结果（当前位置、航向角）
def process_sensor_data(sensor_data, vehicle_data):
    if sensor_data:
        steering_wheel_direction = sensor_data.get('SteeringWheelDirection')
        steering_wheel_angle = sensor_data.get('SteeringWheelAngle')
        throttle_depth = sensor_data.get('ThrottleDepth')
        brake_depth = sensor_data.get('BrakeDepth')
        speed = sensor_data.get('Speed')
        door_status = sensor_data.get('DoorStatus')

        print("方向盘方向:", steering_wheel_direction)
        print("方向盘角度:", steering_wheel_angle)
        print("油门深度:", throttle_depth)
        print("刹车深度:", brake_depth)
        print("速度:", speed)
        print("车门状态:", door_status)

        # 方向角度换算
        wheel_angle = map_degree(steering_wheel_angle)
        # 获取车辆当前位置、航向角（位置偏移+上一时刻位置）
        pos_current, theta_current = calculate_next_pos_theta(vehicle_data.get_pos_current(), vehicle_data.get_theta_current(), float(speed), wheel_angle, 2.875)
        print("pos_current:", pos_current)
        print("theta_current:", theta_current)
        # 更新 VehicleData 实例中的数据
        vehicle_data.update_data(pos_current, theta_current)

        # Write data to a log file
        with open(log_file, 'a') as file:
            file.write(f"pos_current: {pos_current}, theta_current: {theta_current}, speed: {speed}, wheel_angle: {wheel_angle}, steering_wheel_angle: {steering_wheel_angle}\n")

        # 将位置数据发送给 WebSocket 客户端

    else:
        print("未能获取传感器数据")




# async def websocket_handler(websocket, path):
#     while True:
#         # 假设你有一种方法来获取pos_current和theta_current的数值
#         pos_current = vehicle_data.get_pos_current
        
#         # 创建符合要求格式的消息
#         message = {
#             "eventName": "eventValue",
#             "data": f'[[{pos_current[0]},{pos_current[1]},{pos_current[2]}]]'
#         }
        
#         # 发送消息给WebSocket客户端
#         await websocket.send(json.dumps(message))
        
#         # 根据需要调整此处的休眠时间
#         await asyncio.sleep(0.1)  # 每100毫秒发送一次数据



# # 启动WebSocket服务器
# start_server = websockets.serve(websocket_handler, "0.0.0.0", 8765)  # 替换为你的服务器IP和端口
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()

# async def start_websocket_server():
#     async with websockets.serve(websocket_handler, "0.0.0.0", 8765) as websocket_server:
#         await websocket_server.wait_closed()

# asyncio.run(start_websocket_server())
# print("WebSocket服务器已启动")

# 主循环
# first_iteration = True
# while True:
#     if first_iteration:
#         # 获取车辆初始位置
#         vehicle_data = VehicleData()
#         # initial_pos, initial_theta = get_initial_pos_theta()
#         # last_moment_pos = initial_pos
#         # last_moment_theta = initial_theta
#         first_iteration = False
#     else:
#         sensor_data = get_sensor_data()  # 调用获取传感器数据的函数
#         print("last_moment_pos:" + str(last_moment_pos), "\nlast_moment_theta:" + str(last_moment_theta))
#         last_moment_pos, last_moment_theta = process_sensor_data(sensor_data, vehicle_data)  # 处理传感器数据

#         time.sleep(time_slot)  # 等待100ms

# 抑制不安全请求的警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
log_file = './log.txt'
# 主循环
while True:
    sensor_data = get_sensor_data()  # 调用获取传感器数据的函数
    # print("last_moment_pos:" + str(last_moment_pos), "\nlast_moment_theta:" + str(last_moment_theta))
    print("传感器数据:", sensor_data)
    process_sensor_data(sensor_data, vehicle_data)  # 处理传感器数据

    time.sleep(time_slot)  # 等待100ms


    # # test
    # initial_pos, initial_theta = get_initial_pos_theta()
    # pos_calculation(1, 10, initial_pos, initial_theta)
    
    # # 测试获取传感器数据
    # sensor_data = get_sensor_data()
    # if sensor_data:
    #     print("传感器数据:", sensor_data)
