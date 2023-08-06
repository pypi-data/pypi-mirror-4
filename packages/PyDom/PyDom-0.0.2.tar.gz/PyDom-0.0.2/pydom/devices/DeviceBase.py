from pydom.util import enum

State = enum(ON = "on", OFF = "off")

class DeviceBase(object):
    def __init__(self, name, address, group):
        self.name = name
        self.address = address
        self.group = group
        self.state = State.OFF
        
    def __eq__(self,other):
        if other == None:
            return False
        return self.name == other.name and self.address == other.address and self.group == other.group and self.state == other.state