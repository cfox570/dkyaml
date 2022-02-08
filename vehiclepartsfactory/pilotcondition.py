import donkeycar.vehiclepartsfactory.partfactory as factory

class PilotCondition(factory.Part):
    def __init__(self, cfg):   
        super().__init__(loop_time = 1/cfg.DRIVE_LOOP_HZ)
#         # vehicle parameters       
#         self.inputs = ['user/mode']
#         self.outputs = ['run_pilot']
#         self.run_condition = None
        self.run_part = True

#     def run(self, mode):
#         return False if mode == 'user' else True

    def read_from_bus(self):
        self.mode = self.data_bus.read('user/mode')
        
    def write_to_bus(self):
        self.data_bus.write('run_pilot', bool, self.run_pilot)
        
    def operate(self):
        if self.mode is not None:
            self.run_pilot = False if self.mode == 'user' else True
        
#     def stop(self):
#         super().stop()