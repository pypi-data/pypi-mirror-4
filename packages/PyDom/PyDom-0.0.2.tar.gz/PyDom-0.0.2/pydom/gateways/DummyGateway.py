from pydom.gateways.GatewayBase import GatewayBase

class DummyGateway(GatewayBase):
    def __init__(self, config):
        GatewayBase.__init__(self, config)

    def start(self):
        self.logger.info('DummyGateway stared.')

    def stop(self):
        self.logger.info('DummyGateway stopped.')

    def enqueueCommand(self, command):
        for deviceString in command.getDevices():
            if deviceString in self.devices:
                self.setStateByName(deviceString, command.getAction())
            else:
                for device in self.devices:
                    if device.address == deviceString:
                        self.setStateByAddress(deviceString, command.getAction())
                    else:
                        self.setStateByAddress(device, command.getAction())