import os
import time
import gym
import gym_donkeycar
import numpy

import donkeycar.vehiclepartsfactory.partfactory as factory

def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

class DonkeyGymEnv_Original(factory.Part):

    def __init__(self, sim_path, host="127.0.0.1", port=9091, headless=0, env_name="donkey-generated-track-v0", sync="asynchronous", 
            conf={}, record_location=False, record_gyroaccel=False, record_velocity=False, record_lidar=False, delay=0, drive_loop_hz=20):
        super().__init__(loop_time = 1/drive_loop_hz)
        if sim_path != "remote":
            if not os.path.exists(sim_path):
                raise Exception(
                    "The path you provided for the sim does not exist.")

            if not is_exe(sim_path):
                raise Exception("The path you provided is not an executable.")

        conf["exe_path"] = sim_path
        conf["host"] = host
        conf["port"] = port
        conf["guid"] = 0
        conf["frame_skip"] = 1
        self.env = gym.make(env_name, conf=conf)
        self.frame = self.env.reset()
        self.action = [0.0, 0.0, 0.0]
        self.running = True
        self.info = {'pos': (0., 0., 0.),
                     'speed': 0,
                     'cte': 0,
                     'gyro': (0., 0., 0.),
                     'accel': (0., 0., 0.),
                     'vel': (0., 0., 0.)}
        self.delay = float(delay) / 1000
        self.record_location = record_location
        self.record_gyroaccel = record_gyroaccel
        self.record_velocity = record_velocity
        self.record_lidar = record_lidar

        self.buffer = []

    def delay_buffer(self, frame, info):
        now = time.time()
        buffer_tuple = (now, frame, info)
        self.buffer.append(buffer_tuple)

        # go through the buffer
        num_to_remove = 0
        for buf in self.buffer:
            if now - buf[0] >= self.delay:
                num_to_remove += 1
                self.frame = buf[1]
            else:
                break

        # clear the buffer
        del self.buffer[:num_to_remove]

#     def update(self):
#         while self.running:
#             if self.delay > 0.0:
#                 current_frame, _, _, current_info = self.env.step(self.action)
#                 self.delay_buffer(current_frame, current_info)
#             else:
#                 self.frame, _, _, self.info = self.env.step(self.action)
# 
#     def run_threaded(self, steering, throttle, brake=None):
#         if steering is None or throttle is None:
#             steering = 0.0
#             throttle = 0.0
#         if brake is None:
#             brake = 0.0
# 
#         self.action = [steering, throttle, brake]
# 
#         # Output Sim-car position information if configured
#         outputs = [self.frame]
#         if self.record_location:
#             outputs += self.info['pos'][0],  self.info['pos'][1],  self.info['pos'][2],  self.info['speed'], self.info['cte']
#         if self.record_gyroaccel:
#             outputs += self.info['gyro'][0], self.info['gyro'][1], self.info['gyro'][2], self.info['accel'][0], self.info['accel'][1], self.info['accel'][2]
#         if self.record_velocity:
#             outputs += self.info['vel'][0],  self.info['vel'][1],  self.info['vel'][2]
#         if self.record_lidar:
#             outputs += self.info['lidar']
#         if len(outputs) == 1:
#             return self.frame
#         else:
#             return outputs
# 
#     def shutdown(self):
#         self.running = False
#         time.sleep(0.2)
#         self.env.close()

    def read_from_bus(self):
        self.angle = self.data_bus.read('angle')
        self.throttle = self.data_bus.read('throttle')
        self.brake = self.data_bus.read('brake')

    def write_to_bus(self):
        self.data_bus.write('cam/image_array', numpy.ndarray, self.frame)
        
    def operate(self):
        if self.angle is None or self.throttle is None:
            self.steering = 0.0
            self.throttle = 0.0
        if self.brake is None:
            self.brake = 0.0
            
        self.action = [self.angle, self.throttle, self.brake]
        
        if self.delay > 0.0:
            current_frame, _, _, current_info = self.env.step(self.action)
            self.delay_buffer(current_frame, current_info)
        else:
            self.frame, _, _, self.info = self.env.step(self.action)


    def stop(self):
        time.sleep(0.2)
        self.env.close()
        super().stop()


class DonkeyGymEnv(DonkeyGymEnv_Original):
    def __init__(self, cfg):
        super(DonkeyGymEnv, self).__init__(cfg.DONKEY_SIM_PATH, host=cfg.SIM_HOST, env_name=cfg.DONKEY_GYM_ENV_NAME, conf=cfg.GYM_CONF, delay=cfg.SIM_ARTIFICIAL_LATENCY, drive_loop_hz=cfg.DRIVE_LOOP_HZ)
       
#        # vehicle parameters       
#        self.inputs  = ['angle', 'throttle', 'brake']
#        self.outputs = ['cam/image_array']
#        self.threaded = True
        self.run_part = True

