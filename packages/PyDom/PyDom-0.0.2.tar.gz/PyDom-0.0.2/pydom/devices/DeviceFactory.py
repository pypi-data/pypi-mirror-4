import logging

from Lamp import Lamp
from DeviceBase import DeviceBase

def createDevice(deviceConfigDict):
    device = None
    if deviceConfigDict['type'] == 'Lamp':
        device = Lamp(deviceConfigDict['name'], deviceConfigDict['address'], deviceConfigDict['group'])
    else:
        logging.getLogger(__name__).debug("Device type '{0}' not supported, returning basic device type.")
        device = DeviceBase(deviceConfigDict['name'], deviceConfigDict['address'], deviceConfigDict['group'])
        
    return device