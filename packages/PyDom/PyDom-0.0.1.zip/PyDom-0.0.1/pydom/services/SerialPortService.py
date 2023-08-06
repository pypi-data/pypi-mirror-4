import serial, threading
import Queue
import time as t
from pydom.EventHook import EventHook
import logging

class SerialPortService:
    def __init__(self, port, baudrate):
        self.logger = logging.getLogger(__name__)
        self.writeQueue = Queue.Queue()
        self.onDataReceived = EventHook()
        self.serial = serial.serial_for_url(port, baudrate)
        self.logger.info('SerialPortService initialised.')

    def start(self):
        self.alive = True
        self._start_reader()
        self._start_writer()
        
    def enqueue(self, data):
        if type(data) is int:
            self.writeQueue.put(chr(data))
        else:
            self.writeQueue.put(data)
        
    def _start_reader(self):
        """Start reader thread"""
        self._reader_alive = True
        self.receiver_thread = threading.Thread(target=self.reader)
        self.receiver_thread.setDaemon(True)
        self.receiver_thread.start()
        
    def _start_writer(self):
        """Start writer thread"""
        self._writer_alive = True
        self.sender_thread = threading.Thread(target=self.writer)
        self.sender_thread.setDaemon(True)
        self.sender_thread.start()
        
    def reader(self):
        """loop and copy serial->console"""
        try:
            while self.alive and self._reader_alive:
                data = self.serial.read(1)
                for c in data:
                    self.logger.debug("in: %s ", c.encode('hex'))
                    self.onDataReceived.fire(c)
        except serial.SerialException:
            self.alive = False
            raise
    
    def writer(self):
        try:
            while self.alive and self._writer_alive:
                if not self.writeQueue.empty():
                    data = self.writeQueue.get()
                    self.logger.debug("out: %s ", data.encode("hex"))
                    self.serial.write(data)
                else:
                    t.sleep(0.01)
        except:
            self.alive = False
            raise
    
    def join(self, transmit_only=False):
        self.receiver_thread.join()