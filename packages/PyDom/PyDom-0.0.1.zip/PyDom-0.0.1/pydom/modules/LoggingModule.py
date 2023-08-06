from pydom.modules.ModuleBase import ModuleBase


class LoggingModule(ModuleBase):
    def __init__(self, config):
        ModuleBase.__init__(self, config)
   
    def onDeviceUpdated(self, deviceName):       
        self.logger.info('Status of device %s changed', deviceName)
