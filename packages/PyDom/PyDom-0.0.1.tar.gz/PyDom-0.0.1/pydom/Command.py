from pydom.util import enum

Action = enum(ON = "on", OFF = "off")

class Command(object):
    def __init__(self, devices, action):
        if isinstance(devices, list):
            pass
        else:
            raise ValueError('Given value for devices is not a list') 
        if isinstance(action, str) or isinstance(action, unicode):
            if action.lower() == 'on':
                self.action = Action.ON
            elif action.lower() == 'off':
                self.action = Action.OFF
            else:
                raise ValueError("Given action is not %s is not 'on' or 'off'", action)
        elif isinstance(action, str):
            pass
        else:
            raise ValueError('Given action is not a string or Action') 
        self.devices = devices
        self.action = action
    
    def getDevices(self):
        return self.devices
    
    def getAction(self):
        return self.action
    
    def __str__(self):
        return str(self.devices) + ' ' + self.action