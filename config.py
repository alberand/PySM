#!/usr/bin/env python
# coding=utf-8

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
        # Parity
        'parity':[
            'N', # None
            'O', # Odd
            'E', # Even
            'M', # Mark
            'S'  # Space
        ]
}
