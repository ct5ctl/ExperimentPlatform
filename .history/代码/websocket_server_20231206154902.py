import asyncio
import json
import time
import websockets
from pos_server import vehicle_data

async def send_message(websocket):
    while True:
        # 获取当前位置和朝向
        pos_current = vehicle_data.get_pos_current()
        print('pos_current: ', pos_current)
        theta_current = vehicle_data.get_theta_current()

        # 获取当前时间戳
        current_time = time.strftime("%Y%m%d_%H%M", time.localtime())
        # 构建日志文件名
        log_file = f'./log/log_websocket_{current_time}.txt'
        with open(log_file, 'a') as file:
            file.write(f"pos_current: {pos_current}, theta_current: {theta_current}\n")

        message = {
            "eventName": "eventValue",
            "data": f'[[{pos_current[0]},{pos_current[1]},{pos_current[2]}]]'
        }

        # 发送消息给客户端
        # await websocket.send(str(message))
        await websocket.send(json.dumps(message))

        # 等待一段时间再发送下一条消息
        await asyncio.sleep(0.1)  # 100ms

async def echo(websocket, path):
    # 启动发送消息的任务
    send_task = asyncio.create_task(send_message(websocket))

    try:
        # 防止任务提前结束
        await send_task
    except asyncio.CancelledError:
        pass

# 设置服务器 IP 地址和端口号
start_server = websockets.serve(echo, "127.0.0.1", 8765)
# start_server = websockets.serve(echo, "192.168.8.125", 8765)


# 启动服务器
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()