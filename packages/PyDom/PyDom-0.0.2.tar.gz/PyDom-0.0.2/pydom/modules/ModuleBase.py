import logging
import inject

class ModuleBase(object):
    @inject.param('devManager')    
    def __init__(self, config, devManager):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.deviceManager = devManager
        self.deviceManager.onDeviceUpdated += self.onDeviceUpdated
        
    def onDeviceUpdated(self, deviceName):
        self.logger.debug('Status of device {0} changed'.format(deviceName))