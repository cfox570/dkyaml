import time
import donkeycar.vehiclepartsfactory.partfactory as factory


class AiLaunch(factory.Part):
    '''
    This part will apply a large thrust on initial activation. This is to help
    in racing to start fast and then the ai will take over quickly when it's
    up to speed.
    '''

    def __init__(self, cfg):
        super().__init__(loop_time = 1/cfg.DRIVE_LOOP_HZ)
        self.active = False
        self.enabled = False
        self.timer_start = None
        self.timer_duration = cfg.AI_LAUNCH_DURATION
        self.launch_throttle = cfg.AI_LAUNCH_THROTTLE
        self.prev_mode = None
        self.trigger_on_switch = cfg.AI_LAUNCH_KEEP_ENABLED
        
        self.run_part = True
        
#     def enable_ai_launch(self):
#         self.enabled = True
#         print('AiLauncher is enabled.')

#     def run(self, mode, ai_throttle):
#         new_throttle = ai_throttle
# 
#         if mode != self.prev_mode:
#             self.prev_mode = mode
#             if mode == "local" and self.trigger_on_switch:
#                 self.enabled = True
# 
#         if mode == "local" and self.enabled:
#             if not self.active:
#                 self.active = True
#                 self.timer_start = time.time()
#             else:
#                 duration = time.time() - self.timer_start
#                 if duration > self.timer_duration:
#                     self.active = False
#                     self.enabled = False
#         else:
#             self.active = False
# 
#         if self.active:
#             print('AiLauncher is active!!!')
#             new_throttle = self.launch_throttle
# 
#         return new_throttle

    def read_from_bus(self):
        self.mode = self.data_bus.read('user/mode')
        self.throttle = self.data_bus.read('pilot/throttle')
        
    def write_to_bus(self):
        self.data_bus.write('pilot/throttle', float, self.throttle)
        
    def operate(self):
#         print(f'AiLauncher operating... {self.throttle} {self.mode}')
        if self.throttle is not None and self.mode is not None:
            new_throttle = self.throttle

            if self.mode != self.prev_mode:
                self.prev_mode = self.mode
                if self.mode == "local" and self.trigger_on_switch:
                    self.enabled = True
                    print('AILauncher enabled...')

            if self.mode == "local" and self.enabled:
                if not self.active:
                    self.active = True
                    self.timer_start = time.time()
                else:
                    duration = time.time() - self.timer_start
                    if duration > self.timer_duration:
                        self.active = False
                        self.enabled = False
            else:
                self.active = False

            if self.active:
                print(f'AiLauncher is active!!!                       {self.launch_throttle}')
                new_throttle = self.launch_throttle

            self.throttle = new_throttle
        
#     def stop(self):
#         super().stop()