from DeviceBase import DeviceBase

class Lamp(DeviceBase):
    def __init__(self, name, address, group):
        DeviceBase.__init__(self, name, address, group)