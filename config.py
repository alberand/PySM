#!/usr/bin/env python
# coding=utf-8

import serial as s

config = {
        # Default port
        'port': '/dev/ttyUSB0',
        # Baudrate
        'baudrate': 9600,
        # Timeout
        'timeout': 3,
        # End of line
        'eol':[
            '',
            '\n',
            '\r',
            '\r\n'
        ],
        # Data encoding (hex, none)
        'in_hex': False,
        # Decoding 'ASCII' or 'UTF-8'
        'encode': 'ASCII',
        # Parity (PARITY_NONE, PARITY_EVEN, PARITY_ODD PARITY_MARK, 
        # PARITY_SPACE)
        'parity': s.PARITY_NONE,
        # Bytesize (FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS)
        'bytesize': s.EIGHTBITS,
        # Number of stop bits (STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, 
        # STOPBITS_TWO)
        'stopbits': s.STOPBITS_ONE,
        # HEX console coloring
        'hex_colors': True,
        'hex_bytes_in_row': 16,
        # Colors definition for highlitning
        'clr_set':  {
            0x0A: '#0000AA',
            0x0D: '#00AA00'
        }
}
