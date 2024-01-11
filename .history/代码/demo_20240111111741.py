

import multiprocessing
import time
time_slot = 0.1

def send_simul_start_command(q_pos, q_theta, simula_data):
    simula_date_milliseconds = milliseconds_since_2006_01_01(simula_data.get_simula_date())
    simula_time = simula_data.get_simula_time()
    print("simula_date_milliseconds:", simula_date_milliseconds)
    pos_current = q_pos.get()
    theta_current = q_theta.get()
    command = 0x0ABB9011

    # 构建导航模拟启动指令
    frame_data = struct.pack('<qqqqddddddddddddqqqdddddddddddd', int(command), int(simula_date_milliseconds), int(simula_time), 0,
                             pos_current[0], pos_current[1], pos_current[2],
                             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
                             0, 0, 0,
                             0.0, theta_current, 0.0,
                             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    
    # 创建 socket 对象
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('10.129.41.113', 9988)  # 目标服务器地址和端口

    # 构建帧头
    frame_header = struct.pack('<I', 0xA5A56666)
    # 构建帧标志
    frame_flag = struct.pack('<I', 0)
    # 构建帧长
    # 计算帧长
    frame_length = len(frame_data)
    frame_length_packed = struct.pack('<I', frame_length)
    # 构建备用字段
    alternate = struct.pack('<I', 0)
    
    # 合并数据帧
    full_frame = frame_header + frame_flag + frame_length_packed + alternate + frame_data

    try:
        # 发送数据
        sock.sendto(full_frame, server_address)
        print("已发送导航模拟启动指令")
    except socket.error as e:
        print(f"发送数据失败: {e}")
    finally:
        sock.close()

def send_track_data_command(q_pos, q_theta, simula_data):
    # 获取当前数据
    pos_current = q_pos.get()
    theta_current = q_theta.get()
    track_number = simula_data.get_track_number() + 1
    track_time = track_number * time_slot * 1000
    # track_time = track_number * time_slot + 

    # 更新轨迹时间和轨迹序号
    simula_data.update_track_data(track_time + time_slot, track_number)
    # pos_new = [ 222, 222, 222 ]
    print("轨迹时间:", track_time, "轨迹序号:", track_number)

    # 构建数据帧
    command = 0x0A5A5C39  # 命令字
    frame_data = struct.pack('<qqqqddddddddddddqqqdddddddddddd', int(command), int(track_time), int(track_number), 0,
                             pos_current[0], pos_current[1], pos_current[2],
                             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                             0.0, 0, 0, 0, 0.0, theta_current, 0.0, 
                             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    # 创建 socket 对象
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('10.129.41.113', 9988)  # 目标服务器地址和端口

    # 构建帧头
    frame_header = struct.pack('<I', 0xA5A56666)
    # 构建帧标志
    frame_flag = struct.pack('<I', 0)
    # 计算帧长
    frame_length = len(frame_data)
    print("frame_length:", frame_length)
    frame_length_packed = struct.pack('<I', frame_length)
    # 构建备用字段
    alternate = struct.pack('<I', 0)

    # 合并数据帧
    full_frame = frame_header + frame_flag + frame_length_packed + alternate + frame_data

    try:
        # 发送数据
        sock.sendto(full_frame, server_address)
        print("已发送轨迹数据指令 [", pos_current[0], ",", pos_current[1], ",", pos_current[2], "]")
    except socket.error as e:
        print(f"发送数据失败: {e}")
    finally:
        sock.close()

def navigation_simulation_server(q_pos, q_theta, flag, simula_data):
    while True:
        # # 触发式执行
        # send_track_data_command(q_pos, q_theta, simula_data)

        # 非触发式执行
        if flag.is_set():
            # 非首次执行，发送轨迹数据指令
            send_track_data_command(q_pos, q_theta, simula_data)
        else:
            # 首次执行，发送导航模拟启动指令
            print("首次执行，发送导航模拟启动指令")
            send_simul_start_command(q_pos, q_theta, simula_data)
            flag.set() 
            time.sleep(10)
            print("开始轨迹注入")
        
        time.sleep(time_slot)  # 轨迹发送频率


# 启动导航模拟报文发送进程
navigation_simulation_process = multiprocessing.Process(target=navigation_simulation_server, args=(q_pos, q_theta, flag, simula_data))
navigation_simulation_process.start()