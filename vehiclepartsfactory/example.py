
import donkeycar.vehiclepartsfactory.partfactory as factory

class ExamplePart(factory.Part):
    def __init__(self, cfg):
        super().__init__(loop_time = 1/cfg.DRIVE_LOOP_HZ)
        self.run_part = True

    def read_from_bus(self):
    # Thread is locked while reading data; only read
        self.data1 = self.data_bus.read('data1')
        self.data2 = self.data_bus.read('data2')
    
    def write_to_bus(self):
    # Thread is locked while writing data; only write
        self.data_bus.write('out1', float, self.data2)
        self.data_bus.write('out2', int, self.data1)
        
    def operate(self):
    # Process data and save to object variables
        self.data1 = 3 * self.data1
    
#     def stop(self):
#         # add part specific actions here then call super
#         super().stop()