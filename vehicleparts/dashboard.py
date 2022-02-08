

class Dashboard:
    def __init__(self, cfg):
        self.msg = cfg.DASHBOARD_MESSAGE
        
        # vehicle parameters       
        self.inputs = ['angle', 'throttle']
        self.outputs = []
        self.threaded = False
        self.run_condition = None

    def run(self, steering, throttle):
        if steering is not None and throttle is not None:
            print (f's: {steering: 4.2f} t: {throttle: 4.2f}', end='\r')

    def shutdown(self):
        pass