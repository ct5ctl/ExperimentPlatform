import asyncio
import websockets

async def main():
    uri = "ws://websocket_server_url"  # 替换成实际的WebSocket服务器URL

    async with websockets.connect(uri) as websocket:
        # 构建要发送的消息
        message = {
            "eventName": "eventValue",
            "data": '[[0, 0, 4]]'  # 替换成实际的坐标数据
        }

        # 发送消息
        await websocket.send(json.dumps(message))

        # 接收服务器的响应
        response = await websocket.recv()
        print(f"Received from server: {response}")

asyncio.get_event_loop().run_until_complete(main())
