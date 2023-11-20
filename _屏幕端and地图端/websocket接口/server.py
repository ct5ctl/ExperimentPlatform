import asyncio
import websockets

async def handle_client(websocket, path):
    # 处理客户端连接
    async for message in websocket:
        # 处理接收到的消息
        await websocket.send(f"Received111: {message}")

start_server = websockets.serve(handle_client, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
