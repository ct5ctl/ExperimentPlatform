import carla
import pygame
import numpy as np
import time
import ctypes
import win32gui


from carla import ColorConverter as cc

class Visualizer:
    """
    Welcome to CARLA vehicle visualizer.

    Use WASD/QE/FB keys and page up/down for third person camera adjustment.

        W/S          : move camera up/down
        A/D          : move camera left/right
        F/B          : move camera forward/backward
        Q/E          : move camera roll left/right
        Page Up/Down : move camera roll up/down
        R            : reset camera
    
    Use V to switch first person camera or third person camera.
        V            : toggle third/first person camera
    
    Use P or F11 to switch screen mode.
        P            : switch screen resolution between 3840x1080, 1920x1080, 1600x900, 1280x720
        F11          : switch fullscreen/windowed mode
    
    Others
        ESC          : quit
    """
    def __init__(self, client):
        self.client = client
        self.world = client.get_world()
        time.sleep(2)
        print(Visualizer.__doc__)
        self.vehicle = self.get_ego()
        if self.vehicle:
            print("vehicle detected")
            print(self.vehicle)
        else:
            return
        # self.cameras = []
        self.fp_cam = None
        self.tp_cam = None
        self.active_camera_index = 0
        self.display = None
        self.resolution_index = 3  # Default resolution 1280x720
        self.last_resolution_index = 3
        self.resolutions = [(3840, 1080), (1920, 1080),
                            (1600, 900), (1280, 720)]
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        self.full_screen_resolutions = (screen_width, screen_height)
        self.last_screen_pos = (0, 0)
        self.is_fullscreen = False        
        self.hwnd = None
        
        self.tp_cam_init_tf = carla.Transform(carla.Location(x=-3.5, z=1.1), carla.Rotation(0.5,0,0))  # Third person view
        # self.fp_cam_init_tf = carla.Transform(carla.Location(x=0, z=1.8), carla.Rotation(0,0,0))  # First person view
        self.fp_cam_init_tf = carla.Transform(carla.Location(x=-0.8, y=0.0, z=1.8),
                                           carla.Rotation(pitch=0, yaw=-180, roll=0))
        
        self.tp_cam_offset = [[0,0,0],[0,0,0]]
        self.fp_cam_offset = [[0,0,0],[0,0,0]]
        
        self.close_event = False
        self.setup_pygame()
        self.spawn_cameras()

    def find_new_ego(self):
        """Function to find a new ego vehicle in the world."""
        self.vehicle = None
        while self.vehicle is None:
            print("Searching for a new ego vehicle...")
            time.sleep(1)
            self.vehicle = self.get_ego()
            if self.vehicle:
                print("New ego vehicle detected")

    def get_ego(self):
        ego_vehicle = None 
        for actor in self.world.get_actors().filter('vehicle.*'):
            if actor.attributes.get('role_name') in ['hero', 'ego_vehicle']:
                ego_vehicle = actor
                break
        if ego_vehicle == None:
            return None
        return ego_vehicle

    def spawn_cameras(self): 
        # Setup two cameras
        camera_bp = self.world.get_blueprint_library().find('sensor.camera.rgb')

        if self.is_fullscreen:
            camera_bp.set_attribute('image_size_x', str(
                self.full_screen_resolutions[0]))
            camera_bp.set_attribute('image_size_y', str(
                self.full_screen_resolutions[1]))
        else:
            camera_bp.set_attribute('image_size_x', str(
                self.resolutions[self.resolution_index][0]))
            camera_bp.set_attribute('image_size_y', str(
                self.resolutions[self.resolution_index][1]))


        if self.active_camera_index == 0:
            if self.fp_cam is not None:
                self.fp_cam.stop()
                self.fp_cam.destroy()
                self.fp_cam = None
            self.tp_cam = self.world.spawn_actor(
                camera_bp, self.tp_cam_init_tf, attach_to=self.vehicle, 
                attachment_type=carla.AttachmentType.SpringArmGhost)
            time.sleep(0.2)
            self.trans_cam_to_new_tf()
            self.tp_cam.listen(lambda image: self.render(image))
        elif self.active_camera_index == 1:
            if self.tp_cam is not None:
                self.tp_cam.stop()
                self.tp_cam.destroy()
                self.tp_cam = None
            self.fp_cam = self.world.spawn_actor(
                camera_bp, self.fp_cam_init_tf, attach_to=self.vehicle)
            time.sleep(0.2)
            self.trans_cam_to_new_tf(cam_index=1)
            self.fp_cam.listen(lambda image: self.render(image))

    def destroy_cameras(self):
        if self.tp_cam is not None:
            self.tp_cam.stop()
            self.tp_cam.destroy()
            self.tp_cam = None
        if self.fp_cam is not None:
            self.fp_cam.stop()
            self.fp_cam.destroy()
            self.fp_cam = None

    def setup_pygame(self):
        pygame.init()        
        self.set_display_mode()

    def set_display_mode(self):
        self.destroy_cameras()
        if self.is_fullscreen:
            self.display = pygame.display.set_mode(
                self.full_screen_resolutions, flags=(pygame.FULLSCREEN),) 
        else:
            self.display = pygame.display.set_mode(
                self.resolutions[self.resolution_index], flags=(pygame.HWSURFACE | pygame.DOUBLEBUF)) 
        self.hwnd = pygame.display.get_wm_info()["window"]
        self.spawn_cameras()
    
    def switch_display_mode(self):
        print(self.full_screen_resolutions)
        if self.is_fullscreen: 
            self.resolution_index = self.last_resolution_index
        else:
            window_rect = win32gui.GetWindowRect(self.hwnd)
            # print(window_rect)
            self.last_screen_pos = (window_rect[0],window_rect[1])
            # pygame.display.set_pos((0, 0))
            self.last_resolution_index = self.resolution_index  
            self.resolution_index = 0
        self.is_fullscreen = not self.is_fullscreen
        self.set_display_mode()

    def update_camera(self, offset=None, rotation=None, reset=False):        
        # will not work when in first person view
        if self.active_camera_index == 1:
            return
        if reset:
            self.tp_cam_offset = [[0,0,0],[0,0,0]]
        else:
            if offset:
                self.tp_cam_offset[0] = [self.tp_cam_offset[0][i] + offset[i] for i in range(3)]
            if rotation:
                self.tp_cam_offset[1] = [self.tp_cam_offset[1][i] + rotation[i] for i in range(3)]
        self.trans_cam_to_new_tf()
        
    def trans_cam_to_new_tf(self, cam_index=0):
        if cam_index == 0:
            new_loc = self.tp_cam_init_tf.location + carla.Location(self.tp_cam_offset[0][0],
                                                                    self.tp_cam_offset[0][1],
                                                                    self.tp_cam_offset[0][2])
            new_rot = carla.Rotation(self.tp_cam_init_tf.rotation.pitch + self.tp_cam_offset[1][0],
                                    self.tp_cam_init_tf.rotation.yaw + self.tp_cam_offset[1][1],
                                    self.tp_cam_init_tf.rotation.roll + self.tp_cam_offset[1][2])
            # print(f'{new_loc.x}\t{new_loc.y}\t{new_loc.z}\t{new_rot.pitch}\t{new_rot.yaw}\t{new_rot.roll}\t')
            self.tp_cam.set_transform(carla.Transform(new_loc, new_rot))
        else:
            new_loc = self.fp_cam_init_tf.location + carla.Location(self.fp_cam_offset[0][0],
                                                                    self.fp_cam_offset[0][1],
                                                                    self.fp_cam_offset[0][2])
            new_rot = carla.Rotation(self.fp_cam_init_tf.rotation.pitch + self.fp_cam_offset[1][0],
                                    self.fp_cam_init_tf.rotation.yaw + self.fp_cam_offset[1][1],
                                    self.fp_cam_init_tf.rotation.roll + self.fp_cam_offset[1][2])
            
            self.fp_cam.set_transform(carla.Transform(new_loc, new_rot))

    def render(self, image):
        try:
            image.convert(cc.Raw)
            array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (image.height, image.width, 4))
            array = array[:, :, :3]
            array = array[:, :, ::-1]
            surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
            self.display.blit(surface, (0, 0))
            pygame.display.flip()
        except Exception as e:
            print(f"Exception caught during rendering: {e}")

    def process_inputs(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.close_event = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.close_event = True
                if event.key == pygame.K_w:
                    self.update_camera(offset=[0,0,0.5])
                elif event.key == pygame.K_s:
                    self.update_camera(offset=[0,0,-0.5])
                elif event.key == pygame.K_a:
                    self.update_camera(offset=[0,-0.5,0])
                elif event.key == pygame.K_d:
                    self.update_camera(offset=[0,0.5,0])
                elif event.key == pygame.K_f:
                    self.update_camera(offset=[0.5,0,0])
                elif event.key == pygame.K_b:
                    self.update_camera(offset=[-0.5,0,0])
                elif event.key == pygame.K_q:
                    self.update_camera(rotation=[0,0.5,0])
                elif event.key == pygame.K_e:
                    self.update_camera(rotation=[0,-0.5,0])
                elif event.key == pygame.K_PAGEUP:
                    self.update_camera(rotation=[0.5,0,0])
                elif event.key == pygame.K_PAGEDOWN:
                    self.update_camera(rotation=[-0.5,0,0])
                elif event.key == pygame.K_r:
                    self.update_camera(reset=True)

                elif event.key == pygame.K_p:
                    if not self.is_fullscreen:
                        self.resolution_index = (
                            self.resolution_index + len(self.resolutions) - 1) % len(self.resolutions)
                        self.set_display_mode()

                elif event.key == pygame.K_v:
                    self.active_camera_index = (
                        self.active_camera_index + 1) % 2
                    self.spawn_cameras()

                elif event.key == pygame.K_F11:
                    self.switch_display_mode()

    def run(self):
        while not self.close_event:
            self.process_inputs()
            
            # Check if the ego vehicle is still alive
            if self.vehicle is None or not self.vehicle.is_alive:
                self.find_new_ego()
                self.spawn_cameras()
        # while not self.close_event:
        #     self.process_inputs()
        self.close()
    
    def close(self):
        self.destroy_cameras()

def get_actor_blueprints(world, filter, generation):
    bps = world.get_blueprint_library().filter(filter)

    if generation.lower() == "all":
        return bps

    # If the filter returns only one bp, we assume that this one needed
    # and therefore, we ignore the generation
    if len(bps) == 1:
        return bps

    try:
        int_generation = int(generation)
        # Check if generation is in available generations
        if int_generation in [1, 2]:
            bps = [x for x in bps if int(x.get_attribute('generation')) == int_generation]
            return bps
        else:
            print("   Warning! Actor Generation is not valid. No actor will be spawned.")
            return []
    except:
        print("   Warning! Actor Generation is not valid. No actor will be spawned.")
        return []

if __name__ == "__main__":
    client = carla.Client("10.26.48.131", 5000)
    client.set_timeout(10.0)
    world = client.get_world()
    
    # bps = world.get_blueprint_library().filter('vehicle.tesla.model3')
    
    # ego_tf = world.get_map().get_spawn_points()[0]
    # ego_bp = bps[0]
    # ego_bp.set_attribute('role_name', 'ego_vehicle')
    # ego_vehicle = world.try_spawn_actor(ego_bp, ego_tf)
    visualizer = Visualizer(client)
    visualizer.run()
