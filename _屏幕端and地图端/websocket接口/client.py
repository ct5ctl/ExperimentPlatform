
import asyncio
import websockets

async def connect_to_server():
    async with websockets.connect("ws://localhost:8765") as websocket:
        await websocket.send("Hello, server!")
        response = await websocket.recv()
        print(f"Received from server: {response}")

asyncio.get_event_loop().run_until_complete(connect_to_server())
