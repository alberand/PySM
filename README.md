# PySM

Simple serial monitor implemented in Python 3 with usage of PyQt 5. Have basic
function like Arduino IDE serial monitor. Feel free to send me some changes or
bugs =)

Requirements:
- Python 3
- PyQt5 (Remember that you also need to install Qt5)
- PySerial 

### Run:
```
python3 ./main.py
```

### Screenshot:

![Alt text](https://github.com/alberand/PySM/blob/master/stuff/screenshot.png?raw=true "PySM screenshot.")

### TODO
 - Add text decoding. For example: I want to see data in UTF-8, ASCII and Bytes
   formats.
 - Add to screen for HEX representation and ASCII
 - Possibly, color-scheme will be useful. For example, specific HEX codes are
   highlighted by predefined colors. 
    - Editor area for quick addition rules to color-scheme
 - Implements correct policy of interpreting special symbols in editor form.
 - Possibly available hardware ports (RTS, DTR)

References:
===============================================================================
- [PySerial installation guide](http://pyserial.readthedocs.io/en/latest/pyserial.html)
- [PyQt 5 installation guide](http://pyqt.sourceforge.net/Docs/PyQt5/installation.html)
- [Qt 5 installation guide](https://wiki.qt.io/Install_Qt_5_on_Ubuntu)

