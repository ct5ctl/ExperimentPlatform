import multiprocessing
import math
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


# ===================================线程1子任务===================================

time_slot = 0.1
# 车辆数据类
class VehicleData:
    def __init__(self):
        self.pos_current = [ 116.38553266, 39.90440998, 0 ]  # 初始化为默认值
        self.theta_current = 270  # 初始化为默认值
        # self.pos_current = [[ 0, 0, 1 ]]  # 初始化为默认值
        # self.theta_current = 270  # 初始化为默认值

    def update_data(self, pos, theta):
        self.pos_current = pos
        self.theta_current = theta

    def get_pos_current(self):
        return self.pos_current

    def get_theta_current(self):
        return self.theta_current
    
class SimulaData:
    def __init__(self):
        self.simula_date = datetime(2022, 6, 15, 10, 0, 0)
        self.simula_time = 360  # 
        # self.pos_current = [[ 0, 0, 1 ]]  # 初始化为默认值
        # self.theta_current = 270  # 初始化为默认值

    


# --------------------------------------计算当前位置及航向角    
def calculate_next_pos_theta(last_moment_pos, last_moment_theta, speed, wheel_angle, wheel_base = 2.785, time_slot = 0.1):
    # 转换角度为弧度
    radian_theta = math.radians(last_moment_theta)
    radian_wheel_angle = math.radians(wheel_angle)

    # Calculate angular speed
    angular_speed = speed / wheel_base * math.tan(radian_wheel_angle)

    # 计算下一时刻的theta
    next_theta = last_moment_theta + math.degrees(angular_speed * time_slot)

    # 标准化theta到0-360度
    next_theta %= 360

    # 转换速度为m/s
    speed_m_per_s = speed / 3.6

    # 使用公式 dx = vt * cos(theta) 和 dy = vt * sin(theta) 计算下一位置
    dsp_x = speed_m_per_s * time_slot * math.cos(radian_theta)
    dsp_y = speed_m_per_s * time_slot * math.sin(radian_theta)

    # 地球半径（单位：千米） 经度116.38553266纬度39.90440998附近的地球半径
    earth_radius_km = 6371.01

    # 计算经纬度度数（注意要将半径乘以2pi转换为千米）
    ds_longitude = dsp_x / (2 * math.pi * earth_radius_km) * 360
    ds_latitude = dsp_y / (2 * math.pi * earth_radius_km) * 360

    # 计算下一时刻的位置
    next_pos = [last_moment_pos[0] + ds_longitude, last_moment_pos[1] + ds_latitude, 0]

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
        # 获取车辆当前位置、航向角（位置偏移+上一时刻位置）
        pos_current, theta_current = calculate_next_pos_theta(vehicle_data.get_pos_current(), vehicle_data.get_theta_current(), float(speed), wheel_angle)
        # 更新 VehicleData 实例中的数据
        vehicle_data.update_data(pos_current, theta_current)
        print("vehicle_data.get_pos_current(): " , vehicle_data.get_pos_current(), "vehicle_data.get_theta_current(): ", vehicle_data.get_theta_current())

        # debug
        # print("vehicle_data_pos: " + str(vehicle_data.get_pos_current()) + "vehicle_data_theta: " + vehicle_data.get_theta_current())
        # # 构建日志文件名
        # with open(f'log_vehicledata.txt', 'a') as file:
        #     file.write(f"pos_current: {vehicle_data.get_pos_current()}, theta_current: {vehicle_data.get_theta_current()}\n")

        # Write data to a log file
        with open(log_file, 'a') as file:
            file.write(f"pos_current: {vehicle_data.get_pos_current()}, theta_current: {vehicle_data.get_theta_current()}, speed: {speed}, wheel_angle: {wheel_angle}, steering_wheel_angle: {steering_wheel_angle}\n")

        return pos_current, theta_current
    else:
        print("未能获取传感器数据")
        return vehicle_data.get_pos_current(), vehicle_data.get_theta_current() # 返回上一时刻位置和航向角

# ===================================线程2子任务===================================
async def send_message(websocket, q):
    # 这里放入你的 WebSocket 发送消息逻辑
    while True:
        # 模拟获取位置和朝向数据，这里用一个固定的数据代替
        pos_current = q.get()
        theta_current = 270

        message = {
            "eventName": "eventValue",
            "data": f'[[{pos_current[0]},{pos_current[1]},{pos_current[2]}]]'  # Convert set to list here
        }
        
        # 发送消息给客户端
        await websocket.send(json.dumps(message))

        # 等待一段时间再发送下一条消息
        await asyncio.sleep(0.1)  # 100ms

# ===================================线程3子任务===================================
def milliseconds_since_2006_01_01(simula_date):
    # 设置起始日期
    start_date = datetime(2006, 1, 1)
    
    # 计算两个日期之间的时间差
    difference = simula_date - start_date
    
    # 转换时间差为毫秒数
    milliseconds = difference.total_seconds() * 1000
    
    return milliseconds

def send_simul_start_command(q, simula_date):
    simula_date_milliseconds = milliseconds_since_2006_01_01(simula_date)
    pos_current = q.get()
    print("已发送导航模拟启动指令")
    pass

def send_track_data_command(q):
    pos_current = q.get()
    print("已发送轨迹数据指令")
    pass

# ===================================线程任务===================================

def pos_server(q, vehicle_data, log_file):
    while True:
        sensor_data = get_sensor_data()  # 调用获取传感器数据的函数
        # print("last_moment_pos:" + str(last_moment_pos), "\nlast_moment_theta:" + str(last_moment_theta))
        # print("传感器数据:", sensor_data)
        # 处理传感器数据，获取当前车辆位置及航向角
        pos_current, theta_current = process_sensor_data(sensor_data, vehicle_data, log_file)  
        # 写入数据到队列
        q.put(pos_current)
        print(f"q writer data:", pos_current)
        time.sleep(time_slot)  # 等待100ms


def start_websocket_server(q):
    async def echo(websocket, path):
        try:
            await send_message(websocket, q)
        except websockets.exceptions.ConnectionClosedError:
            pass

    # 启动 WebSocket 服务器
    # start_server = websockets.serve(echo, "192.168.229.125", 61111)
    start_server = websockets.serve(echo, "127.0.0.1", 18765)
    asyncio.get_event_loop().run_until_complete(start_server)
    print("Server started")
    asyncio.get_event_loop().run_forever()

def navigation_simulation_server(q, flag, simula_date):
    while True:
        if flag.is_set():
            # 非首次执行，发送轨迹数据指令
            send_track_data_command(q)
        else:
            # 首次执行，发送导航模拟启动指令
            send_simul_start_command(q, simula_date)
            flag.set() 
        
        time.sleep(0.1)  # 轨迹发送频率


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
    # 创建一个进程数据传输队列
    q = multiprocessing.Queue()

    # 启动车辆数据预测进程
    pos_server_process = multiprocessing.Process(target=pos_server, args=(q, vehicle_data, log_file))
    pos_server_process.start()

    # 导航模拟的日期时间
    simula_date = datetime(2022, 6, 15, 10, 0, 0)
    # 启动websocket服务进程
    flag = multiprocessing.Event()
    flag.clear()  # 初始化，确保首次执行执行任务 a
    websocket_server_process = multiprocessing.Process(target=start_websocket_server, args=(q, flag, simula_date))
    websocket_server_process.start()
    # # 启动导航模拟
    # navigation_simulation_process = multiprocessing.Process(target=navigation_simulation_server, args=(q,))
    # navigation_simulation_process.start()
    
    

    

