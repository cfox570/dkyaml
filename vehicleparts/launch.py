import time
#    car.add(AiLaunch(cfg.AI_LAUNCH_DURATION, cfg.AI_LAUNCH_THROTTLE, cfg.AI_LAUNCH_KEEP_ENABLED),


class AiLaunch():
    '''
    This part will apply a large thrust on initial activation. This is to help
    in racing to start fast and then the ai will take over quickly when it's
    up to speed.
    '''

    def __init__(self, cfg):
        self.active = False
        self.enabled = False
        self.timer_start = None
        self.timer_duration = cfg.AI_LAUNCH_DURATION
        self.launch_throttle = cfg.AI_LAUNCH_THROTTLE
        self.prev_mode = None
        self.trigger_on_switch = cfg.AI_LAUNCH_KEEP_ENABLED
        
        # vehicle parameters       
        self.inputs = ['user/mode', 'pilot/throttle']
        self.outputs = ['pilot/throttle']
        self.threaded = False
        self.run_condition = None
        
    def enable_ai_launch(self):
        self.enabled = True
        print('AiLauncher is enabled.')

    def run(self, mode, ai_throttle):
        new_throttle = ai_throttle

        if mode != self.prev_mode:
            self.prev_mode = mode
            if mode == "local" and self.trigger_on_switch:
                self.enabled = True

        if mode == "local" and self.enabled:
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
            print('AiLauncher is active!!!')
            new_throttle = self.launch_throttle

        return new_throttle

    def shutdown(self):
       pass
