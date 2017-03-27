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
from PyQt5.QtWidgets    import QStatusBar
from PyQt5.QtWidgets    import QMenuBar
from PyQt5.QtWidgets    import QFileDialog
from PyQt5.QtCore       import QPoint
from PyQt5.QtCore       import QTimer
from PyQt5.QtCore       import pyqtSignal
from PyQt5.QtCore       import QObject
from PyQt5.QtCore       import Qt
from PyQt5.QtGui        import QFont
from PyQt5.QtGui        import QTextCursor
from PyQt5.QtGui        import QFontMetrics

from math               import floor
from queue              import Queue

import qtawesome        as qta

from config             import config
from status_button      import StatusButton


class View(QWidget):

    # Send data to port
    send_data           = pyqtSignal(object)
    # Chage baudrate
    baudrate_changed    = pyqtSignal(object)
    # Change end of line
    eol_changed         = pyqtSignal(object)
    # Change port
    port_changed        = pyqtSignal(object)
    # Pause model
    pause_m             = pyqtSignal(object)
    # Continue model
    start_m             = pyqtSignal(object)

    def __init__(self):
        QWidget.__init__(self)

        self.queue      = None
        self.end_cmd    = None
        self.autoscroll = False
        self.msg_sent   = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(100)

        self.resize(1000, 600)
        self.__initUI()

    def __initUI(self):
        vbox = QVBoxLayout(self)
        # vbox.setSpacing(0)
        vbox.setContentsMargins(3, 3, 3, 3)

        # Add window's menu bar
        self.menubar = QMenuBar()
        file_menu = self.menubar.addMenu('File')
        file_menu.addAction('Save', self.save_to_file)
        vbox.addWidget(self.menubar)

        # Command box
        cmd_hbox = QHBoxLayout()

        self.cmd_edit = QLineEdit()
        cmd_hbox.addWidget(self.cmd_edit)

        cmd_btn = QPushButton('Send')
        cmd_btn.clicked.connect(self.emit_send_data)
        cmd_hbox.addWidget(cmd_btn)

        self.stat_btn = StatusButton(self.emit_start_m, self.emit_pause_m,
                parent=self)
        cmd_hbox.addWidget(self.stat_btn)

        # cmd_btn = QPushButton('Stop')
        # cmd_btn.clicked.connect(self.pause_m.emit)
        # cmd_hbox.addWidget(cmd_btn)

        vbox.addLayout(cmd_hbox)

        # Editors pair box
        editor_hbox = QHBoxLayout()

        # Text edit area
        self.editer = QPlainTextEdit()
        self.editer.scrollContentsBy = self.ModScrollContentsBy
        self.editer.setReadOnly(True)
        editor_hbox.addWidget(self.editer)

        # HEX edit area
        self.editor_hex = QPlainTextEdit()
        self.editor_hex.scrollContentsBy = self.ModScrollContentsBy

        # font = QFont("serif", 10)
        # font = self.editor_hex.document().defaultFont()
        # fm = QFontMetrics(font)
        # width = fm.width('0'*(config['hex_bytes_in_row']*2 +
            # (floor(config['hex_bytes_in_row']/2) - 1) + 10))
        # print(width)
        # self.editor_hex.setFont(font)

        # self.editor_hex.setFixedWidth(width)
        self.editor_hex.setReadOnly(True)
        editor_hbox.addWidget(self.editor_hex)

        vbox.addLayout(editor_hbox)

        # Settings area
        stng_hbox = QHBoxLayout()

        # - Autoscroll
        chk_btn = QCheckBox('Autoscroll')
        chk_btn.stateChanged.connect(self.set_autoscroll)
        stng_hbox.addWidget(chk_btn)

        cmd_btn = QPushButton('Clear')
        cmd_btn.clicked.connect(self.editer.clear)
        cmd_btn.clicked.connect(self.editor_hex.clear)
        stng_hbox.addWidget(cmd_btn)

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
        self.br_menu.addItem('460800 baud')
        self.br_menu.currentIndexChanged.connect(self.emit_br_changed)
        # Set default baudrate 9600
        self.br_menu.setCurrentIndex(4)

        stng_hbox.addWidget(self.br_menu)

        vbox.addLayout(stng_hbox)

        # Port's list
        ports_hbox_name = QHBoxLayout()
        self.ports_hbox = QHBoxLayout()
        port_lbl = QLabel('Ports: ')
        ports_hbox_name.addWidget(port_lbl)
        ports_hbox_name.addLayout(self.ports_hbox)

        # self.port_edit = QLineEdit()

        # self.port_edit.editingFinished.connect(self.changePort)
        # self.port_hbox.addWidget(self.port_edit)

        vbox.addLayout(ports_hbox_name)

        # Status Bar
        self.status_bar = QStatusBar()

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignRight)

        self.status_bar.addWidget(self.status_label, 1)
        vbox.addWidget(self.status_bar)

        self.setLayout(vbox)

    def remove_all_widgets(self, layout):
        while layout.count() != 0:
            child = layout.takeAt(0)
            if child.layout() != 0:
                lay = child.layout()
                del lay
            elif child.widget() != 0:
                wid = child.widget()
                del wid
            del child

    def add_devices(self, dev_list):
        print('Ports: {}'.format(dev_list))
        self.remove_all_widgets(self.ports_hbox)
        if not dev_list:
            no_devs = QLabel('No ports found.')
            self.ports_hbox.addWidget(no_devs)

            return None

        for device in dev_list:
            device_btn = QPushButton(device.device)
            device_btn.clicked.connect(lambda: self.changePort(device_btn))
            self.ports_hbox.addWidget(device_btn)

        self.update()

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

    # def set_port(self, value):
        # self.port_edit.insert(value)

    def get_cmd(self):
        return self.cmd_edit.text()

    def set_eol(self, value):
        self.eol_menu.setCurrentIndex(value)

    def update_status_bar(self, data_set):
        '''
        Update GUI status bar.
        Args:
            data_set: Dictionary with port configurations: port, baudrate,
            number of bits, parity, number of stop bits.
        '''
        string = '{} {}-{}-{}'.format(data_set['baudrate'],
                data_set['num_of_bits'], data_set['parity'],
                data_set['num_of_stop'])

        self.status_label.setText(string)

    def update_gui(self):
        self.process_incoming()
        self.update()

    def appendText(self, data):
        pos = QPoint(self.editer.textCursor().position(), 0)
        self.editer.moveCursor(QTextCursor.End)
        self.editer.insertPlainText(data[0])
        # self.editer.appendHtml(data[0])
        self.editer.cursorForPosition(pos)

        for line in data[1]:
            self.editor_hex.appendHtml(line)

    def process_incoming(self):
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)

                # self.editer.appendPlainText(msg)
                self.appendText(msg)
                if self.autoscroll:
                    self.editer.ensureCursorVisible()
                    self.editor_hex.ensureCursorVisible()
                    self.scroll_down()
            except Queue.empty:
                pass

    def scroll_down(self):
        for editor in [self.editer, self.editor_hex]:
            sb = editor.verticalScrollBar()
            sb.setValue(sb.maximum())
            editor.moveCursor(QTextCursor.End)

    def changePort(self, btn):
        if not self.msg_sent:
            self.msg_sent = True
            self.emit_port_changed(btn.text())
        else:
            self.msg_sent = False
            return None
#==============================================================================
# Utils
#==============================================================================

    def save_to_file(self):
        _file = QFileDialog.getSaveFileName()
        if _file[0]:
            with open(_file[0], 'w+') as fn:
                fn.write(self.editer.toPlainText())

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

    def emit_port_changed(self, port_name):
        self.port_changed.emit(port_name)

    def emit_pause_m(self):
        print('Pause')
        self.stat_btn.status = 2
        self.pause_m.emit(self)

    def emit_start_m(self):
        print('Start')
        self.stat_btn.status = 0
        self.start_m.emit(self)
#==============================================================================
# Events
#==============================================================================
    def ModScrollContentsBy(self, dx, dy):
        # print('as: {}. dx: {}. dy: {}.'.format(self.autoscroll, dx, dy))
        for editor in [self.editer, self.editor_hex]:
            if self.autoscroll:
                editor.ensureCursorVisible()
            else:
                QPlainTextEdit.scrollContentsBy(editor, dx, dy)

    def closeEvent(self, event):
        self.end_cmd()
        QWidget.closeEvent(self, event)
        print('exit')

