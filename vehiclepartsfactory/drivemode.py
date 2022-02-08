import donkeycar.vehiclepartsfactory.partfactory as factory

class DriveMode(factory.Part):
    def __init__(self, cfg):   
        super().__init__(loop_time = 1/cfg.DRIVE_LOOP_HZ)
        # vehicle parameters       
#         self.inputs = ['user/mode', 'user/angle', 'user/throttle', 'pilot/angle', 'pilot/throttle', 'AImultiplier']
#         self.outputs = ['angle', 'throttle']
#         self.run_condition = None
        self.run_part = True
        
        self.angle = 0.0
        self.throttle = 0.0


    def read_from_bus(self):
        self.mode = self.data_bus.read('user/mode')
        self.user_angle = self.data_bus.read('user/angle')
        self.pilot_angle = self.data_bus.read('pilot/angle')
        self.user_throttle = self.data_bus.read('user/throttle')
        self.pilot_throttle = self.data_bus.read('pilot/throttle')
        self.multiplier = self.data_bus.read('AImultiplier')
        
    def write_to_bus(self):
        self.data_bus.write('angle', float, self.angle)
        self.data_bus.write('throttle', float, self.throttle)
        
    def operate(self):
        self.angle = 0.0
        self.throttle = 0.0
        
        if self.mode is not None:
            if self.mode == 'user' and \
               self.user_angle is not None and \
               self.user_throttle is not None:
                self.angle = self.user_angle
                self.throttle = self.user_throttle

        if self.mode is not None and \
           self.user_angle is not None and \
           self.user_throttle is not None and \
           self.pilot_angle is not None and \
           self.pilot_throttle is not None and \
           self.multiplier is not None:
           
            if self.mode =='user':
                self.angle = self.user_angle
                self.throttle = self.user_throttle
        
            elif self.mode == 'local_angle':
                self.angle = self.pilot_angle if self.pilot_angle else 0.0
                self.throttle = self.user_throttle

            else: 
                self.angle =  self.pilot_angle if self.pilot_angle else 0.0
                self.throttle = (self.pilot_throttle * self.multiplier) if self.pilot_throttle else 0.0


#     def stop(self):
#         super().stop()


