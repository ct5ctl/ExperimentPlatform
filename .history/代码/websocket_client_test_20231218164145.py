import asyncio
import websockets

async def receive_message():
    # uri = "ws://127.0.0.1:18765"  # 修改为你的服务器地址和端口
    uri = "ws://192.168.8.125:9876"  # 修改为你的服务器地址和端口

    async with websockets.connect(uri) as websocket:
        while True:
            try:
                message = await websocket.recv()
                print(str(message))
            except websockets.exceptions.ConnectionClosedOK:
                print("Connection closed")
                break

asyncio.run(receive_message())
