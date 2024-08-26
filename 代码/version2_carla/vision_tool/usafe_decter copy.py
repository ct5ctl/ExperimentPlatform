import carla
import time
from threading import Thread, Lock, Event

class UnsafeDetector(object):
    def __init__(self, world: carla.World, vehicle: carla.Vehicle):
        self.world = world
        self.vehicle = vehicle
        self.map = self.world.get_map()
        self.lane_change_detector = None
        self.collision_detector = None
        self.callbacks = []
        self.active_timers = {}
        self.timers_lock = Lock()  
        self.threshold_time = 5.0  

        bounding_box = self.vehicle.bounding_box
        vehicle_transform = self.vehicle.get_transform()
        corners = bounding_box.get_world_vertices(vehicle_transform)
        db = self.world.debug
        for index, cor in enumerate(corners):
            text = f'{index}'
            # db.draw_point(cor, size=0.1, life_time=10, color=carla.Color(255, 0, 0))
            db.draw_string(cor, text,  life_time=10, color=carla.Color(255, 0, 0))
        
        spectator = world.get_spectator()
        sp_loc = self.vehicle.get_transform().location + carla.Location(y=-10, z=2)
        spectator.set_transform(carla.Transform(sp_loc, self.vehicle.get_transform().rotation))
            
            
    def init_sensors(self):
        # Setup the lane invasion and collision sensors
        lane_invasion_bp = self.world.get_blueprint_library().find('sensor.other.lane_invasion')
        self.lane_change_detector = self.world.spawn_actor(lane_invasion_bp, carla.Transform(), attach_to=self.vehicle)
        self.lane_change_detector.listen(self.on_lane_invasion)

        collision_bp = self.world.get_blueprint_library().find('sensor.other.collision')
        self.collision_detector = self.world.spawn_actor(collision_bp, carla.Transform(), attach_to=self.vehicle)
        self.collision_detector.listen(self.on_collision)

    def on_collision(self, event):
        # Handle collision events
        self.trigger_callbacks('Collision detected')

    def register_callback(self, callback):
        self.callbacks.append(callback)

    def on_lane_invasion(self, event: carla.LaneInvasionEvent):
        for marking in event.crossed_lane_markings:
            if marking.type in [carla.LaneMarkingType.Solid,
                                carla.LaneMarkingType.SolidSolid]:
                self.trigger_callbacks('Crossed a solid line')
                return
        # Handle lane invasion events
        waypoint = self.map.get_waypoint(self.vehicle.get_location(), project_to_road=False)
        uid = f"{waypoint.road_id}_{waypoint.section_id}"

        with self.timers_lock:
            if uid not in self.active_timers:
                stop_event = Event()
                timer_thread = Thread(target=self.lane_occupation_timer, args=(waypoint.road_id, waypoint.section_id, stop_event))
                self.active_timers[uid] = (timer_thread, stop_event)
                timer_thread.start()

    def check_vehicle_position(self):
        bounding_box = self.vehicle.bounding_box
        vehicle_transform = self.vehicle.get_transform()
        corners = bounding_box.get_world_vertices(vehicle_transform)[2:6]

        road_ids, section_ids, lane_ids = set(), set(), set()
        for corner in corners:
            waypoint = self.world.get_map().get_waypoint(corner, project_to_road=False)
            if not waypoint: continue
            road_ids.add(waypoint.road_id)
            section_ids.add(waypoint.section_id)
            lane_ids.add(waypoint.lane_id)

        if len(road_ids) == 1 and len(section_ids) == 1 and len(lane_ids) > 1:
            return True
        return False
    def lane_occupation_timer(self, road_id, section_id, stop_event:Event):
        start_time = time.time()
        while time.time() - start_time < self.threshold_time and not stop_event.is_set():
            if not self.check_vehicle_position():
                break
            time.sleep(0.1)
        else:
            if not stop_event.is_set():
                self.trigger_callbacks('Long time between lanes')

        with self.timers_lock:
            uid = f"{road_id}_{section_id}"
            del self.active_timers[uid]

    def trigger_callbacks(self, message):
        # Call registered callback functions
        for callback in self.callbacks:
            callback(message)

    def cleanup(self):
        # Clean up the sensors and stop all timers
        try:
            with self.timers_lock:
                for uid, (thread, stop_event) in self.active_timers.items():
                    stop_event.set()  # Signal the event to stop the thread
                    thread.join()  # Wait for the thread to finish
                self.active_timers.clear()

            if self.lane_change_detector:
                self.lane_change_detector.stop()
                self.lane_change_detector.destroy()
            if self.collision_detector:
                self.collision_detector.stop()
                self.collision_detector.destroy()
        except Exception as e:
            print(f"Error cleaning up sensors and timers: {e}")

if __name__ == '__main__':
    client = carla.Client("localhost", 2000)
    client.set_timeout(10.0)
    world = client.get_world()
    settings = world.get_settings()
    print(
        f'world connnected, working in synchronous_mode:{settings.synchronous_mode}')

    time.sleep(1)

    ego_vehicle = None
    for actor in world.get_actors().filter('vehicle.*'):
        # print(actor.attributes.get('role_name'))
        if actor.attributes.get('role_name') in ['hero', 'ego_vehicle']:
            ego_vehicle = actor
            break
    if ego_vehicle == None:
        print("No ego vehicle found")
        exit()
    print("Ego vehicle found")

    decector = UnsafeDetector(world, ego_vehicle)
    
    def callback(message):
        print(message)
    
    decector.register_callback(callback)
    decector.init_sensors()
    
    while True:
        print("Press 'q' to quit or any other key to continue...")
        key = input()
        if key.lower() == 'q':
            break

    decector.cleanup()
