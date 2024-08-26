import carla
import random

def generate_vehicles(client, world, starting_location):
    # Connect to the simulator on localhost:2000 and get the world
    map = world.get_map()
    
    # Get the waypoint for the starting location
    start_waypoint = map.get_waypoint(carla.Location(x=-10, y=312, z=2), project_to_road=True)
    
    # other_side = start_waypoint.get_left_lane().get_left_lane().get_left_lane()
    
    # db = world.debug 
    # db.draw_point(other_side.transform.location, size=0.1, color=carla.Color(255, 0, 0),life_time=10)
    # Get waypoints for the left and right lanes
    left_lane_wp = start_waypoint.get_left_lane()
    right_lane_wp = start_waypoint.get_right_lane()
    right_r_lane_wp = right_lane_wp.get_right_lane()

    # Move 3 meters forward in the left and right lanes to find the NPC start points
    npc1_start_waypoint = left_lane_wp.previous(3.0)[0]
    npc2_start_waypoint = right_lane_wp.next(3.0)[0]
    npc3_start_waypoint = right_r_lane_wp.previous(3.0)[0]

    # Function to generate vehicle spawns for given waypoint and distances
    def generate_vehicle_spawns(waypoint, distances):
        spawns = []
        for d in distances:
            try:
                wp = waypoint.next(d)[0] if d >= 0 else waypoint.previous(-d)[0]
                tf = wp.transform
                tf.location.z += 2
                if random.random() < 0.8:
                    spawns.append(tf)
            except :
                pass
        return spawns

    # Generate spawn points: 1 backward and 5 forward, each 10 meters apart
    sp = [i for i in range(-150,150,15)]
    print(sp)
    vehicle_spawn_points = generate_vehicle_spawns(start_waypoint, sp)
    vehicle_spawn_points += generate_vehicle_spawns(npc1_start_waypoint, sp)
    vehicle_spawn_points += generate_vehicle_spawns(npc2_start_waypoint, sp)
    vehicle_spawn_points += generate_vehicle_spawns(npc3_start_waypoint, sp)

    # Spawn vehicles at each spawn point
    blueprint_library = world.get_blueprint_library() 
    vehicle_blueprints = []
    for bp in blueprint_library.filter('vehicle.*'):
        # print(bp.get_attribute('base_type'))
        if not bp.get_attribute('base_type').as_str() not in ['bicycle', 'motorcycle']:
            continue
        vehicle_blueprints.append(bp)

    db = world.debug 

    for transform in vehicle_spawn_points:
        db.draw_point(transform.location, size=0.1, color=carla.Color(255, 0, 0),life_time=10)
        vehicle_bp = random.choice(vehicle_blueprints)
        if vehicle_bp.has_attribute('color'):
            vehicle_color = random.choice(vehicle_bp.get_attribute('color').recommended_values)
            vehicle_bp.set_attribute('color', vehicle_color)
        world.try_spawn_actor(vehicle_bp, transform)
        world.wait_for_tick()

    # Set spectator's view near the starting vehicle
    spectator = world.get_spectator()
    # spectator_transform = carla.Transform(start_waypoint.transform.location + carla.Location(z=50), 
    #                                       carla.Rotation(pitch=-60,
    #                                                      yaw = start_waypoint.transform.rotation.yaw))
    spectator_transform = carla.Transform(carla.Location(x=-43.016201, y=375.011932, z=1.781044), carla.Rotation(pitch=-8.577058, yaw=-77.722641, roll=0.000072))
    spectator.set_transform(spectator_transform)


def clear_all_actors_except_spectator(world):
    # Get all actors and destroy them except for the spectator
    actors = world.get_actors().filter('vehicle.*')
    spectator = world.get_spectator()
    for actor in actors:
        if actor.id != spectator.id:
            actor.destroy()

def main():
    # Connect to the Carla server
    client = carla.Client('localhost', 2000)
    client.set_timeout(50.0)  # seconds
    # world = client.load_world('Town04')
    world = client.get_world()
    clear_weather = carla.WeatherParameters(
        cloudiness=0.0,   # Set cloudiness to 0% for clear skies
        precipitation=0.0,  # No precipitation
        sun_altitude_angle=50.0  # Sun at the highest point for maximum brightness
    )

    # Apply the weather to the world
    world.set_weather(clear_weather)

    try:
        # Clear any existing actors
        clear_all_actors_except_spectator(world)

        # Set up the simulation
        generate_vehicles(client, world, carla.Location(x=-10, y=316, z=2))

        print("Press 'q' to quit or any other key to continue...")
        # Wait for a key press to decide the next action
        
        spectator = world.get_spectator()
        
        while True:
            key = input()
            if key.lower() == 'q':
                break
            elif key.lower() == 'g':
                
                print(spectator.get_transform())
            print("Press 'q' to quit or any other key to continue...")
    
    finally:
        # Ensure all actors are destroyed on exit
        clear_all_actors_except_spectator(world)
        print("Simulation ended and all actors cleared.")

if __name__ == '__main__':
    main()