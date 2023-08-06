import logging
import inject
from pydom.EventHook import EventHook

class DeviceManager(object):
    @inject.param('gateways')
    def __init__(self, gateways):
        self.logger = logging.getLogger(__name__)
        self.gateways = gateways
        self.devices = {}
        for gw in self.gateways:
            gw.onStatusChanged += self.deviceUpdated
            devices = gw.getDevices()
            for name in devices:
                self.devices[name] = devices[name]
        self.onDeviceUpdated = EventHook()

    def deviceUpdated(self, gatewayName, deviceName):
        self.logger.info('Status of device %s under %s changed', deviceName, gatewayName)
        self.onDeviceUpdated.fire(deviceName)