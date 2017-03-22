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

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        self._lyt  = QHBoxLayout()
        self._lyt.setSpacing(0)
        self._lyt.setContentsMargins(0, 0, 0, 0)

        # fa.play fa.stop fa.pause fa.spinner
        self._icon = 'fa.play'
        self._text = 'Connect'
        self._btn  = QPushButton(qta.icon(self._icon), self._text, parent=self)
        self._clr  = '#0F822C'
        self._btn.setStyleSheet('background-color: {};'.format(self._clr))
        # Status 0: connected, 1: loading, 2: paused
        self.status = 0
        self.clicked = self._btn.clicked

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
        return self.status

    @status.setter
    def status(self, status):
        if not status:
            return None

        if status not in range(3):
            return None

        if status == 0:
            self._text = 'Running'
            self._icon = qta.icon('fa.play')
            self._clr  = '#0F822C'
        elif status == 1:
            self._text = 'Loading'
            self._icon = qta.icon('fa.spinner')
            self._clr  = '#D8D8D8'
        elif status == 2:
            print('Paused')
            self._text = 'Paused'
            self._icon = qta.icon('fa.pause')
            self._clr  = '#DB9292'
        else:
            pass

        self._repaint()

    def _repaint(self):
        self._btn.setStyleSheet('background-color: {};'.format(self._clr))
        self._btn.setText(self._text)
        self._btn.setIcon(self._icon)
        self.update()
