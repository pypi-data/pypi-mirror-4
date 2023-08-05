try:
    from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot
except ImportError:
    from PySide import QtCore, QtGui, QtWebKit, QtNetwork
