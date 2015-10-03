#!/usr/bin/env python
# coding=utf-8

# Library imports
from PyQt5.QtWidgets    import QWidget
from PyQt5.QtWidgets    import QLabel
from PyQt5.QtWidgets    import QLineEdit
from PyQt5.QtWidgets    import QPushButton
from PyQt5.QtWidgets    import QPlainTextEdit
from PyQt5.QtWidgets    import QCheckBox
from PyQt5.QtWidgets    import QVBoxLayout
from PyQt5.QtWidgets    import QHBoxLayout
from PyQt5.QtWidgets    import QComboBox
from PyQt5.QtWidgets    import QMessageBox
from PyQt5.QtCore       import QTimer
from PyQt5.QtCore       import QObject
from PyQt5.QtCore       import pyqtSignal

from queue              import Queue


class View(QWidget):

    send_data           = pyqtSignal(object)
    baudrate_changed    = pyqtSignal(object)
    eol_changed         = pyqtSignal(object)
    port_changed        = pyqtSignal(object)

    def __init__(self):
        QWidget.__init__(self)

        self.queue      = None
        self.end_cmd    = None
        self.autoscroll = True
        self.msg_sent   = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(100)
                
        self.__initUI()

    def __initUI(self):
        vbox = QVBoxLayout(self)

        # Command box
        cmd_hbox = QHBoxLayout()

        self.cmd_edit = QLineEdit()
        cmd_hbox.addWidget(self.cmd_edit)

        cmd_btn = QPushButton('Send')
        cmd_btn.clicked.connect(self.emit_send_data)
        cmd_hbox.addWidget(cmd_btn)

        vbox.addLayout(cmd_hbox)

        # Text edit area
        self.editer = QPlainTextEdit()
        vbox.addWidget(self.editer)

        # Settings area
        stng_hbox = QHBoxLayout()

        # - Autoscroll
        chk_btn = QCheckBox('Autoscroll')
        chk_btn.stateChanged.connect(self.set_autoscroll)
        stng_hbox.addWidget(chk_btn)

        stng_hbox.addStretch(1)

        # - Ending of line
        self.eol_menu = QComboBox()
        self.eol_menu.addItem('No line ending')
        self.eol_menu.addItem('Newline')
        self.eol_menu.addItem('Carriage return')
        self.eol_menu.addItem('Both NL + CR')
        self.eol_menu.setCurrentIndex(0)
        self.eol_menu.currentIndexChanged.connect(self.emit_eol_changed)
        stng_hbox.addWidget(self.eol_menu)

        # - Baudrate select
        self.br_menu = QComboBox()
        self.br_menu.addItem('300 baud')
        self.br_menu.addItem('1200 baud')
        self.br_menu.addItem('2400 baud')
        self.br_menu.addItem('4800 baud')
        self.br_menu.addItem('9600 baud')
        self.br_menu.addItem('19200 baud')
        self.br_menu.addItem('38400 baud')
        self.br_menu.addItem('57600 baud')
        self.br_menu.addItem('115200 baud')
        self.br_menu.addItem('230400 baud')
        self.br_menu.addItem('250000 baud')
        self.br_menu.currentIndexChanged.connect(self.emit_br_changed)
        # Set default baudrate 9600
        self.br_menu.setCurrentIndex(4)

        stng_hbox.addWidget(self.br_menu)

        vbox.addLayout(stng_hbox)

        port_hbox = QHBoxLayout()
        port_lbl = QLabel('Port: ')
        port_hbox.addWidget(port_lbl)

        self.port_edit = QLineEdit()

        self.port_edit.editingFinished.connect(self.changePort)
        port_hbox.addWidget(self.port_edit)

        vbox.addLayout(port_hbox)

        self.setLayout(vbox)

    def show_error(self, value):
        msg = QMessageBox(
                QMessageBox.NoIcon, 'Error occured.', value, QMessageBox.Ok)
        msg.exec()

#==============================================================================
# Get, set
#==============================================================================

    def set_queue(self, queue):
        self.queue = queue

    def set_end_cmd(self, end_cmd):
        self.end_cmd = end_cmd

    def set_autoscroll(self, value):
        self.autoscroll = value

    def set_port(self, value):
        self.port_edit.insert(value)

    def get_cmd(self):
        return self.cmd_edit.text()

    def set_eol(self, value):
        self.eol_menu.setCurrentIndex(value)

    def closeEvent(self, event):
        self.end_cmd()
        QWidget.closeEvent(self, event)
        print('exit')

    def update_gui(self):
        self.process_incoming()
        self.update()

    def process_incoming(self):
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it
                print(str(msg))
                self.editer.appendPlainText(str(msg))
                if self.autoscroll:
                    self.editer.ensureCursorVisible()
                    self.scroll_down()
            except Queue.empty:
                pass

    def scroll_down(self):
        sb = self.editer.verticalScrollBar()
        sb.setValue(sb.maximum())


    def changePort(self):
        if not self.msg_sent:
            self.msg_sent = True
            self.emit_port_changed()
        else:
            self.msg_sent = False
            return None

#==============================================================================
# Signals
#==============================================================================

    def emit_send_data(self):
        self.send_data.emit(self.get_cmd())
        self.cmd_edit.clear()

    def emit_br_changed(self, value):
        baudrate = self.br_menu.itemText(value)[:-5]
        self.baudrate_changed.emit(baudrate)

    def emit_eol_changed(self, value):
        self.eol_changed.emit(value)

    def emit_port_changed(self):
        self.port_changed.emit(self.port_edit.text())
