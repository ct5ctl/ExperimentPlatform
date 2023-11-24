import time
import requests

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

def process_sensor_data(sensor_data):
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

        #计算该时刻车辆位置
    else:
        print("未能获取传感器数据")

# 主循环
while True:
    # sensor_data = get_sensor_data()  # 调用获取传感器数据的函数
    # process_sensor_data(sensor_data)  # 处理传感器数据
    mapped_angle = map_degree(10)
    print(str( mapped_angle))

    time.sleep(0.1)  # 等待100ms