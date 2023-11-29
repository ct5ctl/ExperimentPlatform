import math
import time
import requests
import numpy as np
import asyncio
import websocket
import websockets
import json

time_slot = 0.1

def get_initial_pos_theta():
    # TODO：后续需要从M1处获得
    initial_pos = [ 116.38553266, 39.90440998, 0 ]
    initial_theta = 270
    return initial_pos, initial_theta


def pos_calculation(speed, wheel_angle, last_moment_pos, last_moment_theta):
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
        0   # z轴恒为0
    ]
    
    # 计算下一时刻航向角
    next_pos_theta = last_moment_theta + math.degrees(wheel_angle_rad)
    # print("next_pos_theta: " + str(next_pos_theta))
    # 确保航向角在[0, 360)范围内
    next_pos_theta = (next_pos_theta + 360) % 360
    
    
    return next_pos, next_pos_theta

# 从泽鹿服务器的网页接口获取传感器数据
def get_sensor_data():
    url = "http://192.168.8.125:9001/api/ipc/channel/getIpcLog"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            # 处理传感器数据
            steering_wheel_direction = data['info']['SteeringWheelDirection']
            steering_wheel_angle = data['info']['SteeringWheelAngle']
            throttle_depth = data['info']['ThrottleDepth']
            brake_depth = data['info']['BrakeDepth']
            speed = data['info']['speed']
            door_status = data['info']['Doorstatus']

            # 这里可以对传感器数据进行进一步处理或返回
            return {
                'SteeringWheelDirection': steering_wheel_direction,
                'SteeringWheelAngle': steering_wheel_angle,
                'ThrottleDepth': throttle_depth,
                'BrakeDepth': brake_depth,
                'Speed': speed,
                'DoorStatus': door_status
            }
        else:
            print("请求失败:", response.status_code)
            return None

    except requests.RequestException as e:
        print("请求异常:", e)
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


# websocket
connected_clients = set()  # 用于记录已连接的客户端

async def websocket_handler(websocket, path):
    # 将每个新客户端添加到已连接客户端的集合中
    connected_clients.add(websocket)
    try:
        while True:
            await asyncio.sleep(time_slot)  # 发送频率
    except websockets.exceptions.ConnectionClosedError:
        pass
    finally:
        connected_clients.remove(websocket)

async def notify_clients(pos_current):
    if connected_clients:
        message = {
            "eventName": "eventValue",
            "data": json.dumps([pos_current])
        }
        await asyncio.wait([client.send(json.dumps(message)) for client in connected_clients])

def websocket_send_data(pos_current):
    asyncio.get_event_loop().run_until_complete(notify_clients(pos_current))
    


# 处理传感器数据，并发送结果（当前位置、航向角）
def process_sensor_data(sensor_data, last_moment_pos, last_moment_theta):
    if sensor_data:
        steering_wheel_direction = sensor_data['info']['SteeringWheelDirection']
        steering_wheel_angle = sensor_data['info']['SteeringWheelAngle']
        throttle_depth = sensor_data['info']['ThrottleDepth']
        brake_depth = sensor_data['info']['BrakeDepth']
        speed = sensor_data['info']['speed']
        door_status = sensor_data['info']['Doorstatus']

        # 在这里可以根据需要对传感器数据进行处理
        print("方向盘方向:", steering_wheel_direction)
        print("方向盘角度:", steering_wheel_angle)
        print("油门深度:", throttle_depth)
        print("刹车深度:", brake_depth)
        print("速度:", speed)
        print("车门状态:", door_status)
        
        #方向角度换算
        wheel_angle = map_degree(steering_wheel_angle)
        #获取车辆当前位置、航向角（位置偏移+上一时刻位置）
        pos_current, theta_current = pos_calculation(speed, wheel_angle, last_moment_pos, last_moment_theta)
        # 将位置数据发送给 WebSocket 客户端
        websocket_send_data(pos_current)
        return pos_current, theta_current
    else:
        print("未能获取传感器数据")


# 主循环
first_iteration = True
# 启动 WebSocket 服务器
start_server = websockets.serve(websocket_handler, "localhost", 8765)  # 将 "localhost" 替换为你的服务器 IP
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
while True:
    if first_iteration:
        # 获取车辆初始位置
        initial_pos, initial_theta = get_initial_pos_theta()
        last_moment_pos = initial_pos
        last_moment_theta = initial_theta
        first_iteration = False
    else:
        sensor_data = get_sensor_data()  # 调用获取传感器数据的函数
        last_moment_pos, last_moment_theta = process_sensor_data(sensor_data, last_moment_pos, last_moment_theta)  # 处理传感器数据

        time.sleep(time_slot)  # 等待100ms


    # # test
    # initial_pos, initial_theta = get_initial_pos_theta()
    # pos_calculation(1, 10, initial_pos, initial_theta)