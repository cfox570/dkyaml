
import donkeycar.vehiclepartsfactory.partfactory as factory

class Dashboard(factory.Part):
    def __init__(self, cfg):
        super().__init__(loop_time = 1/cfg.DRIVE_LOOP_HZ)
        self.msg = cfg.DASHBOARD_MESSAGE
        self.run_part = True

    def read_from_bus(self):
        self.angle = self.data_bus.read('angle')
        self.throttle = self.data_bus.read('throttle')
        self.mode = self.data_bus.read('user/mode')

        
    def operate(self):
        if self.angle is not None and self.throttle is not None:
            print (f'{self.mode:}: s: {self.angle: 4.2f} t: {self.throttle: 4.2f}', end='\r')
        else:
#             print (f'{self.msg}: No available data', end='\n')
            pass