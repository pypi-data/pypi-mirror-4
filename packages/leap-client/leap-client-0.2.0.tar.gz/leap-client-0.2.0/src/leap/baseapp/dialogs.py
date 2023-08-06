# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import logging

from PyQt4.QtGui import (QDialog, QFrame, QPushButton, QLabel, QMessageBox)

logger = logging.getLogger(name=__name__)


class ErrorDialog(QDialog):
    def __init__(self, parent=None, errtype=None, msg=None, label=None):
        super(ErrorDialog, self).__init__(parent)
        frameStyle = QFrame.Sunken | QFrame.Panel
        self.warningLabel = QLabel()
        self.warningLabel.setFrameStyle(frameStyle)
        self.warningButton = QPushButton("QMessageBox.&warning()")

        if msg is not None:
            self.msg = msg
        if label is not None:
            self.label = label
        if errtype == "critical":
            self.criticalMessage(self.msg, self.label)

    def warningMessage(self, msg, label):
        msgBox = QMessageBox(QMessageBox.Warning,
                             "LEAP Client Error",
                             msg,
                             QMessageBox.NoButton, self)
        msgBox.addButton("&Ok", QMessageBox.AcceptRole)
        if msgBox.exec_() == QMessageBox.AcceptRole:
            pass
            # do whatever we want to do after
            # closing the dialog. we can pass that
            # in the constructor

    def criticalMessage(self, msg, label):
        msgBox = QMessageBox(QMessageBox.Critical,
                             "LEAP Client Error",
                             msg,
                             QMessageBox.NoButton, self)
        msgBox.addButton("&Ok", QMessageBox.AcceptRole)
        msgBox.exec_()

        # It's critical, so we exit.
        # We should better emit a signal and connect it
        # with the proper shutdownAndQuit method, but
        # this suffices for now.
        logger.info('Quitting')
        import sys
        sys.exit()

    def confirmMessage(self, msg, label, action):
        msgBox = QMessageBox(QMessageBox.Critical,
                             self.tr("LEAP Client Error"),
                             msg,
                             QMessageBox.NoButton, self)
        msgBox.addButton("&Ok", QMessageBox.AcceptRole)
        msgBox.addButton("&Cancel", QMessageBox.RejectRole)

        if msgBox.exec_() == QMessageBox.AcceptRole:
            action()
