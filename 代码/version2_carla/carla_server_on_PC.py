import asyncio
import random
import websockets
import json
import carla

# CARLA 主机地址与端口
HOST = 'localhost'
PORT = 2000

# 创建 CARLA 客户端与世界
client = carla.Client(HOST, PORT)
client.set_timeout(2.0)  # 设置超时时间为2秒
world = client.get_world()

# 获取车辆蓝图
blueprint_library = world.get_blueprint_library()
vehicle_blueprint = blueprint_library.filter('model3')[0]  # 假设使用 Tesla Model 3

# 选择初始位置和生成车辆
spawn_point = random.choice(world.get_map().get_spawn_points())
vehicle = world.spawn_actor(vehicle_blueprint, spawn_point)

# 设置自动驾驶与速度控制器
vehicle.set_autopilot(False)  # 关闭自动驾驶

# 控制函数
def control_vehicle(data):
    throttle = data["throttle_depth"] / 100  # 假设throttle_depth范围是0-100
    steer = data["wheel_angle"] / 36.0  # 假设wheel_angle的范围是-36到36,将转向角度从客户端传来的范围缩放到 CARLA 需要的范围 [-1, 1]
    brake = data["brake_depth"] / 100  # 假设brake_depth范围是0-100
    vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=brake))

async def connect_to_server(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            # 处理接收到的车辆数据
            print(f"Received and applied vehicle data: {data}")
            if 'data' in data:
                control_vehicle(data['data'])  # 控制车辆
                print(f"Received and applied vehicle data: {data}")


if __name__ == '__main__':
    # 这里填入服务端IP地址和端口
    uri = "ws://localhost:8765"
    asyncio.get_event_loop().run_until_complete(connect_to_server(uri))

