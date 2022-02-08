#!/usr/bin/env python3
"""
Assemble and drive a donkeycar.
Parts are specified in parts.yml in the order they need to execute.

Usage:
    driver.py  [--myconfig=<filename>]

Options:
    -h --help               Show this screen.
    --myconfig=filename     Specify myconfig file to use. 
                            [default: myconfig.py]
"""
import os
import time
import logging
import importlib
from docopt import docopt
import donkeycar as dk
import yaml


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


#__________________________________ ASSEMBLE THE VEHICLE________________________

def assemble(cfg):
    #Initialize car
    V = dk.vehicle.Vehicle()

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
        part_class = getattr(module, class_name)
        part = part_class(cfg)
        logger.info(f'    {class_name} part created')
        
        #add part to vehicle
        V.add(part, inputs=part.inputs, outputs=part.outputs, threaded=part.threaded, run_condition=part.run_condition)
        logger.info(f'    {class_name} part added to vehicle')
        logger.info(f'    Inputs  {part.inputs}')
        logger.info(f'    Outputs {part.outputs}')
           
    return V

#__________________________________ MAIN _________________________________________
if __name__ == '__main__':
    # load and check command line options
    args = docopt(__doc__)

    # assemble vehicle with configuration parameters
    configuration = dk.load_config(myconfig=args['--myconfig'])
    logger.info('\nAssembling vehicle from parts...')
    vehicle = assemble(configuration)

    # start the vehicle
    logger.info('Start your engines...')
    vehicle.start(rate_hz=configuration.DRIVE_LOOP_HZ, max_loop_count=configuration.MAX_LOOPS)

    logger.info('Vehicle end.\n')
    
    

