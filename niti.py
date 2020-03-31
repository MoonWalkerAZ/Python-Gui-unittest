from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QObject, pyqtSlot

import testExecutor as testExecutor
import testDiscoverer as testDiscoverer

class RunnerThread(QtCore. QThread):
    runner_data = QtCore.pyqtSignal(object)

    def __init__(self, imeDatoteke, list=[]):
        QtCore.QThread.__init__(self)
        self.imeDatoteke = imeDatoteke
        self.list = list

    def run(self):
        val = testExecutor.izvedi(self.imeDatoteke, self.list)
        self.runner_data.emit(val)


class DiscovererThread(QtCore.QThread):
    discoverer_data = QtCore.pyqtSignal(object)

    def __init__(self, imeDatoteke):
        QtCore.QThread.__init__(self)
        self.imeDatoteke = imeDatoteke

    def run(self):
        val = testDiscoverer.isciTeste(self.imeDatoteke)
        self.discoverer_data.emit(val)