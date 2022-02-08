
class PilotCondition:
    def __init__(self, cfg):   
        
        # vehicle parameters       
        self.inputs = ['user/mode']
        self.outputs = ['run_pilot']
        self.threaded = False
        self.run_condition = None

    def run(self, mode):
        return False if mode == 'user' else True

    def shutdown(self):
        pass

