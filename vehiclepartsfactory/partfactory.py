#!/usr/bin/env python3
"""
Base classes to create vehicle parts
Simple factory implementation where we are using a metaclass to register
creation functions of classes derived from a base class Creatable.
"""



import time
from threading import Thread
from threading import Lock

class PartFactory(type):
    """
    Metaclass to hold the registration dictionary of the constructor functions
    """
    register = {}
    def __init__(cls, name, bases, d):
        cls.register[cls.__name__] = cls.create

    @classmethod
    def make(mcs, concrete, kwargs):
        return mcs.register[concrete](kwargs)


class Part(object, metaclass=PartFactory):
    """ 
    Base class for factory creatable objects, implementing create()
    Part base class, provides asynchronous threads with individual loop
        frequencies """

    @classmethod
    def create(cls, kwargs):
        return cls(**kwargs)

    def __init__(self, loop_time):
        self.data_bus = None
        self.loop_time = loop_time
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True
        self.lock = Lock()
        self.on = False
        self.last_time = time.time()
        self.loop_count = 0
        self.time_diff_total = 0.
        print('Created part', type(self).__name__, 'with loop time', self.loop_time)
        self.run_part = False

    def update(self):
        """ Only needs to be implemented here """
        assert self.data_bus, "Need to set data bus first"
        self.on = True
        while self.on:

            # lock share resource
            with self.lock:
                self.read_from_bus()
            if self.run_part:
                self.operate()
                # lock shared resource
                with self.lock:
                    self.write_to_bus()
#                     print(f'{self.__class__.__name__}: ', end ='')
#                     self.data_bus.dump()
                        
            now = time.time()
            time_diff = now - self.last_time
            # mechanically delay loop to match expected loop time - this is
            # not exact but approximate
            if time_diff < self.loop_time:
                time.sleep(self.loop_time - time_diff)
            now = time.time()
            self.time_diff_total += now - self.last_time
            self.last_time = now
            self.loop_count += 1

    def read_from_bus(self):
        pass

    def write_to_bus(self):
        pass
        
    def operate(self):
        pass
    
    def mainthread(self):
        # process that is called by vehicle main ; where statements need to be executed outside of thread
        pass

    def start(self):
#         print (f'{self.__class__.__name__} starting...')        
        self.t.start()

    def set_data_bus(self, data_bus):
        self.data_bus = data_bus

    def stop(self):
        self.on = False
        # just check how exact the timing was
        print('Stopped part', type(self).__name__, 'with avg loop time',
              self.time_diff_total / self.loop_count)


