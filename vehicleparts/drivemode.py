
class DriveMode:
    def __init__(self, cfg):   

        # vehicle parameters       
        self.inputs = ['user/mode', 'user/angle', 'user/throttle', 'pilot/angle', 'pilot/throttle', 'AImultiplier']
        self.outputs = ['angle', 'throttle']
        self.threaded = False
        self.run_condition = None

    def run(self, mode, user_angle, user_throttle, pilot_angle, pilot_throttle, ai_throttle_multiplier):
        if mode == 'user':
             return user_angle, user_throttle

        elif mode == 'local_angle':
            return pilot_angle if pilot_angle else 0.0, user_throttle

        else: 
            angle =  pilot_angle if pilot_angle else 0.0
            throttle = pilot_throttle * ai_throttle_multiplier if pilot_throttle else 0.0
            return angle, throttle

    def shutdown(self):
        pass

