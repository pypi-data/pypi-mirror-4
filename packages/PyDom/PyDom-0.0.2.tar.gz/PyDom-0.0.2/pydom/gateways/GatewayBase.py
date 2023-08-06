from pydom.EventHook import EventHook
from pydom.Command import Command
from pydom.devices import DeviceFactory
import logging
import inject

class GatewayBase(object):
    @inject.param('dispatcher')    
    def __init__(self, config, dispatcher):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.dispatcher = dispatcher
        self.dispatcher.onCommandReceived += self.parseCommand
        self.onStatusChanged = EventHook()
        self.checkDevices = True
        try:
            self.checkDevices = config['checkDevices']
        except KeyError:
            self.logger.warning('No checkDevices set for {0}.'.format(self.__class__.__name__))
        except ValueError:
            self.logger.error('checkDevices setting of {0} is invalid.'.format(self.__class__.__name__))
            
        self.devices = {}        
        try:
            for deviceConfigDict in config['devices']:
                self.devices[deviceConfigDict['name']] = DeviceFactory.createDevice(deviceConfigDict)
        except KeyError:
            self.logger.warning('No devices configured for {0}.'.format(self.__class__.__name__))
        self.devices.keys()
    
    def setCheckDevices(self, b):
        if isinstance(b, bool):
            self.checkDevices = b
        else:
            raise ValueError('"{0}" not a boolean'.format(b)) 
    
    def getDevices(self):
        return self.devices

    def setStateByName(self, deviceName, state):
        device = self.getDeviceByName(deviceName)
        if not device == None:
            device.state = state
            self.onStatusChanged.fire(self.__class__.__name__, device.name)
    
    def setStateByAddress(self, address, state):
        device = self.getDeviceByAddress(address)
        if not device == None:
            device.state = state
            self.onStatusChanged.fire(self.__class__.__name__, device.name)
                
    def getDeviceByName(self, deviceName):
        if self.devices.has_key(deviceName):
            return self.devices[deviceName]
        return None

    def getDeviceByAddress(self, address):
        for deviceName in self.devices:
            device = self.devices[deviceName]
            if device.address == address:
                return self.devices[device.name]
        return None

    def parseCommand(self, command):
        if (isinstance(command, Command)):
            if self.checkDevices:
                newDeviceList = []
                for deviceString in command.getDevices():
                    device = self.getDeviceByName(deviceString)
                    if device == None:
                        device = self.getDeviceByAddress(deviceString)
                    if device == None:
                        self.logger.warning("Unknown device '{0}', ignoring".format(deviceString))
                    else:
                        newDeviceList.append(device.name)
                if len(newDeviceList) > 0:
                    self.enqueueCommand(Command(newDeviceList, command.getAction()))
            else:
                self.enqueueCommand(command)
        else:
            self.logger.error("Command '" + command + "' not enqueued. Not an instance of Command.")
            raise ValueError("Command '" + command + "' not enqueued. Not an instance of Command.")

    def start(self):
        raise NotImplementedError('The subclass {0} should implement a start method.'.format(self.__class__.__name__))

    def stop(self):
        raise NotImplementedError('The subclass {0} should implement a stop method.'.format(self.__class__.__name__))

    def enqueueCommand(self, command):
        raise NotImplementedError('The subclass {0} should implement a enqueueCommand method.'.format(self.__class__.__name__))