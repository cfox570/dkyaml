
# Note: Does not handle parameter: other_array in keras.py
import donkeycar as dk

class AI_Pilot:
    def __init__(self, cfg):   
        self.kl = dk.utils.get_model_by_type(None, cfg)
        self.kl.load(cfg.MODEL_PATH)
        
        # vehicle parameters       
        self.inputs = ['cam/image_array']
        self.outputs = ['pilot/angle', 'pilot/throttle']
        self.threaded = False
        self.run_condition = 'run_pilot'

    def run(self,image):
    # Note: Does not handle parameter: other_array in keras.py
        return self.kl.run(image)

    def shutdown(self):
        self.kl.shutdown()
