
from multiprocessing import Manager

with Manager() as manager:
        # 连接到共享的命名空间
        shared_vehicle_data = manager.Namespace()

        # 获取共享的VehicleData实例
        vehicle_data = shared_vehicle_data.instance

        # 访问共享对象的属性和方法
        pos = vehicle_data.get_pos_current()
        theta = vehicle_data.get_theta_current()

        print("Position:", pos)
        print("Theta:", theta)

        # 修改共享对象的属性
        new_pos = [120.0, 40.0, 5.0]
        new_theta = 180
        vehicle_data.update_data(new_pos, new_theta)

        # 再次获取更新后的属性
        updated_pos = vehicle_data.get_pos_current()
        updated_theta = vehicle_data.get_theta_current()

        print("Updated Position:", updated_pos)
        print("Updated Theta:", updated_theta)