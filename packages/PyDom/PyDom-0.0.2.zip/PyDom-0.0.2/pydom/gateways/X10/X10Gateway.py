import re
from pydom.gateways.GatewayBase import GatewayBase
from pydom.devices.DeviceBase import DeviceBase

class X10Gateway(GatewayBase):
    def __init__(self, config):
        GatewayBase.__init__(self, config)
    
    def getHouseCode(self, devicecode):
        if (self.isX10Code(devicecode)):
            return devicecode[0:1]
        raise ValueError("Could not determine the house code")
     
    def getDeviceAddress(self, devicecode):
        if (self.isX10Code(devicecode)):
            return int(devicecode[1:])
        raise ValueError("Could not determine the device address")
        
    def isX10Code(self, code):
        pattern = re.compile("[A-P][1]{0,1}[1-9]{1}")
        if (pattern.match(code)):
            if int(code[1:]) <= 16 and int(code[1:]) > 0:
                return True
        else:
            return False
    
    def splitCommandToHouseCodes(self, command):
        groupedList = {}
        for id in command.getDevices():
            device = self.getDeviceByName(id)
            if device == None:
                device = self.getDeviceByAddress(id)
            if device == None:
                # The device does not exist in configuration, just create one
                device = DeviceBase(id, id, None)
                
            hc = self.getHouseCode(device.address)
            if not groupedList.has_key(hc):
                groupedList[hc] = []
            groupedList[hc].append(self.getDeviceAddress(device.address))
        return groupedList
                