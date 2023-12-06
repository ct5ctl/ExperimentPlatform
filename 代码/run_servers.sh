#!/bin/bash

# 运行pos_server.py
echo "Starting pos_server.py"
python3 pos_server.py &

# 等待一会儿，确保 pos_server.py 已经启动
sleep 2

# 运行websocket_server.py
echo "Starting websocket_server.py"
python3 websocket_server.py
