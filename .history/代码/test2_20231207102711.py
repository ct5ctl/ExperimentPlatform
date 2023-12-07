from multiprocessing import Manager

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
