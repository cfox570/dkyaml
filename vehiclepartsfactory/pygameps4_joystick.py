'''
PyGame PS4 Joystick mapping on MacOS
'''

from donkeycar.vehiclepartsfactory.jscontroller import PyGameJoystick, JoystickController

class PyGamePS4Joystick(PyGameJoystick):
    '''
    An interface to a physical PS4 joystick available via pygame
    Windows setup: https://github.com/nefarius/ScpToolkit/releases/tag/v1.6.238.16010
    '''
    def __init__(self, *args, **kwargs):
        super(PyGamePS4Joystick, self).__init__(*args, **kwargs)
        
        # Not implemented in code
        # Hat (first,second)
        # first  - dpad_left/right
        # second  - dpad_down/up
        
        self.axis_names = {
            0x00 : 'left_stick_horz',
            0x01 : 'left_stick_vert',
            0x04 : 'right_stick_vert',
            0x03 : 'right_stick_horz',
            
            0x02 : 'L2_trigger_axis', # default value is -1.0 so need to offset value if used
            0x05 : 'R2_trigger_axis', # default value is -1.0 so need to offset value if used
        }

        self.button_names = {
            0 : "cross",
            1 : "circle",
            2 : 'square',
            3 : "triangle",

            8 : 'share',
            9 : 'PS',
            10 : 'options',

            4 : 'L1',
            5 : 'R1',
            
            6 : 'Left_stick',
            7 : 'Right_stick',
        }

# class PyGamePS4JoystickController_Original(JoystickController):

#     def __init__(self, which_js=0, *args, **kwargs):
#         super(PyGamePS4JoystickController, self).__init__(*args, **kwargs)

class PyGamePS4JoystickController(JoystickController):
    '''
    A Controller object that maps inputs to actions
    '''
    def __init__(self, cfg):
        super(PyGamePS4JoystickController, self).__init__(throttle_dir=cfg.JOYSTICK_THROTTLE_DIR,
                            throttle_scale=cfg.JOYSTICK_THROTTLE_SCALE,
                            steering_scale=cfg.JOYSTICK_STEERING_SCALE,
                            auto_record_on_throttle=cfg.AUTO_RECORD_ON_THROTTLE,
                            ai_throttle_multiplier=cfg.AI_THROTTLE_MULT,
                            drive_loop_hz = cfg.DRIVE_LOOP_HZ)
                                                    
        self.set_deadzone(cfg.JOYSTICK_DEADZONE)
        
        self.which_js = 0
#         self.which_js=which_js

        #wait for joystick to be online
        import time
        while not self.init_js():
            time.sleep(1)
        
        self.print_controls()

    def init_js(self):
        '''
        attempt to init joystick
        '''
        try:
            self.js = PyGamePS4Joystick(which_js=self.which_js)
        except Exception as e:
            print(e)
            self.js = None
        return self.js is not None
    
    def init_trigger_maps(self):
        '''
        init set of mapping from buttons to function calls for ps4
        '''

        self.button_down_trigger_map = {
#             'square' : None,
            'circle' : self.toggle_manual_recording,
            'triangle' : self.erase_last_N_records,
            'cross' : self.emergency_stop,
            
            'L1' : self.increase_max_throttle,
            'R1' : self.decrease_max_throttle,
            
#             'L2'          : do_nothing,
            'Left_stick'  : self.decrease_ai_throttle_multiplier,
            
#             'R2'          : do_nothing,
            'Right_stick' : self.increase_ai_throttle_multiplier,
            
#           'PAD'     : do_nothing,
            'share'   : self.toggle_mode,          
            'options' : self.toggle_constant_throttle,
            'PS'      : self.toggle_moving
        }

        self.axis_trigger_map = {
            'left_stick_horz'  : self.set_steering,
#             'right_stick_horz' : None,
            'right_stick_vert' : self.set_throttle,
#             'dpad_leftright'   : self.change_ai_throttle_multiplier,
        }
        
    def mainthread(self):
        # process that is called by vehicle main ; where statements need to be executed outside of thread
        import pygame
        pygame.event.pump()
