"""
Assemble and drive a donkeycar.
Parts are specified in parts.yml in the order they need to execute.

Usage:
    donkeycar.py  [--myconfig=<filename>]

Options:
    -h --help               Show this screen.
    --myconfig=filename     Specify myconfig file to use. 
                            [default: myconfig.py]
"""

import math
import time
import collections
import yaml
import logging
import importlib
from docopt import docopt
import donkeycar as dk
import donkeycar.vehiclepartsfactory.partfactory as factory

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Not really needed, but a structure to combine data, its type and a timestamp
DataStruct = collections.namedtuple('DataStruct', 'data_type data time_stamp')

class DataBus:
    """ Single object in the car that shares all data between parts"""
    def __init__(self):
        self.data_store = {}

    def write(self, data_name, data_type, data):
        if data is not None:
            """ Write data into the bus"""
            d = DataStruct(data_type=data_type, data=data, time_stamp=time.time())

            # here we check types but could check more like types don't change, etc
            assert type(data) is data_type, f'{type(data).__name__} does not ' \
                                            f'match {data_type.__name__}'

            # we just replace data, don't keep history, but we could also keep
            # the last n entries and tag it with an additional counter which gets
            # cycled
            self.data_store[data_name] = d

    def read(self, data_name):
        """ Return current data entry, return None when nothing found but don't throw """
        d = self.data_store.get(data_name)
        if d is not None:
            return d.data
        else:
            return None

    def readlist(self, data_names):
        """ Return list of data entries, return None when nothing found but don't throw """
        datalist = []
        for i in range(len(data_names)):
            d = self.data_store.get(data_names[i])
#             if data_names[i] != 'cam/image_array':
#                 print (f'{data_names[i]}:{d}')
            if d is None:
                datalist = None
                break
            else:
                datalist.append(d.data)
        return datalist
    
    def dump(self):
        """ Print out the DataBus """
        for k, d in self.data_store.items():  
            print(f'{k}:{d.data} ', end = '')
        print()

class Vehicle:
    def __init__(self, cfg):
        self.parts = []
        # the vehicle owns the data bus
        self.data_bus = DataBus()
        self.assemble_parts(cfg)

    def add_part(self, part):
        # here we set the bus into the part, no need for the child classed to
        # do that
        part.set_data_bus(self.data_bus)
        self.parts.append(part)

    def start(self):
        for part in self.parts:
            part.start()
        try:
            while True:
                time.sleep(.2)
                for part in self.parts:
                    part.mainthread()
                pass
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)
        finally:
            print(f'Stopped car.')
            self.stop()

    def stop(self):
        for part in self.parts:
            part.stop()
    
    def assemble_parts(self, cfg):
        # Load the YAML file specifying the parts
        with open(cfg.PARTS_PATH) as file:
            try:
                dict = yaml.safe_load(file)
            except yaml.YAMLError as exception:
                logger.error(exception)
    
        parts = dict.get("parts")
        if parts is None:
            logger.error("parts.yml is missing the parts key")
            raise Exception()
        
        for mod_name, class_name in parts.items():
            #import module <mod_name>
            module = importlib.import_module(mod_name)
            logger.info(f'{module.__name__} imported.')
        
            #create part object from <class_name>
#             part_class = getattr(module, class_name)
            part = factory.PartFactory.make(class_name, {'cfg': cfg})
#             part = part_class(cfg)
            logger.info(f'    {class_name} part created')
        
            #add part to vehicle
            self.add_part(part)
            logger.info(f'    {class_name} part added to vehicle')

 
#__________________________________ MAIN _________________________________________
if __name__ == '__main__':
    # load and check command line options
    args = docopt(__doc__)

    # assemble vehicle with configuration parameters
    configuration = dk.load_config(myconfig=args['--myconfig'])
    logger.info('Assembling vehicle from parts...')

    car = Vehicle(configuration)

    # start the vehicle
    logger.info('Start your engines...')
    car.start()

    logger.info('Vehicle end.\n')
