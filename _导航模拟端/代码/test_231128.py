import asyncio
import websockets

class Server:
    def __init__(self):
        self.shared_data = "Initial Data"  # 数据可以在此初始化

    async def hello(self, websocket, path):
        name = await websocket.recv()
        print(f"< {name}")

        # 使用共享数据
        greeting = f"Hello {name}! Shared data: {self.shared_data}"

        await websocket.send(greeting)
        print(f"> {greeting}")

    async def other_function(self):
        # 在其他函数中操作共享数据
        self.shared_data = "New Data"

server = Server()
start_server = websockets.serve(server.hello, 'localhost', 8765)

async def periodic_task():
    while True:
        # 定期更新共享数据
        server.other_function()
        await asyncio.sleep(10)  # 每10秒更新一次数据

async def main():
    await asyncio.gather(
        start_server,
        periodic_task()
    )

asyncio.run(main())