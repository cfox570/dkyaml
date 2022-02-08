
import os
import array
import time
import struct
import random
from threading import Thread
import logging

from prettytable import PrettyTable

#import for syntactical ease
from donkeycar.parts.web_controller.web import LocalWebController
from donkeycar.parts.web_controller.web import WebFpv
import donkeycar.vehiclepartsfactory.partfactory as factory

class JoystickController(factory.Part):
    '''
    JoystickController is a base class. You will not use this class directly,
    but instantiate a flavor based on your joystick type. See classes following this.

    Joystick client using access to local physical input. Maps button
    presses into actions and takes action. Interacts with the Donkey part
    framework.
    '''

    ES_IDLE = -1
    ES_START = 0
    ES_THROTTLE_NEG_ONE = 1
    ES_THROTTLE_POS_ONE = 2
    ES_THROTTLE_NEG_TWO = 3

    def __init__(self, poll_delay = 0.0,
                 throttle_scale = 1.0,
                 steering_scale = 1.0,
                 throttle_dir = -1.0,
                 dev_fn = '/dev/input/js0',
                 auto_record_on_throttle = True,
                 initial_mode = 'user', #FX
                 ai_throttle_multiplier = 1.0, #FX
                 drive_loop_hz = 20): #FX
                 
        super().__init__(loop_time = 1/drive_loop_hz)
        self.angle = 0.0
        self.throttle = 0.0
        self.mode = initial_mode
        self.poll_delay = poll_delay
        self.running = True
        self.last_throttle_axis_val = 0
        self.throttle_scale = throttle_scale
        self.steering_scale = steering_scale
        self.throttle_dir = throttle_dir
        self.recording = False
        self.constant_throttle = False
        self.auto_record_on_throttle = auto_record_on_throttle
        self.dev_fn = dev_fn
        self.js = None
        self.tub = None
        self.num_records_to_erase = 100
        self.estop_state = self.ES_IDLE
        self.chaos_monkey_steering = None
        self.dead_zone = 0.0

        self.button_down_trigger_map = {}
        self.button_up_trigger_map = {}
        self.axis_trigger_map = {}
        self.init_trigger_maps()
        
        self.ai_throttle_multiplier = ai_throttle_multiplier
        self.joy_command = 0 # 1 = stop vehicle loop;  2 = previous waypoint; 3 = next waypoint; 4 = print waypoint
        self.moving = True  # initial state is car is moving when not moving throttle,steering forced to zero
        print ("Initial mode is " + self.mode)
        
        self.run_part = True

        
    def init_js(self):
        '''
        Attempt to init joystick. Should be definied by derived class
        Should return true on successfully created joystick object
        '''
        raise(Exception("Subclass needs to define init_js"))

    def init_trigger_maps(self):
        '''
        Creating mapping of buttons to functions.
        Should be definied by derived class
        '''
        raise(Exception("init_trigger_maps"))

    def set_deadzone(self, val):
        '''
        sets the minimim throttle for recording and running
        '''
        self.dead_zone = val

    def print_controls(self):
        '''
        print the mapping of buttons and axis to functions
        '''
        pt = PrettyTable()
        pt.field_names = ["control", "action"]
        for button, control in self.button_down_trigger_map.items():
            pt.add_row([button, control.__name__])
        for axis, control in self.axis_trigger_map.items():
            pt.add_row([axis, control.__name__])
        print("Joystick Controls:")
        print(pt)

    def set_button_down_trigger(self, button, func):
        '''
        assign a string button descriptor to a given function call
        '''
        self.button_down_trigger_map[button] = func

    def set_button_up_trigger(self, button, func):
        '''
        assign a string button descriptor to a given function call
        '''
        self.button_up_trigger_map[button] = func

    def set_axis_trigger(self, axis, func):
        '''
        assign a string axis descriptor to a given function call
        '''
        self.axis_trigger_map[axis] = func

    def set_tub(self, tub):
        self.tub = tub

    def erase_last_N_records(self):
        if self.tub is not None:
            try:
                self.tub.delete_last_n_records(self.num_records_to_erase)
                print('deleted last %d records.' % self.num_records_to_erase)
            except:
                print('failed to erase')

    def on_throttle_changes(self):
        '''
        turn on recording when non zero throttle in the user mode.
        '''
        if self.auto_record_on_throttle:
            self.recording = (abs(self.throttle) > self.dead_zone and self.mode == 'user')

    def emergency_stop(self):
        '''
        initiate a series of steps to try to stop the vehicle as quickly as possible
        '''
        print('E-Stop!!!')
        self.mode = "user"
        self.recording = False
        self.constant_throttle = False
        self.estop_state = self.ES_START
        self.throttle = 0.0

#     def update(self):
#         '''
#         poll a joystick for input events
#         '''
# 
# #         if self.__class__.__name__ != 'PyGamePS4JoystickController':
# #             #wait for joystick to be online
# #             while self.running and self.js is None and not self.init_js():
# #                 print('waiting for joystick/gamepad...')
# #                 time.sleep(1)
# 
#         while self.running:
#             button, button_state, axis, axis_val = self.js.poll()
# 
#             if axis is not None and axis in self.axis_trigger_map:
#                 '''
#                 then invoke the function attached to that axis
#                 '''
#                 self.axis_trigger_map[axis](axis_val)
# 
#             if button and button_state >= 1 and button in self.button_down_trigger_map:
#                 '''
#                 then invoke the function attached to that button
#                 '''
#                 self.button_down_trigger_map[button]()
# 
#             if button and button_state == 0 and button in self.button_up_trigger_map:
#                 '''
#                 then invoke the function attached to that button
#                 '''
#                 self.button_up_trigger_map[button]()
# 
#             time.sleep(self.poll_delay)

    def do_nothing(self, param):
        '''assign no action to the given axis
        this is useful to unmap certain axes, for example when swapping sticks
        '''
        pass

    def set_steering(self, axis_val):
        self.angle = self.steering_scale * axis_val
#         print(f'Angle {axis_val}')
 
    def set_throttle(self, axis_val):
        #this value is often reversed, with positive value when pulling down
        self.last_throttle_axis_val = axis_val
        self.throttle = (self.throttle_dir * axis_val * self.throttle_scale)
        #print("throttle", self.throttle)
        self.on_throttle_changes()

    def remove_carkey(self):
        '''
        remove the carkey
        '''
        self.joy_command = 1
    
    def toggle_moving(self):
        '''
        toggle moving on/off
        controls whether to output real values for steering, throttle or zero values
        '''
        if self.moving:
            print("Not moving...")
            self.moving = False
        else:
            print("Moving...")
            self.moving = True
            
#         self.moving = False if self.moving else True

    def toggle_manual_recording(self):
        '''
        toggle recording on/off
        '''
        if self.auto_record_on_throttle:
            print('auto record on throttle is enabled.')
        elif self.recording:
            self.recording = False
        else:
            self.recording = True

        print('recording:', self.recording)

    def increase_max_throttle(self):
        '''
        increase throttle scale setting
        '''
        self.throttle_scale = round(min(1.0, self.throttle_scale + 0.01), 2)
        if self.constant_throttle:
            self.throttle = self.throttle_scale
            self.on_throttle_changes()
        else:
            self.throttle = (self.throttle_dir * self.last_throttle_axis_val * self.throttle_scale)

        print('throttle_scale:', self.throttle_scale)

    def decrease_max_throttle(self):
        '''
        decrease throttle scale setting
        '''
        self.throttle_scale = round(max(0.0, self.throttle_scale - 0.01), 2)
        if self.constant_throttle:
            self.throttle = self.throttle_scale
            self.on_throttle_changes()
        else:
            self.throttle = (self.throttle_dir * self.last_throttle_axis_val * self.throttle_scale)

        print('throttle_scale:', self.throttle_scale)

    def increase_ai_throttle_multiplier(self): #fox
        '''
        increase the multiplier for the ai pilot_throttle
        '''
#         self.ai_throttle_multiplier = round((self.ai_throttle_multiplier + 0.2), 2)
        self.ai_throttle_multiplier = self.ai_throttle_multiplier + 0.2
        print ('\nAI_throttle_multiplier+:', self.ai_throttle_multiplier)
 
    def decrease_ai_throttle_multiplier(self): #fox
        '''
        decrease the multiplier for the ai pilot_throttle
        '''
#         self.ai_throttle_multiplier = round(max(0.0, self.ai_throttle_multiplier - 0.2), 2)
        self.ai_throttle_multiplier = self.ai_throttle_multiplier - 0.2
        print ('\nAI_throttle_multiplier-:', self.ai_throttle_multiplier)
 
    def change_ai_throttle_multiplier(self, axis_val):  #fox
        if axis_val > 0:
            self.increase_ai_throttle_multiplier()
        else:
            self.decrease_ai_throttle_multiplier()

    def toggle_constant_throttle(self):
        '''
        toggle constant throttle
        '''
        if self.constant_throttle:
            self.constant_throttle = False
            self.throttle = 0
            self.on_throttle_changes()
        else:
            self.constant_throttle = True
            self.throttle = self.throttle_scale
            self.on_throttle_changes()
        print('constant_throttle:', self.constant_throttle)

    def toggle_mode(self):
        '''
        switch modes from:
        user: human controlled steer and throttle
        local_angle: ai steering, human throttle
        local: ai steering, ai throttle
        '''
#         if self.mode == 'user':
#             self.mode = 'local_angle'
#         elif self.mode == 'local_angle':
#             self.mode = 'local'
#         else:
#             self.mode = 'user'
#         print('new mode:', self.mode)

        if self.mode == 'user':
            self.mode = 'local'
        else:
            self.mode = 'user'
#             print(f'new mode: {self.mode}')

    def chaos_monkey_on_left(self):
        self.chaos_monkey_steering = -0.2

    def chaos_monkey_on_right(self):
        self.chaos_monkey_steering = 0.2

    def chaos_monkey_off(self):
        self.chaos_monkey_steering = None

#     def run_threaded(self, img_arr=None):
#         self.img_arr = img_arr
# 
#         '''
#         process E-Stop state machine
#         Fox: return ai_throttle_multiplier
#         '''
#         import pygame
#         pygame.event.pump()
#        
#         if not self.moving:
#             self.angle = 0
#             self.throttle = 0
#         
#         command = self.joy_command
#         self.joy_command = 0          
# 
#         
#         if self.estop_state > self.ES_IDLE:
#             if self.estop_state == self.ES_START:
#                 self.estop_state = self.ES_THROTTLE_NEG_ONE
#                 #return 0.0, -1.0 * self.throttle_scale, self.mode, False, self.ai_throttle_multiplier
#             elif self.estop_state == self.ES_THROTTLE_NEG_ONE:
#                 self.estop_state = self.ES_THROTTLE_POS_ONE
#                 #return 0.0, 0.01, self.mode, False, self.ai_throttle_multiplier
#             elif self.estop_state == self.ES_THROTTLE_POS_ONE:
#                 self.estop_state = self.ES_THROTTLE_NEG_TWO
#                 self.throttle = -1.0 * self.throttle_scale
#                 #return 0.0, self.throttle, self.mode, False, self.ai_throttle_multiplier
#             elif self.estop_state == self.ES_THROTTLE_NEG_TWO:
#                 self.throttle += 0.05
#                 if self.throttle >= 0.0:
#                     self.throttle = 0.0
#                     self.estop_state = self.ES_IDLE
#             return 0.0, self.throttle, self.mode, False, self.ai_throttle_multiplier, self.joy_command
# 
#         if self.chaos_monkey_steering is not None:
#             return self.chaos_monkey_steering, self.throttle, self.mode, False, self.ai_throttle_multiplier, command
#                     
#         return self.angle, self.throttle, self.mode, self.recording, self.ai_throttle_multiplier, command

#     def run(self, img_arr=None):
#         raise Exception("We expect for this part to be run with the threaded=True argument.")
#         self.run_threaded(img_arr)
#         return None, None, None, None, None #Fox see run_threaded

#     def shutdown(self):
#         #set flag to exit polling thread, then wait a sec for it to leave
#         print('JSController shutting down...')
#         self.running = False
#         time.sleep(0.5)


    def read_from_bus(self):
        self.img_arr = self.data_bus.read('cam/image_array')
        
    def write_to_bus(self):
        self.data_bus.write('user/angle', float, self.angle)
        self.data_bus.write('user/throttle', float, self.throttle)
        self.data_bus.write('user/mode', str, self.mode)
        self.data_bus.write('recording', bool, self.recording)
        self.data_bus.write('AImultiplier', float, self.ai_throttle_multiplier)
        self.data_bus.write('command', int, self.joy_command)
        
#         a = self.data_bus.read('user/angle')
#         t = self.data_bus.read('user/throttle')
#         m = self.data_bus.read('user/mode')
#         
#         print(f'Joystick {a} {t} {m}')
        
    def operate(self):
        '''
        process E-Stop state machine
        Fox: return ai_throttle_multiplier
        '''
        if not self.moving:
            self.angle = 0
            self.throttle = 0
            
        button, button_state, axis, axis_val = self.js.poll()

        if axis is not None and axis in self.axis_trigger_map:
            ''' then invoke the function attached to that axis '''
            self.axis_trigger_map[axis](axis_val)

        if button and button_state >= 1 and button in self.button_down_trigger_map:
            ''' then invoke the function attached to that button '''
            self.button_down_trigger_map[button]()

        if button and button_state == 0 and button in self.button_up_trigger_map:
            '''then invoke the function attached to that button'''
            self.button_up_trigger_map[button]()           
        
        if self.estop_state > self.ES_IDLE:
            if self.estop_state == self.ES_START:
                self.estop_state = self.ES_THROTTLE_NEG_ONE
                #return 0.0, -1.0 * self.throttle_scale, self.mode, False, self.ai_throttle_multiplier
            elif self.estop_state == self.ES_THROTTLE_NEG_ONE:
                self.estop_state = self.ES_THROTTLE_POS_ONE
                #return 0.0, 0.01, self.mode, False, self.ai_throttle_multiplier
            elif self.estop_state == self.ES_THROTTLE_POS_ONE:
                self.estop_state = self.ES_THROTTLE_NEG_TWO
                self.throttle = -1.0 * self.throttle_scale
                #return 0.0, self.throttle, self.mode, False, self.ai_throttle_multiplier
            elif self.estop_state == self.ES_THROTTLE_NEG_TWO:
                self.throttle += 0.05
                if self.throttle >= 0.0:
                    self.throttle = 0.0
                    self.estop_state = self.ES_IDLE
            self.angle = 0.0

        if self.chaos_monkey_steering is not None:
            self.angle = self.chaos_monkey_steering


class Joystick(object):
    '''
    An interface to a physical joystick
    '''
    def __init__(self, dev_fn='/dev/input/js0'):
        self.axis_states = {}
        self.button_states = {}
        self.axis_names = {}
        self.button_names = {}
        self.axis_map = []
        self.button_map = []
        self.jsdev = None
        self.dev_fn = dev_fn


    def init(self):
        try:
            from fcntl import ioctl
        except ModuleNotFoundError:
            self.num_axes = 0
            self.num_buttons = 0
            print("no support for fnctl module. joystick not enabled.")
            return False

        if not os.path.exists(self.dev_fn):
            print(self.dev_fn, "is missing")
            return False

        '''
        call once to setup connection to device and map buttons
        '''
        # Open the joystick device.
        print('Opening %s...' % self.dev_fn)
        self.jsdev = open(self.dev_fn, 'rb')

        # Get the device name.
        buf = array.array('B', [0] * 64)
        ioctl(self.jsdev, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
        self.js_name = buf.tobytes().decode('utf-8')
        print('Device name: %s' % self.js_name)

        # Get number of axes and buttons.
        buf = array.array('B', [0])
        ioctl(self.jsdev, 0x80016a11, buf) # JSIOCGAXES
        self.num_axes = buf[0]

        buf = array.array('B', [0])
        ioctl(self.jsdev, 0x80016a12, buf) # JSIOCGBUTTONS
        self.num_buttons = buf[0]

        # Get the axis map.
        buf = array.array('B', [0] * 0x40)
        ioctl(self.jsdev, 0x80406a32, buf) # JSIOCGAXMAP

        for axis in buf[:self.num_axes]:
            axis_name = self.axis_names.get(axis, 'unknown(0x%02x)' % axis)
            self.axis_map.append(axis_name)
            self.axis_states[axis_name] = 0.0

        # Get the button map.
        buf = array.array('H', [0] * 200)
        ioctl(self.jsdev, 0x80406a34, buf) # JSIOCGBTNMAP

        for btn in buf[:self.num_buttons]:
            btn_name = self.button_names.get(btn, 'unknown(0x%03x)' % btn)
            self.button_map.append(btn_name)
            self.button_states[btn_name] = 0
            #print('btn', '0x%03x' % btn, 'name', btn_name)

        return True


    def show_map(self):
        '''
        list the buttons and axis found on this joystick
        '''
        print ('%d axes found: %s' % (self.num_axes, ', '.join(self.axis_map)))
        print ('%d buttons found: %s' % (self.num_buttons, ', '.join(self.button_map)))


    def poll(self):
        '''
        query the state of the joystick, returns button which was pressed, if any,
        and axis which was moved, if any. button_state will be None, 1, or 0 if no changes,
        pressed, or released. axis_val will be a float from -1 to +1. button and axis will
        be the string label determined by the axis map in init.
        '''
        button = None
        button_state = None
        axis = None
        axis_val = None

        if self.jsdev is None:
            return button, button_state, axis, axis_val

        # Main event loop
        evbuf = self.jsdev.read(8)

        if evbuf:
            tval, value, typev, number = struct.unpack('IhBB', evbuf)

            if typev & 0x80:
                #ignore initialization event
                return button, button_state, axis, axis_val

            if typev & 0x01:
                button = self.button_map[number]
                #print(tval, value, typev, number, button, 'pressed')
                if button:
                    self.button_states[button] = value
                    button_state = value
                    logging.info("button: %s state: %d" % (button, value))

            if typev & 0x02:
                axis = self.axis_map[number]
                if axis:
                    fvalue = value / 32767.0
                    self.axis_states[axis] = fvalue
                    axis_val = fvalue
                    logging.debug("axis: %s val: %f" % (axis, fvalue))

        return button, button_state, axis, axis_val

class PyGameJoystick(object):
    def __init__( self,
                  poll_delay=0.0,
                  throttle_scale=1.0,
                  steering_scale=1.0,
                  throttle_dir=-1.0,
                  dev_fn='/dev/input/js0',
                  auto_record_on_throttle=True,
                  which_js=0):

        import pygame
        pygame.init()
        self.screen = pygame.display.set_mode([50,50]) # required to use joysticks. Click on box to make frontmost!!!
        # Initialize the joysticks
        sticks = 0
        while sticks == 0:
            pygame.event.pump()
            pygame.joystick.init()
            sticks = pygame.joystick.get_count()
            print('waiting for joystick...')
            time.sleep(1)
        self.joystick = pygame.joystick.Joystick(which_js)
        self.joystick.init()
        name = self.joystick.get_name()
        print("detected joystick device:", name)

        self.axis_states = [ 0.0 for i in range(self.joystick.get_numaxes())]
        self.button_states = [ 0 for i in range(self.joystick.get_numbuttons() + self.joystick.get_numhats() * 4)]
        self.axis_names = {}
        self.button_names = {}
        self.dead_zone = 0.0
        axes = self.joystick.get_numaxes()
        for i in range(axes):
            self.axis_names[i] = i
        buttons = self.joystick.get_numbuttons()
        hats = self.joystick.get_numhats()
        for i in range(buttons + hats * 4):
            self.button_names[i] = i
            
#         # test joystick 
#         for r in range(20):
#             pygame.event.pump()
#             print('r:', end='', flush=True)
#             for i in range(axes):
#                 val = self.joystick.get_axis(i)
#                 print(f'{val} ', end='', flush=True)
#             print()
#             time.sleep(.5)
#         print('********** joystick test complete')

#         pygame.event.pump()


    def poll(self):
        button = None
        button_state = None
        axis = None
        axis_val = None
        
#         self.joystick.init()
                 
        axes =  self.joystick.get_numaxes()
        for i in range(axes):
            val = self.joystick.get_axis( i )
#             if val != 0:
#                 print(f'{i}: {self.axis_states[i]} {val} ', end='\n', flush=True)
            if abs(val) < self.dead_zone:
                val = 0.0
            if self.axis_states[i] != val and i in self.axis_names:
                axis = self.axis_names[i]
                axis_val = val
                self.axis_states[i] = val
                break
        
        for i in range( self.joystick.get_numbuttons() ):
            state = self.joystick.get_button( i )
            if self.button_states[i] != state:
                if not i in self.button_names:
                    continue
                button = self.button_names[i]
                button_state = state
                self.button_states[i] = state
                break
        
        return button, button_state, axis, axis_val
        
    def set_deadzone(self, val):
        self.dead_zone = val

class JoyStickPub(object):
    '''
    Use Zero Message Queue (zmq) to publish the control messages from a local joystick
    '''
    def __init__(self, port = 5556, dev_fn='/dev/input/js1'):
        import zmq
        self.dev_fn = dev_fn
        self.js = PS3JoystickPC(self.dev_fn)
        self.js.init()
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind("tcp://*:%d" % port)


    def run(self):
        while True:
            button, button_state, axis, axis_val = self.js.poll()
            if axis is not None or button is not None:
                if button is None:
                    button  = "0"
                    button_state = 0
                if axis is None:
                    axis = "0"
                    axis_val = 0
                message_data = (button, button_state, axis, axis_val)
                self.socket.send_string( "%s %d %s %f" % message_data)
                print("SENT", message_data)

class JoyStickSub(object):
    '''
    Use Zero Message Queue (zmq) to subscribe to control messages from a remote joystick
    '''
    def __init__(self, ip, port = 5556):
        import zmq
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect("tcp://%s:%d" % (ip, port))
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')
        self.button = None
        self.button_state = 0
        self.axis = None
        self.axis_val = 0.0
        self.running = True


    def shutdown(self):
        self.running = False
        time.sleep(0.1)


    def update(self):
        while self.running:
            payload = self.socket.recv().decode("utf-8")
            #print("got", payload)
            button, button_state, axis, axis_val = payload.split(' ')
            self.button = button
            self.button_state = (int)(button_state)
            self.axis = axis
            self.axis_val = (float)(axis_val)
            if self.button == "0":
                self.button = None
            if self.axis == "0":
                self.axis = None


    def run_threaded(self):
        pass


    def poll(self):
        ret = (self.button, self.button_state, self.axis, self.axis_val)
        self.button = None
        self.axis = None
        return ret

class JoystickCreator(Joystick):
    '''
    A Helper class to create a new joystick mapping
    '''
    def __init__(self, *args, **kwargs):
        super(JoystickCreator, self).__init__(*args, **kwargs)

        self.axis_names = {}
        self.button_names = {}

    def poll(self):

        button, button_state, axis, axis_val = super(JoystickCreator, self).poll()

        return button, button_state, axis, axis_val

class JoystickCreatorController(JoystickController):
    '''
    A Controller object helps create a new controller object and mapping
    '''
    def __init__(self, *args, **kwargs):
        super(JoystickCreatorController, self).__init__(*args, **kwargs)


    def init_js(self):
        '''
        attempt to init joystick
        '''
        try:
            self.js = JoystickCreator(self.dev_fn)
            if not self.js.init():
                self.js = None
        except FileNotFoundError:
            print(self.dev_fn, "not found.")
            self.js = None

        return self.js is not None


    def init_trigger_maps(self):
        '''
        init set of mapping from buttons to function calls
        '''
        pass



