
# Note: Does not handle parameter: other_array in keras.py
import donkeycar as dk
import donkeycar.vehiclepartsfactory.partfactory as factory

class AI_Pilot(factory.Part):
    def __init__(self, cfg):   
        super().__init__(loop_time = 1/cfg.DRIVE_LOOP_HZ)
        self.kl = dk.utils.get_model_by_type(None, cfg)
        self.kl.load(cfg.MODEL_PATH)
        self.run_part = False
          
    def read_from_bus(self):
        self.run_part = self.data_bus.read('run_pilot')
        if self.run_part is not None:
            if self.run_part:
                self.image = self.data_bus.read('cam/image_array')

    def write_to_bus(self):
        self.data_bus.write('pilot/angle', float, float(self.angle))
        self.data_bus.write('pilot/throttle', float, float(self.throttle))
        
    def operate(self):
    # Note: Does not handle parameter: other_array in keras.py
        if self.image is not None:
            self.angle, self.throttle = self.kl.run(self.image)
        
    def stop(self):
        self.kl.shutdown()
        super().stop()


