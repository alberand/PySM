#!/usr/bin/env python
# coding=utf-8

# System imports
import  threading
import  queue
from    time                import sleep
from    sys                 import exit

# PyQt5 imports
from    PyQt5.QtCore        import pyqtSignal
from    PyQt5.QtCore        import QObject

# PySerial imports
import  serial
from    serial.serialutil   import SerialException

class Model(threading.Thread, QObject):

    # This signal emitted when program fail to read serial port (self.port)
    error = pyqtSignal(object)

    def __init__(self):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        # Queue with data (lines) received from serial port
        self.queue      = queue.Queue()

        # Communications settings
        self.port       = '/dev/ttyACM0'
        self.br         = 9600
        self.timeout    = 0.01
        # Line ending id
        self.eol        = 0

        # PySerial object
        self.ser        = None
        # Flag for main cycle
        self.running    = True

        # TODO 
        # Configuration for line ending
        self.config     = {
                'eol':[
                    '',
                    '\n',
                    '\r',
                    '\r\n'
                ]
        }
        
    def run(self):
        '''
        Run thread.
        In every iteration trying to read one line from serial port and put
        it in queue.
        '''
        try:
            while self.running:
                data = None

                try:
                    data = self.readline()
                except SerialException:
                    print('Error occured while reading data.')

                if data:
                    self.queue.put(data.strip())

                sleep(self.timeout)

        except KeyboardInterrupt:
            exit()

    def stop(self):
        '''
        Stop thread.
        '''
        self.running = False

    def begin(self):
        '''
        Initializate PySerial object
        '''
        try:
            self.ser = serial.Serial(
                    self.port, self.br, timeout=3
            )
        except SerialException:
            print('Fail to open default port.')
            self.ser = serial.Serial(baudrate=self.br, timeout=3)

#==============================================================================
# Get, Set
#==============================================================================

    def get_queue(self):
        return self.queue

    def set_port(self, port):
        self.port = port
        try:
            self.ser.port = self.port
            self.ser.open()
        except SerialException:
            self.emit_error('Can\'t open this port: ' + str(port) + '.')

    def get_port(self):
        return self.port

    def set_br(self, baudrate):
        self.br = baudrate
        self.ser.baudrate = self.br

    def get_br(self):
        return self.br

    def set_eol(self, value):
        self.eol = value

    def get_eol(self):
        return self.config['eol'][self.eol]

#==============================================================================
# PySerial communication
#==============================================================================
    def readline(self):
        data = self.ser.readline(256)
        return data.decode('ASCII')

    def write(self, data):
        '''
        @data data to send
        '''
        self.ser.write(bytes(data, 'ASCII') + bytes(self.get_eol(), 'ASCII'))
        sleep(0.1)

#==============================================================================
# Signals
#==============================================================================

    def emit_error(self, value):
        self.error.emit(value)
