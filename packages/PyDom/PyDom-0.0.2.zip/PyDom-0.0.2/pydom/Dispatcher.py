from pydom.EventHook import EventHook

class Dispatcher(object):
    def __init__(self):
        self.onCommandReceived = EventHook()
        
    def enqueue(self, command):
        self.onCommandReceived.fire(command)