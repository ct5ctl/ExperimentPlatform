



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