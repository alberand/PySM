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

from config import config

class Model(threading.Thread, QObject):

    # This signal emitted when program fail to read serial port (self.port)
    error = pyqtSignal(object)

    def __init__(self):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        # Queue with data (lines) received from serial port
        self.queue      = queue.Queue()
        self.paused = threading.Event()
        self.paused.set()

        # Communications settings
        self.port       = config['port']
        self.br         = config['baudrate']
        self.timeout    = config['timeout']
        # Line ending id
        self.eol        = config['eol'][0]

        # PySerial object
        self.ser        = None
        # Flag for main cycle
        self.running    = True

    def run(self):
        '''
        Run thread.
        In every iteration trying to read one line from serial port and put
        it in queue.
        '''
        try:
            while self.running:
                self.paused.wait()
                if not self.ser.isOpen():
                    sleep(0.05)
                    continue

                try:
                    data = self.readline()
                except SerialException as e:
                    print('Error occured while reading data. ' + str(e))
                    continue

                if data:
                    self.queue.put(data.strip())

        except KeyboardInterrupt:
            if self.ser:
                self.ser.close()
            exit()

    def pause(self):
        self.ser.close()
        self.paused.clear()

    def resume(self):
        self.ser.open()
        self.paused.set()

    def stop(self):
        '''
        Stop thread.
        '''
        self.running = False
        self.paused.set()
        if self.ser:
            self.ser.close()

    def begin(self):
        '''
        Initializate PySerial object
        '''
        try:
            self.ser = serial.Serial(
                    self.port, self.br, timeout=self.timeout
            )
        except SerialException:
            print('Fail to open default port.')
            self.ser = serial.Serial(
                    baudrate=self.br, timeout=self.tiemout)

#==============================================================================
# Get, Set
#==============================================================================

    def get_queue(self):
        return self.queue

    def set_port(self, port):
        if self.port != port:
            self.port = port
        else:
            return

        # self.begin()
        try:
            self.ser.port = port
            self.ser.open()
        except SerialException as e:
            self.emit_error('Can\'t open this port: ' + str(port) + '.')
            print(e)
            self.ser.close()

    def get_port(self):
        return self.port

    def set_br(self, baudrate):
        self.ser.reset_input_buffer()
        if int(baudrate) in serial.Serial.BAUDRATES:
            self.br = baudrate
            self.ser.baudrate = baudrate

    def get_br(self):
        return self.br

    def set_eol(self, index):
        if index < len(config['eol']) and index >= 0:
            self.eol = config['eol'][index]
        else:
            print('Can\t set up this type of End Of Line. Because it\'s not in'
                  'standart list.')

    def get_eol(self):
        return self.eol

#==============================================================================
# PySerial communication
#==============================================================================
    def read(self, size=1):
        '''
        Read bytes from port. 
        Args:
            size: integer specify number of bytes to read. Default is 1.
        Returns:
            String
        '''
        data = None

        try:
            if self.ser.isOpen():
                try:
                    data = self.ser.read(size)
                except TypeError:
                    print('Strange bug in the library.')
            else:
                print('Can\'t read from the port. Port isn\'t open.')
        except SerialException as e:
            print('Exception occured, while reading from serial port. ' 
                    + str(e))

        return data

    def readline(self):
        '''
        Read line from serial port. Read byte by byte until program get '\n'
        symbol.
        Returns:
            String
        '''
        data = b''

        try:
            if self.ser.isOpen():
                sym = self.read()
                while sym != b'\n' and sym and len(data) < 256:
                    data += sym
                    sym = self.read()
            else:
                print('Can\'t read from the port. Port isn\'t open.')

        except SerialException as e:
            print('Exception occured, while reading line from serial port.')

        # return data.decode('UTF-8')
        # return data.decode('ASCII')
        return data

    def write(self, data):
        '''
        Write data to serial port.
        Args:
            data: data to send
        '''
        try:
            if self.ser.isOpen():
                self.ser.write(
                        bytes(data, 'ASCII') + 
                        bytes(self.get_eol(), 'ASCII')
                )
            else:
                print('Can\'t write to the port. Port isn\'t open.')
        except SerialExceptin as e:
            print('Exception occured, while writing to serial port.')
            print(e)

#==============================================================================
# Signals
#==============================================================================

    def emit_error(self, value):
        self.error.emit(value)
