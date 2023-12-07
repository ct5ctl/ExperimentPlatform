from multiprocessing import shared_memory
# 车辆数据类
class VehicleData:
    def __init__(self):
        self.pos_current = [ 116.38553266, 39.90440998, 0 ]  # 初始化为默认值
        self.theta_current = 270  # 初始化为默认值

    def update_data(self, pos, theta):
        self.pos_current = pos
        self.theta_current = theta

    def get_pos_current(self):
        return self.pos_current

    def get_theta_current(self):
        return self.theta_current
    


if __name__ == '__main__':
    # with Manager() as manager:
    #     shared_vehicle_data = manager.Namespace()
    #     vehicle_data = VehicleData()

    #     # 将VehicleData实例存储在共享对象中
    #     shared_vehicle_data.instance = vehicle_data
    vehicle_data = VehicleData()
    a = [0, 0, 0]
    while True:
        a[0] += 1
        vehicle_data.update_data(a, 0)
        print(str(vehicle_data.get_pos_current()))