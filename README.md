# dkyaml
 Demo new way to implement DonkeyCar parts
# Dynamic DonkeyCar parts

This repository was developed to be a demonstration of a new way to implement DonkeyCar parts. Note that this is for demonstration purposes only and not a full implementation of DonkeyCar parts.

The current implementation of DonkeyCar uses a very large and complex template manage.py to assemble parts. The python script uses the config.py and many ‘if statements’ to decide which parts are included into the vehicle.   To add a new part, the developer must dig into this complex and add the new part with appropiate if statements.

# Proposed alternative: YAML part configuration
Since parts have a standard structure, a YAML file can be used to identify to identify which parts to include. If the YAML file contains every part,  a comment symbol # can be used to prevent the inclusion of the part.

Instantiating a part requires two sets of parameters. 1) Class Parameters are sent to the Class to configure the object.   2) Vehicle run parameters are used to control inputs, outputs, threading and the run condition.

Class Parameters: Since the values of these are typically setup in the config/myconfig files, I propose that the Class definition of parts be simplified to accept one parameter: cfg which holds all of the configuration parameters.

Vehicle Parameters: I would argue that these are really Part Parameters and should be set by the Part itself.

# Two Implementations Prototyped
Changing the architecture of vehicle/part scheme will require significant modifications to the code repository.  Therefore, I prototyped two methods where method 1 is an effort to keep compatibility with the existing Vehicle/Manage architecture while also supporting the new architecture.   Method 2 implements a new vehicle.py and parts are modified without regard to compatibility. 


Method 1 driver.py  {parts in vehicleparts folder}
This script replaces manage.py.  The parts list is read from parts.yml.  The module importlib is used to dynamically import the modules and then create part objects.  Each part has been updated to contain only one parameter: ‘cfg’.   The config/myconfig file is updated with any missing necessary part parameters. Each part also contains new parameters to define inputs, outputs, threading and run_condition.  After each part is created, it is added to the standard DonkeyCar vehicle.py.

python driver.py --myconfig myconfig-one.py

Method2 vehicle.py {parts in vehiclepartsfactory folder}
Note: This implementation was derived from the gists described by DocGarbanzo at https://gist.github.com/DocGarbanzo.
This script replaces the existing vehicle.py.  This module contains a simple message database that replaces memory.py and a simplified vehicle class.   This implementation requires all parts to be threaded.   The partfactory.py file defines a base class for each part.  The performance code from the original vehicle.py has been moved here.   Most importantly it contains a Factory class to build new parts dynamically.

python vehicle.py --myconfig myconfig-two.py

# Parts
Two versions of the following parts were implemented and specified in parts.yml
1. PyGamePS4JoystickController  - uses jscontroller.py.  This was customized to use PyGame and tested on MacOS only.
2. PilotCondition - from manage.py
3. AI_Pilot (keras)
4. AiLaunch
5. DriveMode - from manage.py
6. DonkeyGymEnv
7. TubWriter
8. Dashboard - custom part to print angle, throttle
