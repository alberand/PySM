from PyQt5.QtWidgets    import QWidget
from PyQt5.QtWidgets    import QLabel
from PyQt5.QtWidgets    import QPushButton
from PyQt5.QtWidgets    import QVBoxLayout
from PyQt5.QtWidgets    import QHBoxLayout
from PyQt5.QtCore       import pyqtSignal
from PyQt5.QtCore       import QObject

from math               import floor
from queue              import Queue

import qtawesome        as qta

from config             import config


class StatusButton(QWidget):

    def __init__(self, start_m, pause_m, parent=None):
        QWidget.__init__(self, parent=parent)

        self._lyt  = QHBoxLayout()
        self._lyt.setSpacing(0)
        self._lyt.setContentsMargins(0, 0, 0, 0)

        # Signals: 0: start signal, pause signal
        self._sigs = [start_m, pause_m]
        # fa.play fa.stop fa.pause fa.spinner
        self._st_loading()
        self._btn  = QPushButton(self._icon, self._text, parent=self)
        self._btn.setStyleSheet('background-color: {};'.format(self._clr))
        self._btn.clicked.connect(self._sigs[1])
        # Status 0: connected, 1: loading, 2: paused
        self._status = 1

        self._lyt.addWidget(self._btn)
        self.setLayout(self._lyt)

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, name):
        if not name:
            return None

        if name not in ['play', 'stop', 'pause', 'spinner']:
            return None

        self._icon = qta.icon('fa.{}'.format(name))

    @property
    def text(self):
        return self._text

    @text.setter
    def icon(self, text):
        if not text:
            return None

        self._text = text

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        # print('Status {}'.format(status))
        if not self.sigs:
            print('Can\'t change status before signals will be assigned.')
            return None

        if status not in range(3):
            return None

        self._status = status
        # print('Chaging status to: {}.'.format(self._status))
        if status == 0:
            self._st_running()
        elif status == 1:
            self._st_loading()
        elif status == 2:
            self._st_paused()
        else:
            pass

        self._repaint()

    def _st_running(self):
        self._text = 'Pause'
        self._icon = qta.icon('fa.pause')
        self._clr  = '#DB9292'
        self._btn.disconnect()
        self._btn.clicked.connect(self._sigs[1])

    def _st_loading(self):
        self._text = 'Loading'
        self._icon = qta.icon('fa.spinner')
        self._clr  = '#D8D8D8'

    def _st_paused(self):
        self._text = 'Run'
        self._icon = qta.icon('fa.play')
        self._clr  = '#0F822C'
        self._btn.disconnect()
        self._btn.clicked.connect(self._sigs[0])

    @property
    def sigs(self):
        return self._sigs

    @sigs.setter
    def sigs(self, signals):
        if not signals:
            return None

        self._sigs = signals

    def _repaint(self):
        self._btn.setStyleSheet('background-color: {};'.format(self._clr))
        self._btn.setText(self._text)
        self._btn.setIcon(self._icon)
        self.update()
