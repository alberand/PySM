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
    # Signal emitted when port configuratin changes
    port_conf_change = pyqtSignal(object)

    def __init__(self):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        # Queue with data (lines) received from serial port
        self.queue      = queue.Queue()
        self.paused = threading.Event()
        self.paused.set()

        # Communications settings
        self._port      = config['port']
        self._br        = config['baudrate']
        self._parity    = config['parity']
        self._bytesize  = config['bytesize']
        self._stopbits  = config['stopbits']
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

                    if config['in_hex']:
                        # Only for Python 3.5 and newer
                        decoded = data.hex().upper()
                    else:
                        if config['encode'].upper() in ['ASCII', 'UTF-8']:
                            try:
                                decoded = data.decode(config['encode'])
                            except UnicodeError as e:
                                print('Fail to decode bytes. Error: {}'.format(
                                    e))
                        else:
                            print('Wrong decoding format. Using ASCII.')
                            decoded = data.decode('ASCII')

                    # One not formated and formated string for hex
                    # representation
                    hex_repr = self.add_html_colors(decoded)
                    # print(hex_repr)
                    result = [decoded, hex_repr]

                    self.queue.put(result)

        except KeyboardInterrupt:
            if self.ser:
                self.ser.close()
            exit()

    def pause(self):
        self.ser.close()
        if self.paused.isSet():
            self.paused.clear()

    def resume(self):
        self.ser.open()
        if not self.paused.isSet():
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
                    port=self._port, baudrate=self._br, timeout=self.timeout,
                    bytesize=self._bytesize, stopbits=self._stopbits
            )
        except SerialException:
            print('Fail to open default port.')
            self.ser = serial.Serial(
                    baudrate=self._br, timeout=self.timeout)

#==============================================================================
# Attributes
#==============================================================================

    @property
    def br(self):
        return self._br

    @br.setter
    def br(self, baudrate):
        self.ser.reset_input_buffer()
        if int(baudrate) in serial.Serial.BAUDRATES:
            self._br = baudrate
            self.ser.baudrate = baudrate

        self.emit_port_conf_change(self.port_config())

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, port):
        if self.ser and self.ser.isOpen():
            self.ser.close()

        if self._port != port:
            self._port = port
        else:
            return

        try:
            self.ser.port = port
            self.resume()
        except SerialException as e:
            self.emit_error('Can\'t open this port: ' + str(port) + '.')
            print(e)
            self.ser.close()

        self.emit_port_conf_change(self.port_config())

    def get_queue(self):
        return self.queue

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
# Utils
#==============================================================================
    
    def add_html_colors(self, string):
        '''
        Use predifiend dictionary to find regex at the string and add color HTML
        tags to them.
        Args:
            string: String to parse
        Returns:
            HTML parsed string.
        '''
        clr_set = {
            0xA: '#0000AA',
            0xD: '#00AA00'
        }

        i = 0
        line = list(string)
        result = list()

        sub_str = list()
        for i, sym in enumerate(line):
            if ord(sym) in clr_set.keys():
                sub_str.append('<span style="color: {}">'.format(
                    clr_set[ord(sym)]))
                sub_str.append('{0:02x}'.format(ord(sym)).upper())
                sub_str.append('</span>')
            else:
                sub_str.append('{0:02x}'.format(ord(sym)).upper())

            if (i + 1)%2 == 0:
                sub_str.append(' ')

            if (i + 1)%16 == 0:
                result.append(''.join(sub_str))
                sub_str = list()

        if sub_str:
            result.append(''.join(sub_str))

        return result


    def divide_text_in_blocks(self, string, length=4):
        """
        Divide string into substring of the 'length'.
        Args:
            string: string to divide.
        Returns:
            Divided string.
        """
        if length < 0:
            return None

        if len(string) < length:
            return string

        return ' '.join(string[i:i + length] for i in range(
            0, len(string), length))


    def port_config(self):
        '''
        Generate port configuration dictinoary. (Used in view)
        Returns:
            Dictionary.
        '''
        return {'baudrate': self._br, 'num_of_bits': self._bytesize, 
                'parity': self._parity, 'num_of_stop': self._stopbits}

#==============================================================================
# Signals
#==============================================================================

    def emit_error(self, value):
        self.error.emit(value)

    def emit_port_conf_change(self, value):
        self.port_conf_change.emit(value)

