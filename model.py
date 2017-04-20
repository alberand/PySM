#!/usr/bin/env python
# coding=utf-8

# System imports
import  sys
import  glob
import  queue
import  select
import  logging
import  threading
from    time                import sleep
from    sys                 import exit

# PyQt5 imports
from    PyQt5.QtCore        import pyqtSignal
from    PyQt5.QtCore        import QObject

# PySerial imports
import  serial
import  serial.tools.list_ports
from    serial.serialutil   import SerialException

from config import config

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Model(threading.Thread, QObject):

    # Signal emitted when port configuratin changes
    port_conf_change = pyqtSignal(object)

    update_device_list = pyqtSignal(object)

    # Emitted to indecate that error occured.
    # Fails: open port/close port/read from port/write to port
    error = pyqtSignal(object)
    # Emitted when data is ready
    data_ready = pyqtSignal(object)

    def __init__(self):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        # Queue with data (lines) received from serial port
        self.queue      = queue.Queue()
        self.paused = threading.Event()
        self.paused.clear()

        # Set configuration from config file
        self.set_configuration(config['port'], config['baudrate'], 
                config['parity'], config['bytesize'], config['stopbits'],
                config['timeout'], config['eol'][0])

        # PySerial object
        self.ser = serial.Serial(baudrate=self._br, timeout=self.timeout,
                bytesize=self._bytesize, parity=self._parity,
                stopbits=self._stopbits)
        # Flag for main cycle
        self.running    = True
        self.current_ports = []

    def set_configuration(self, port=None, br=9600, parity=serial.PARITY_NONE, 
            bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, timeout=3,
            eol='\n'):
        self._port      = port or config['port']
        self._br        = br or config['baudrate']
        self._parity    = parity or config['parity']
        self._bytesize  = bytesize or config['bytesize']
        self._stopbits  = stopbits or config['stopbits']
        self.timeout    = timeout or config['timeout']
        self.eol        = eol or config['eol'][0]

    def run(self):
        '''
        Run thread.
        In every iteration trying to read one line from serial port and put
        it in queue.
        '''
        try:
            while self.running:
                data = b''

                if self.scan_ports():
                    logger.info("Update port's list. Ports: {}.".format(
                        self.current_ports))

                self.paused.wait()
                if not self.ser.isOpen():
                    self.open_port()

                rlist = select.select([self.ser], [], [], self.timeout)
                if not rlist:
                    continue 
                elif self.paused.isSet():
                    try:
                        size = self.ser.inWaiting()
                        if size:
                            data = self.read(size)
                    except SerialException as e:
                        logger.error('Error occured while reading data. ' + str(e))
                else:
                        sleep(0.05)
                        continue

                if data:
                    decoded = ''
                    if config['in_hex']:
                        # Only for Python 3.5 and newer
                        decoded = data.hex().upper()
                    else:
                        if config['encode'].upper() in ['ASCII', 'UTF-8']:
                            try:
                                decoded = data.decode(config['encode'])
                            except UnicodeError as e:
                                logger.warn('Fail to decode bytes. Error: {}'.format(
                                    e))
                        else:
                            logger.error('Wrong decoding format. Using ASCII.')
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

    def open_port(self):
        if self.ser:
            logger.debug('Opening port {}.'.format(self._port))
            try:
                self.ser.open()
                self.resume()
            except SerialException as e:
                self.emit_error(0, 'Can\'t open port: ' + str(self._port) + '.')
                logger.debug('Fail to open port: {}'.format(e))

    def close_port(self):
        if self.ser:
            try:
                self.ser.close()
            except SerialException as e:
                self.emit_error(1, 'Can\'t close port: ' + str(port) + '.')
                logger.debug('Fail to close port: {}'.format(e))

    def pause(self):
        if self.ser.isOpen():
            self.close_port()

        if self.paused.isSet():
            self.paused.clear()


    def resume(self):
        if not self.ser.isOpen():
            self.open_port()

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

    def scan_ports(self):
        '''
        Scans serial ports and if found changes in ports list (new one, one
        dissapear etc.) update current port list.
        Returns:
            True if update.
        '''
        found_ports = self.list_serial_ports()
        if found_ports != self.current_ports:
            self.current_ports = found_ports
            self.emit_update_device_list(self.current_ports)

            return True

        return False


    def list_serial_ports(self):
        """
        Lists serial port names
        """
        return serial.tools.list_ports.comports()

#==============================================================================
# PySerial communication
#==============================================================================
    def read(self, size=1):
        '''
        Read all bytes in waiting buffer. 
        Args:
            size: integer specify number of bytes to read. Default is 1.
        Returns:
            String
        '''
        data = None

        if self.ser.isOpen():
            logger.debug('Size to read: {}.'.format(size))
            try:
                data = self.ser.read(size)
                self.ser.flushInput()
            except TypeError as e:
                logger.error('Error while reading: {}.'.format(e))
                self.emit_error(2, 'Fail reading from port: {}'.format(
                    self._port))
        else:
            logger.info('Can\'t read from the port. Port isn\'t open.')

        return data

    def readline(self):
        '''
        Read line from serial port. Read byte by byte until program get '\n'
        symbol.
        Returns:
            String
        '''
        data = b''

        if self.ser.isOpen():
            try:
                data = self.ser.readline()
                self.ser.flushInput()
            except SerialException as e:
                logger.error(('Exception occured, while reading line from ' 
                        'serial port.'))
                self.emit_error(2, 'Fail reading from port: {}'.format(
                    self._port))
        else:
            logger.info('Can\'t read from the port. Port isn\'t open.')

        return data

    def write(self, data):
        '''
        Write data to serial port.
        Args:
            data: data to send
        '''
        if self.ser.isOpen():
            try:
                self.ser.write(bytes(data, self.config['encode']) + 
                               bytes(self.get_eol(), self.config['encode']))
                self.ser.flushOutput()
            except SerialExceptin as e:
                logger.error(('Exception occured, while writing to serial port.'
                        '{}').format(e))
                self.emit_error(3, 'Fail writing to port: {}'.format(
                    self._port))
        else:
            logger.info('Can\'t write to the port. Port isn\'t open.')

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
        logger.debug('Set new port: {}.'.format(port))
        if self.ser and self.ser.isOpen():
            self.close_port()

        if self.ser.port != port:
            self._port = port
            self.ser.port = port
        else:
            return None

    def get_queue(self):
        return self.queue

    def set_eol(self, index):
        if index < len(config['eol']) and index >= 0:
            self.eol = config['eol'][index]
        else:
            logger.error('Can\t set up this type of End Of Line. Because it\'s '
                    'not instandart list.')

    def get_eol(self):
        return self.eol

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

        i = 0
        line = list(string)
        result = list()

        sub_str = list()
        for i, sym in enumerate(line):
            if ord(sym) in config['clr_set'].keys():
                sub_str.append('<span style="color: {}">'.format(
                    config['clr_set'][ord(sym)]))
                sub_str.append('{0:02x}'.format(ord(sym)).upper())
                sub_str.append('</span>')
            else:
                sub_str.append('{0:02x}'.format(ord(sym)).upper())

            if (i + 1)%2 == 0:
                sub_str.append(' ')

            if (i + 1)%config['hex_bytes_in_row'] == 0:
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

    def emit_error(self, code, msg):
        '''
        Emits error signal. Signals:
            0 = Fail to open port
            1 = Fail to close port
            2 = Fail to read from the port
            3 = Fail to write to the port
        Args:
            code: int in range 0 - 3.
        '''
        if code in range(3):
            self.error.emit(msg)
        else:
            logger.debug('Unknown error code.')

    def emit_data_ready(self, data):
        '''
        Emits that data read from serial port is ready to send.
        Args:
            data: string
        '''
        self.data_ready.emit(data)

    def emit_port_conf_change(self, value):
        self.port_conf_change.emit(value)

    def emit_update_device_list(self, dev_list):
        self.update_device_list.emit(dev_list)

if __name__ == '__main__':
    a = Model()
    print(a.list_serial_ports())
