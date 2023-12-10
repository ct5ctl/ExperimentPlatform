import multiprocessing

class VehicleData:
    def __init__(self):
        self.pos_current = [[0, 0, 1]]  # 初始化为默认值
        self.theta_current = 270  # 初始化为默认值

    def update_data(self, pos, theta):
        self.pos_current = pos
        self.theta_current = theta

    def get_pos_current(self):
        return self.pos_current

    def get_theta_current(self):
        return self.theta_current

    def update_shared_data(shared_data, pos, theta):
        shared_data['pos'] = pos
        shared_data['theta'] = theta

if __name__ == "__main__":
    manager = multiprocessing.Manager()
    shared_vehicle_data = manager.dict()

    vehicle_data = VehicleData()  # 创建 VehicleData 实例
    shared_vehicle_data['data'] = vehicle_data  # 将实例存储在共享字典中

    # 更新共享数据
    update_shared_data(shared_vehicle_data['data'], [[116.38553266, 39.90440998, 0]], 270)

    # 获取共享数据
    shared_data = shared_vehicle_data['data']
    print("Shared VehicleData pos_current:", shared_data.get_pos_current())
    print("Shared VehicleData theta_current:", shared_data.get_theta_current())
