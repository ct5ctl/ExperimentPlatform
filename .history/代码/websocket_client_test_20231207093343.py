import asyncio
import websockets

async def receive_message():
    uri = "ws://127.0.0.1:8765"  # 修改为你的服务器地址和端口
    uri = "ws://192.168.8.125:61111"  # 修改为你的服务器地址和端口

    async with websockets.connect(uri) as websocket:
        while True:
            try:
                message = await websocket.recv()
                print(f"Received message: {message}")
            except websockets.exceptions.ConnectionClosedOK:
                print("Connection closed")
                break

asyncio.run(receive_message())
