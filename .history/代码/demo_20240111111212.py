# 启动导航模拟报文发送进程
navigation_simulation_process = multiprocessing.Process(target=navigation_simulation_server, args=(q_pos, q_theta, flag, simula_data))
navigation_simulation_process.start()