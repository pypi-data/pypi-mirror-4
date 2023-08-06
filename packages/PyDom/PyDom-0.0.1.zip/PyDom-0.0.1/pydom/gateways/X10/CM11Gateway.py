import serial, threading
from threading import Timer
from pydom.services.SerialPortService import SerialPortService
from pydom.Command import Action
from pydom.gateways.X10.X10Gateway import X10Gateway
from pydom.gateways.GatewayBase import GatewayBase
import Queue
import logging
from fluidity import StateMachine, state, transition

from pydom.util import enum

BAUDRATE = 4800

MAX_TRIES = 3

HOUSECODE_A = 0x06
HOUSECODE_B = 0x0E
HOUSECODE_C = 0x02
HOUSECODE_D = 0x0A
HOUSECODE_E = 0x01
HOUSECODE_F = 0x09
HOUSECODE_G = 0x05
HOUSECODE_H = 0x0D
HOUSECODE_I = 0x07
HOUSECODE_J = 0x0F
HOUSECODE_K = 0x03
HOUSECODE_L = 0x0B
HOUSECODE_M = 0x00
HOUSECODE_N = 0x08
HOUSECODE_O = 0x04
HOUSECODE_P = 0x0C
HOUSECODES = {"A": 0x06, "B": 0x0E, "C": 0x02, "D": 0x0A, "E": 0x01, "F": 0x09, "G": 0x05, "H": 0x0D, "I": 0x07, "J": 0x0F, "K": 0x03, "L": 0x0B, "M": 0x00, "N": 0x08, "O": 0x04, "P": 0x0C}

DEVICECODE_1 = 0x06
DEVICECODE_2 = 0x0E
DEVICECODE_3 = 0x02
DEVICECODE_4 = 0x0A
DEVICECODE_5 = 0x01
DEVICECODE_6 = 0x09
DEVICECODE_7 = 0x05
DEVICECODE_8 = 0x0D
DEVICECODE_9 = 0x07
DEVICECODE_10 = 0x0F
DEVICECODE_11 = 0x03
DEVICECODE_12 = 0x0B
DEVICECODE_13 = 0x00
DEVICECODE_14 = 0x08
DEVICECODE_15 = 0x04
DEVICECODE_16 = 0x0C

ALL_UNITS_OFF = 0x00
ALL_LIGHTS_ON = 0x01
ON = 0x02
OFF = 0x03
DIM = 0x04
BRIGHT = 0x05
ALL_LIGHTS_OFF = 0x06
EXTENDED_CODE = 0x07
HAIL_REQUEST = 0x08
HAIL_ACK = 0x09
PRESET_DIM_1 = 0x0A
PRESET_DIM_2 = 0x0B
EXTENDED_DATA_TRASNFER = 0x0C
STATUS_ON = 0x0D
STATUS_OFF = 0x0E
STATUS_REQUEST = 0x0F

BIT_2 = 0x04
FUNCTION = 0x02
EXTENDED_TRANSMISSION = 0x01

ACKOWNLEDGE = 0x00
INTERFACE_READY_TO_RECEIVE = 0x55

POWER_FAIL_POLL_SIGNAL = 0xa5
TIMER_DOWNLOAD_HEADER = 0x9b
INTERFACE_POLL_SIGNAL = 0x5a
RESPONSE_TO_POLL_SIGNAL = 0xc3
STATUS_REQUEST = 0x8b

State = enum(STOPPED = 'stopped',
             READY = 'ready',
             WAITING_FOR_CHECKSUM = 'waiting_for_checksum',
             WAITING_FOR_IF_READY = 'waiting_for_if_ready')

class CM11Gateway(X10Gateway, GatewayBase, StateMachine):
    logger = logging.getLogger(__name__)
    
    initial_state = State.STOPPED

    state(State.STOPPED, enter='logState')
    state(State.READY, enter='logState')
    state(State.WAITING_FOR_CHECKSUM, enter=['logState', 'startChecksumTimer'], exit='stopChecksumTimer')
    state(State.WAITING_FOR_IF_READY, enter='logState', exit='clearData')

    transition(from_=State.STOPPED, event='start', to=State.READY, action='startController')
    transition(from_=State.READY, event='sendTrigger', to=State.WAITING_FOR_CHECKSUM, action='sendData')
    transition(from_=State.WAITING_FOR_CHECKSUM, event='resendTrigger', to=State.WAITING_FOR_CHECKSUM, action='resendData')  
    transition(from_=State.WAITING_FOR_CHECKSUM, event='checksumOkTrigger', to=State.WAITING_FOR_IF_READY, action='acknowledge')
    transition(from_=State.WAITING_FOR_IF_READY, event='interfaceReadyTrigger', to=State.READY)    
    transition(from_=[State.WAITING_FOR_CHECKSUM, State.WAITING_FOR_IF_READY, State.READY], event='stop', to=State.STOPPED)
    transition(from_=State.WAITING_FOR_CHECKSUM, event='abortTrigger', to=State.WAITING_FOR_IF_READY, action='acknowledge')
    transition(from_=State.WAITING_FOR_CHECKSUM, event='atimeoutTrigger', to=State.READY, action='sendStatusRequest')
    
    def __init__(self, config, serialPortService=None):
        StateMachine.__init__(self)
        X10Gateway.__init__(self, config)
        try:
            self.port = config['port']
#            int(self.port)
        except KeyError:
            raise ValueError('Port not configured.')
#        except ValueError:
#            raise ValueError('Port %s is not a number.' % self.port)

        self.serialPortService = None
        if serialPortService != None: # expected to be filled only during unit tests
            self.serialPortService = serialPortService

        self.commandQueue = Queue.Queue()
        self.CM11OutQueue = Queue.Queue()
        self.clearData()
        self.checksumTimerThread = None
        self.logger.info('CM11Gateway initialised.')

    def logState(self):
        self.logger.debug('New state active: %s', self.current_state)
        
    def clearData(self):
        self.logger.debug('Clearing checksum.')
        self.expected_checksum = None
        self.dataToSend = None
        self.retries = 0

    def handle_data(self, data):
        data = ord(data)
        
        if self.current_state == State.WAITING_FOR_CHECKSUM:
            self.logger.debug("Checksum expected: " + chr(self.expected_checksum).encode('hex'))
            if data != self.expected_checksum:
                self.logger.error('Checksum error! expected %s but got %s', chr(self.expected_checksum).encode('hex'), chr(data).encode('hex'))
                self.resendTrigger()
            else:
                self.checksumOkTrigger()
        elif self.current_state == State.WAITING_FOR_IF_READY and data == INTERFACE_READY_TO_RECEIVE:
            self.logger.debug('Interface ready signal received')
            self.interfaceReadyTrigger()
        elif data == POWER_FAIL_POLL_SIGNAL:
            self.logger.info('Time request received, responding accordingly')
            body = []
            body.append(0x02)
            body.append(0x05)
            body.append(0x0b)
            body.append(0x59)
            body.append(0x84)
            body.append(0x60)
          
            self.serialPortService.enqueue(TIMER_DOWNLOAD_HEADER)
            self.sendTrigger(body)
        elif data == INTERFACE_POLL_SIGNAL:
            self.logger.info('Interface poll signal received')
            self.serialPortService.enqueue(RESPONSE_TO_POLL_SIGNAL)
           
    def enqueueCommand(self, command):
        self.commandQueue.put(command)

    def startController(self):
        continueStart = True
        
        if self.serialPortService == None: # expected not to be None only during unit tests
            try:
                self.serialPortService = SerialPortService(self.port, BAUDRATE)
            except serial.serialutil.SerialException, se:
                self.logger.error(se)
                self.stop()
                continueStart = False
        
        if continueStart:
            self.connect()
            self.sendStatusRequest()
            self.alive = True
            self.thread = threading.Thread(target=self.run)
            self.thread.setDaemon(True)
            self.thread.start()
            self.logger.info('Controller started');
        
    def connect(self):
        self.logger.info('Connecting to CM11 module')
        try:
            self.serialPortService.onDataReceived += self.handle_data
            self.serialPortService.start()
        except serial.SerialException:
            self.logger.exception('Could not open port')
            self.stop()
    
    def run(self):
        self.logger.info(' Running')
        while self.alive:
            if self.current_state == State.READY:
                # if there is data to be sent to the controller, send it
                if not self.CM11OutQueue.empty():
                    self.sendTrigger(self.CM11OutQueue.get())
            # Always process new commands
            if not self.commandQueue.empty():
                command = self.commandQueue.get()
                groupedCodes = self.splitCommandToHouseCodes(command)
                for hc in groupedCodes:
                    for device in groupedCodes[hc]:
                        houseCode = eval('HOUSECODE_' + str(hc))
                        deviceCode = eval('DEVICECODE_' + str(device))
                                
                        headerByte = BIT_2
                        addressByte = (houseCode << 4) | deviceCode
                        self.CM11OutQueue.put([headerByte, addressByte])                        
                    
                        """ Since is to some more work to actually check if the device(s)
                        switched state we'll just assume everything went ok..."""
                        self.setStateByAddress(str(hc)+str(device), command.getAction())
                    
                    headerByte = BIT_2 | FUNCTION
                    if (command.getAction() == Action.ON):
                        functionByte = (houseCode << 4) | ON
                    else:
                        functionByte = (houseCode << 4) | OFF
                    self.CM11OutQueue.put([headerByte, functionByte])
        
    def sendStatusRequest(self):
        self.serialPortService.enqueue(STATUS_REQUEST)
        
    def sendData(self, data):
        self.dataToSend = data
        self.sendWithChecksum(self.dataToSend)
        #time.sleep(0.3)

    def resendData(self):
        self.retries += 1
        self.stopChecksumTimer()
        if self.retries < MAX_TRIES:
            self.logger.info('Retrying send %s retries left', MAX_TRIES - self.retries)
            self.sendWithChecksum(self.dataToSend)
        else:
            self.logger.error('Max send retries exceeded, aborting')
            self.abortTrigger()

    def startChecksumTimer(self):
        self.checksumTimerThread = Timer(2.0, self.checkChecksumTimedOut)
        self.checksumTimerThread.start()
        
    def stopChecksumTimer(self):
        if self.checksumTimerThread != None:
            self.logger.debug('Checksum timer stopped')
            self.checksumTimerThread.cancel()

    def checkChecksumTimedOut(self):
        self.logger.error('Checksum not received in time')
        self.resendData()

    def sendWithChecksum(self, data):
        checksumSet = set()
        for i in data:
            self.serialPortService.enqueue(i)
            checksumSet.add(i)
        self.expected_checksum = self.checksum(checksumSet)

    def acknowledge(self):
        self.serialPortService.enqueue(ACKOWNLEDGE)
                     
    def stop(self):
        self.dispatcher.onCommandReceived -= self.enqueueCommand
        self.alive = False
        
    def checksum(self, data):
        return sum(data) & 0x0000ff