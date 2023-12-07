from multiprocessing import Manager

if __name__ == "__main__":
    with Manager() as manager:
        shared_vehicle_data = manager.Namespace()

        # 在这里连接到共享对象
        print("Python Shell 2 is running. Modifying shared object...")
        vehicle_data = shared_vehicle_data.instance

        # 修改共享对象的属性
        new_pos = [120.0, 40.0, 5.0]
        new_theta = 180
        vehicle_data.update_data(new_pos, new_theta)
