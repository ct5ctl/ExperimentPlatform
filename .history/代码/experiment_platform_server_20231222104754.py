import multiprocessing
import math
import socket
import struct
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


# ===================================初始参数===================================

time_slot = 0.1

# 车辆数据类
class VehicleData:
    def __init__(self):
        self.pos_current = [ 116.38553266, 39.90440998, 0 ]  # 初始化为默认值
        self.theta_current = 270  # 初始化为默认值
        self.speed = 0  # 初始化为默认值

    def update_data(self, pos, theta, speed):
        self.pos_current = pos
        self.theta_current = theta
        self.speed = speed

    def get_pos_current(self):
        return self.pos_current

    def get_theta_current(self):
        return self.theta_current
    
# 仿真数据类
class SimulaData:
    def __init__(self):
        self.simula_date = datetime(2022, 6, 15, 10, 0, 0)      # 仿真日期
        self.simula_time = 360  # 仿真时间，单位：秒
        self.track_time = 0  # 轨迹时间，单位：秒
        self.track_number = 0  # 轨迹序号
        
    def get_simula_date(self):
        return self.simula_date

    def get_simula_time(self):
        return self.simula_time
    
    def get_track_time(self):
        return self.track_time
    
    def get_track_number(self):
        return self.track_number
    
    def update_track_data(self, track_time, track_number):
        self.track_time = track_time
        self.track_number = track_number


    

# ===================================线程1子任务===================================
# --------------------------------------计算当前位置及航向角    
def calculate_next_pos_theta(last_moment_pos, last_moment_theta, speed, wheel_angle, wheel_base = 2.785):
    b = 1303.304018485985
    speed_m_per_s = speed * 1000 / 3600

    # 如果wheel_angle等于0，表示车辆直行
    if wheel_angle == 0:
        # 计算直行的距离
        distance = speed_m_per_s * time_slot
        # 转换theta为弧度
        theta_radian = math.radians(last_moment_theta)
        dx = distance * math.sin(theta_radian)
        dy = distance * math.cos(theta_radian)
        next_theta = last_moment_theta
    else:
        # 转换wheel_angle为弧度
        wheel_angle_radian = math.radians(wheel_angle)
        # 计算以车辆为圆心的弧线半径R
        R = wheel_base / math.tan(abs(wheel_angle_radian))
        # 计算车辆实际行驶的弧长distance
        distance = speed_m_per_s * time_slot
        # 计算车辆经过的弧线对应圆心角alpha（弧度）
        alpha = distance / R
        # 计算经纬度变化
        dx = R * math.sin(alpha) if wheel_angle > 0 else -R * math.sin(alpha)
        dy = R * (1 - math.cos(alpha))
        # 计算下一时刻的theta
        next_theta = (last_moment_theta - math.degrees(alpha)) if wheel_angle > 0 else (last_moment_theta + math.degrees(alpha))
        # Ensure next_theta is within 0~360
        next_theta %= 360

    # 一个纬度上距离1km对应的角度变化
    lat_to_km = 1 / 111
    # 一个经度上距离1km对应的角度变化
    lon_to_km = 1 / (111 * math.cos(math.radians(last_moment_pos[1])))

    # 计算经纬度变化对应的角度变化
    delta_lon = dx * lat_to_km  /  b
    delta_lat = dy * lon_to_km  /  b
    # 计算下一时刻的位置
    next_pos = [last_moment_pos[0]+delta_lon, last_moment_pos[1]+delta_lat, 0]

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
        vehicle_data.update_data(pos_current, theta_current, speed)
        print("vehicle_data.get_pos_current(): " , vehicle_data.get_pos_current(), "vehicle_data.get_theta_current(): ", vehicle_data.get_theta_current())

        # debug
        # print("vehicle_data_pos: " + str(vehicle_data.get_pos_current()) + "vehicle_data_theta: " + vehicle_data.get_theta_current())
        # # 构建日志文件名
        # with open(f'log_vehicledata.txt', 'a') as file:
        #     file.write(f"pos_current: {vehicle_data.get_pos_current()}, theta_current: {vehicle_data.get_theta_current()}\n")

        # Write data to a log file
        with open(log_file, 'a') as file:
            file.write(f"pos_current: {vehicle_data.get_pos_current()}, speed: {speed}, wheel_angle: {wheel_angle}, steering_wheel_angle: {steering_wheel_angle}\n")

        return pos_current, theta_current
    else:
        print("未能获取传感器数据")
        return vehicle_data.get_pos_current(), vehicle_data.get_theta_current() # 返回上一时刻位置和航向角

# ===================================线程2子任务===================================
async def send_message(websocket, q_pos):
    # 这里放入你的 WebSocket 发送消息逻辑
    while True:
        # 模拟获取位置和朝向数据，这里用一个固定的数据代替
        pos_current = q_pos.get()
        theta_current = 270

        message = {
            "eventName": "eventValue",
            "data": [list(pos_current)]
        }

        print("websocket send message:", message)
        
        # 发送消息给客户端
        await websocket.send(json.dumps(message))

        # 等待一段时间再发送下一条消息
        await asyncio.sleep(time_slot)  # 100ms

# ===================================线程3子任务===================================
def milliseconds_since_2006_01_01(simula_date):
    # 设置起始日期
    start_date = datetime(2006, 1, 1)
    
    # 计算两个日期之间的时间差
    difference = simula_date - start_date
    
    # 转换时间差为毫秒数
    milliseconds = difference.total_seconds() * 1000
    
    return milliseconds

def send_simul_start_command(q_pos, q_theta, simula_data):
    simula_date_milliseconds = milliseconds_since_2006_01_01(simula_data.get_simula_date())
    simula_time = simula_data.get_simula_time()
    pos_current = q_pos.get()
    theta_current = q_theta.get()
    command = 0x0ABB9011

    # 构建导航模拟启动指令
    frame_length = 248  # 根据表格中指令结构与参数的总长度确定
    frame_data = struct.pack('<IIIIIddd', command, simula_date_milliseconds, simula_time, 0,
                             pos_current[0], pos_current[1], pos_current[2],
                             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0,
                             0, theta_current, 0,
                             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    
    # 创建 socket 对象
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('10.129.41.251', 8080)  # 目标服务器地址和端口

    # 构建帧头
    frame_header = struct.pack('<I', 0xA5A56666)
    # 构建帧标志
    frame_flag = struct.pack('<I', 0)
    # 构建帧长
    frame_length_packed = struct.pack('<I', frame_length)
    # 构建备用字段
    alternate = struct.pack('<I', 0)
    
    # 合并数据帧
    full_frame = frame_header + frame_flag + frame_length_packed + alternate + frame_data

    try:
        # 发送数据
        sock.sendto(full_frame, server_address)
        print("已发送导航模拟启动指令")
    except socket.error as e:
        print(f"发送数据失败: {e}")
    finally:
        sock.close()

def send_track_data_command(q_pos, q_theta, simula_data):
    # 获取当前数据
    pos_current = q_pos.get()
    theta_current = q_theta.get()
    track_time = simula_data.get_track_time()
    track_number = simula_data.get_track_number()

    # 更新轨迹时间和轨迹序号
    simula_data.update_track_data(track_time + time_slot, track_number + 1)

    # 构建数据帧
    command = 0x0A5A5C39  # 命令字
    frame_data = struct.pack('<qqqdddddddddddddddddddd', command, track_time, track_number, 0,
                             pos_current[0], pos_current[1], pos_current[2],
                             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                             0.0, track_time, track_number, 0, 0.0, theta_current, 0.0, 
                             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    # 创建 socket 对象
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('10.129.41.251', 8080)  # 目标服务器地址和端口

    # 构建帧头
    frame_header = struct.pack('<I', 0xA5A56666)
    # 构建帧标志
    frame_flag = struct.pack('<I', 0)
    # 计算帧长
    frame_length = len(frame_data)
    frame_length_packed = struct.pack('<I', frame_length)
    # 构建备用字段
    alternate = struct.pack('<I', 0)

    # 合并数据帧
    full_frame = frame_header + frame_flag + frame_length_packed + alternate + frame_data

    try:
        # 发送数据
        sock.sendto(full_frame, server_address)
        print("已发送轨迹数据指令")
    except socket.error as e:
        print(f"发送数据失败: {e}")
    finally:
        sock.close()

# ===================================线程任务===================================

def pos_server(q_pos, q_theta, vehicle_data, log_file):
    while True:
        sensor_data = get_sensor_data()  # 调用获取传感器数据的函数
        # 处理传感器数据，获取当前车辆位置及航向角
        pos_current, theta_current = process_sensor_data(sensor_data, vehicle_data, log_file)  
        # 写入数据到队列
        q_pos.put(pos_current)
        q_theta.put(theta_current)
        # print(f"q_pos writer data:", pos_current)
        # print(f"q_theta writer data:", theta_current)
        time.sleep(time_slot)  # 等待100ms


def start_websocket_server(q_pos):
    async def echo(websocket, path):
        try:
            await send_message(websocket, q_pos)
        except websockets.exceptions.ConnectionClosedError:
            pass

    # 启动 WebSocket 服务器
    start_server = websockets.serve(echo, "192.168.229.125", 9876)
    # start_server = websockets.serve(echo, "192.168.8.125", 9876)
    # start_server = websockets.serve(echo, "127.0.0.1", 9876)
    asyncio.get_event_loop().run_until_complete(start_server)
    print("Server started")
    asyncio.get_event_loop().run_forever()

def navigation_simulation_server(q_pos, q_theta, flag, simula_data):
    while True:
        if flag.is_set():
            # 非首次执行，发送轨迹数据指令
            send_track_data_command(q_pos, q_theta, simula_data)
        else:
            # 首次执行，发送导航模拟启动指令
            send_simul_start_command(q_pos, q_theta, simula_data)
            flag.set() 
        
        time.sleep(time_slot)  # 轨迹发送频率


# ===================================主函数===================================
if __name__ == "__main__":

    # 获取当前时间戳
    current_time = time.strftime("%Y%m%d_%H%M", time.localtime())
    # 构建日志文件名
    log_file = f'log_{current_time}.txt'

    # 构建车辆数据实例
    vehicle_data = VehicleData()
    # 构建仿真数据实例
    simula_data = SimulaData()
    
    # 抑制不安全请求的警告
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)
    # 创建一个进程数据传输队列
    q_pos = multiprocessing.Queue()
    q_theta = multiprocessing.Queue()

    # 启动车辆数据预测进程
    pos_server_process = multiprocessing.Process(target=pos_server, args=(q_pos, q_theta, vehicle_data, log_file))
    pos_server_process.start()
    
    # 启动websocket服务进程
    websocket_server_process = multiprocessing.Process(target=start_websocket_server, args=(q_pos, ))   # 参数的逗号不能省略！否则会被判断为一个对象而非元组
    websocket_server_process.start()

    # flag = multiprocessing.Event()
    # flag.clear()  
    # # 启动导航模拟报文发送进程
    # navigation_simulation_process = multiprocessing.Process(target=navigation_simulation_server, args=(q_pos, q_theta, flag, simula_data))
    # navigation_simulation_process.start()
    
    

    

