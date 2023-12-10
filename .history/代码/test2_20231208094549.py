from multiprocessing import shared_memory

# 使用之前创建的共享内存块的名称连接到它
existing_pos_shm = shared_memory.SharedMemory(name='name_of_shared_memory')

# 创建一个新的变量，连接到共享内存块的数据
shared_pos_current = np.ndarray(pos_current.shape, dtype=pos_current.dtype, buffer=existing_pos_shm.buf)

if __name__ == "__main__":
    with Manager() as manager:
        shared_vehicle_data = manager.Namespace()

        # 在这里连接到共享对象
        print("Python Shell 2 is running. Modifying shared object...")
        vehicle_data = shared_vehicle_data.instance
        pos = vehicle_data.get_pos_current()
        theta = vehicle_data.get_theta_current()
        print("Position in Shell 1:", pos)
        print("Theta in Shell 1:", theta)
