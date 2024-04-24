import multiprocessing
import math
import socket
import struct
import sys
import threading
import time
import warnings
import requests
import numpy as np
import asyncio
import urllib3
import websockets
import json
import requests
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from decimal import Decimal, getcontext

# 设置全局精度
getcontext().prec = 50 


# ===================================初始参数===================================

time_slot = 0.1

# 车辆数据类
class VehicleData:
    def __init__(self):
        # self.pos_current = [ 116.38553266, 39.90440998, 0 ]  # 由carla设置位置并更新   
        self.teering_wheel_direction = 0
        self.steering_wheel_angle = 0 # 方向盘转角
        self.wheel_angle = 0 # 车轮转角
        self.throttle_depth = 0
        self.brake_depth = 0
        self.speed = 0
        self.door_status = 0     
           

    def update_data(self, speed, teering_wheel_direction, steering_wheel_angle, wheel_angle, throttle_depth, brake_depth):
        self.speed = 0
        self.teering_wheel_direction = 0
        self.steering_wheel_angle = 0
        self.wheel_angle = 0
        self.throttle_depth = 0
        self.brake_depth = 0

    def get_speed_current(self):
        return self.speed

    def get_wheel_direction_current(self):
        return self.teering_wheel_direction
    
    def get_steering_wheel_angle_current(self): # 方向盘转角
        return self.steering_wheel_angle
    
    def get_wheel_angle_current(self): # 车轮转角
        return self.wheel_angle
    
    def get_throttle_depth_current(self):
        return self.throttle_depth
    
    def get_brake_depth_current(self):  
        return self.brake_depth
    


# ===================================线程1子任务===================================


def calculate_next_pos_theta(last_moment_pos, last_moment_theta, speed, wheel_angle, wheel_base = 2.785):
    last_moment_pos = [Decimal(pos) for pos in last_moment_pos]
    speed_m_per_s = speed * 1000 / 3600
    b = 1000
    if speed == 0:
        next_pos = last_moment_pos
        next_theta = last_moment_theta
    else:
        if wheel_angle == 0:
            # 计算直行的距离
            distance = speed_m_per_s * time_slot
            theta_radian = math.radians(last_moment_theta)
            dx = Decimal(distance * math.cos(theta_radian))
            dy = Decimal(distance * math.sin(theta_radian))
            next_theta = last_moment_theta

            lat_to_km = Decimal(1 / 111)
            lon_to_km = Decimal(1 / (111 * math.cos(math.radians(last_moment_pos[1]))))
            delta_lon = Decimal(dx * lat_to_km / b)
            delta_lat = Decimal(dy * lon_to_km / b)
            next_pos = [Decimal(last_moment_pos[0]+delta_lon), Decimal(last_moment_pos[1]+delta_lat), 0]
        else:
            wheel_angle_radian = math.radians(wheel_angle)
            # Calculate radius of turn
            R = wheel_base / math.tan(abs(wheel_angle_radian))
            # Arc distance the vehicle traveled
            distance = speed_m_per_s * time_slot
            alpha = distance / R

            # The position change in vehicle's local frame
            theta_direction = R * math.sin(alpha)
            theta_vertical_direction = Decimal(R * (1 - math.cos(alpha)))

            # Convert the position change to global frame
            theta_radian = math.radians(last_moment_theta)

            # Calculate next moment theta
            next_theta = (last_moment_theta + math.degrees(alpha)) if wheel_angle > 0 else (last_moment_theta - math.degrees(alpha))
            next_theta %= 360

            # 计算位置
            next_pos = calculate_coordinates(last_moment_pos, last_moment_theta, wheel_angle, theta_direction, theta_vertical_direction, b)

    return next_pos, next_theta

# --------------------------------------使用泽鹿网页接口获取传感器数据
def get_query_id():
    query_id_url = "https://192.168.8.125:9001/api/ipc/channel/calibrationSend?type=F6"
    # print("请求queryId地址1111:", query_id_url)

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
        # print("请求传感器数据地址:", sensor_data_url)

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




# --------------------------------------方向盘to车轮 转角映射    
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

    
# --------------------------------------处理传感器数据，并发送结果（当前位置、航向角）
def process_sensor_data(sensor_data, vehicle_data, log_file):
    if sensor_data:
        steering_wheel_direction = sensor_data.get('SteeringWheelDirection')
        steering_wheel_angle = sensor_data.get('SteeringWheelAngle')
        throttle_depth = sensor_data.get('ThrottleDepth')
        brake_depth = sensor_data.get('BrakeDepth')
        speed = sensor_data.get('Speed')
        door_status = sensor_data.get('DoorStatus')

        # print("方向盘方向:", steering_wheel_direction)
        print("方向盘角度:", steering_wheel_angle)
        # print("油门深度:", throttle_depth)
        # print("刹车深度:", brake_depth)
        print("速度:", speed)
        # print("车门状态:", door_status)

        # 方向角度换算
        wheel_angle = map_degree(steering_wheel_angle)
        # 获取车辆当前位置、航向角
        pos_current, theta_current = calculate_next_pos_theta(vehicle_data.get_pos_current(), vehicle_data.get_theta_current(), float(speed), wheel_angle)
        # 更新 VehicleData 实例中的数据
        speed_x = float(speed) * math.cos(math.radians(theta_current))
        speed_y = float(speed) * math.sin(math.radians(theta_current))
        vehicle_data.update_data(pos_current, theta_current, speed, speed_x, speed_y)
        print("vehicle_data.get_pos_current(): " , vehicle_data.get_pos_current(), "vehicle_data.get_theta_current(): ", vehicle_data.get_theta_current())

        # debug
        # print("vehicle_data_pos: " + str(vehicle_data.get_pos_current()) + "vehicle_data_theta: " + vehicle_data.get_theta_current())
        # # 构建日志文件名
        # with open(f'log_vehicledata.txt', 'a') as file:
        #     file.write(f"pos_current: {vehicle_data.get_pos_current()}, theta_current: {vehicle_data.get_theta_current()}\n")

        # Write data to a log file
        with open(log_file, 'a') as file:
            pos1 = vehicle_data.get_pos_current()
            pos_as_strings = [str(pos1) for pos1 in pos_current]
            file.write(f"pos_current: {pos_as_strings}, speed: {speed}, wheel_angle: {wheel_angle}\n")
    else:
        print("未能获取传感器数据")

# ===================================线程2子任务===================================
async def send_message(websocket, vehicle_data):
    # 这里放入你的 WebSocket 发送消息逻辑
    while True:
        # 获取车辆数据
        vehicle_data_dict = {
            "speed": vehicle_data.get_speed_current(),
            "wheel_direction": vehicle_data.get_wheel_direction_current(),
            "steering_wheel_angle": vehicle_data.get_steering_wheel_angle_current(),
            "wheel_angle": vehicle_data.get_wheel_angle_current(),
            "throttle_depth": vehicle_data.get_throttle_depth_current(),
            "brake_depth": vehicle_data.get_brake_depth_current()
        }

        # Prepare and send the data as a JSON string
        try:
            message = json.dumps({
                "eventName": "vehicleData",
                "data": vehicle_data_dict
            })
            await websocket.send(message)
            print("WebSocket sent message:", message)
        except Exception as e:
            print("Failed to send message:", e)
            break  # Optionally handle reconnection here
            
        # 等待一段时间再发送下一条消息
        await asyncio.sleep(time_slot)  # 100ms

        # # Convert the dictionary to a JSON string for websocket transmission
        # vehicle_data_json = json.dumps(vehicle_data_dict)
        # print("websocket send message:", vehicle_data_json)
        # message = {
        #     "eventName": "eventValue",
        #     "data": vehicle_data_json
        # }
        
        # # 发送消息给客户端
        # await websocket.send(json.dumps(message))

        # # 等待一段时间再发送下一条消息
        # await asyncio.sleep(time_slot)  # 100ms

# ===================================线程任务===================================

def get_vehicle_data(vehicle_data, log_file):
    while True: 
        sensor_data = get_sensor_data()  # 调用获取传感器数据的函数
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
            # print("车门状态:", door_status)

            # 方向角度换算，获得车轮转角
            wheel_angle = map_degree(steering_wheel_angle)
            vehicle_data.update_data(speed, steering_wheel_direction, steering_wheel_angle, wheel_angle, throttle_depth, brake_depth)
            print("vehicle_data.get_speed_current(): " , vehicle_data.get_speed_current(), "vehicle_data.get_wheel_angle_current(): ", vehicle_data.get_wheel_angle_current(),
                   "vehicle_data.get_throttle_depth_current(): ", vehicle_data.get_throttle_depth_current(), "vehicle_data.get_brake_depth_current(): ", vehicle_data.get_brake_depth_current())

        # # test
        # steering_wheel_direction = 0
        # steering_wheel_angle = 1
        # throttle_depth = 1
        # brake_depth = 0
        # speed = 2
        # door_status = 0

        # # print("方向盘方向:", steering_wheel_direction)
        # print("方向盘角度:", steering_wheel_angle)
        # # print("油门深度:", throttle_depth)
        # # print("刹车深度:", brake_depth)
        # print("速度:", speed)
        # # print("车门状态:", door_status)
        
        # # 方向角度换算，获得车轮转角
        # wheel_angle = map_degree(steering_wheel_angle)
        # vehicle_data.update_data(speed, steering_wheel_direction, steering_wheel_angle, wheel_angle, throttle_depth, brake_depth)
        # print("vehicle_data.get_speed_current(): " , vehicle_data.get_speed_current(), "vehicle_data.get_wheel_angle_current(): ", vehicle_data.get_wheel_angle_current(),
        #         "vehicle_data.get_throttle_depth_current(): ", vehicle_data.get_throttle_depth_current(), "vehicle_data.get_brake_depth_current(): ", vehicle_data.get_brake_depth_current())

        # time.sleep(time_slot)  # 等待100ms


def start_websocket_server(vehicle_data):
    async def echo(websocket, path):
        try:
            await send_message(websocket, vehicle_data)
        except websockets.exceptions.ConnectionClosedError:
            pass

    # 启动 WebSocket 服务器
    # start_server = websockets.serve(echo, "192.168.8.125", 9876)   # 传给carla PC的IP地址
    start_server = websockets.serve(echo, 'localhost', 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    print("Server started")
    asyncio.get_event_loop().run_forever()

# ===================================主函数===================================
if __name__ == "__main__":

    # 获取当前时间戳
    current_time = time.strftime("%Y%m%d_%H%M", time.localtime())
    # 构建日志文件名
    log_file = f'log_{current_time}.txt'

    # 构建车辆数据实例
    vehicle_data = VehicleData()
    
    # 抑制不安全请求的警告
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

    # 启动车辆数据预测进程
    pos_server_process = multiprocessing.Process(target=get_vehicle_data, args=(vehicle_data, log_file))
    pos_server_process.start()
    
    # 启动websocket服务进程,发送车辆数据给carla
    websocket_server_process = multiprocessing.Process(target=start_websocket_server, args=(vehicle_data, ))   # 单个参数的逗号不能省略！否则会被判断为一个对象而非元组
    websocket_server_process.start()

    


    

