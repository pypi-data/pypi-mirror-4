# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from functools import partial
import logging
import platform
import signal

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)
from PyQt4.QtGui import (QApplication, QSystemTrayIcon, QMessageBox)
from PyQt4 import QtCore

from leap import __version__ as VERSION
from leap.baseapp.mainwindow import LeapWindow
from leap.util import polkit
from leap.gui import locale_rc


def sigint_handler(*args, **kwargs):
    logger = kwargs.get('logger', None)
    logger.debug('SIGINT catched. shutting down...')
    mainwindow = args[0]
    mainwindow.shutdownSignal.emit()


def main():
    """
    launches the main event loop
    long live to the (hidden) leap window!
    """
    import sys
    from leap.util import leap_argparse
    parser, opts = leap_argparse.init_leapc_args()
    debug = getattr(opts, 'debug', False)

    # XXX get severity from command line args
    if debug:
        level = logging.DEBUG
    else:
        level = logging.WARNING

    logger = logging.getLogger(name='leap')
    logger.setLevel(level)
    console = logging.StreamHandler()
    console.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s '
        '- %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    logger.info('LEAP client version %s', VERSION)
    logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    logfile = getattr(opts, 'log_file', False)
    if logfile:
        logger.debug('setting logfile to %s ', logfile)
        fileh = logging.FileHandler(logfile)
        fileh.setLevel(logging.DEBUG)
        fileh.setFormatter(formatter)
        logger.addHandler(fileh)

    logger.info('Starting app')
    app = QApplication(sys.argv)

    # launch polkit-auth agent if needed
    if platform.system() == "Linux":
        polkit.check_if_running_polkit_auth()

    # To test:
    # $ LANG=es ./app.py
    locale = QtCore.QLocale.system().name()
    qtTranslator = QtCore.QTranslator()
    if qtTranslator.load("qt_%s" % locale, ":/translations"):
        app.installTranslator(qtTranslator)
    appTranslator = QtCore.QTranslator()
    if appTranslator.load("leap_client_%s" % locale, ":/translations"):
        app.installTranslator(appTranslator)

    # needed for initializing qsettings
    # it will write .config/leap/leap.conf
    # top level app settings
    # in a platform independent way
    app.setOrganizationName("leap")
    app.setApplicationName("leap")
    app.setOrganizationDomain("leap.se")

    # XXX we could check here
    # if leap-client is already running, and abort
    # gracefully in that case.

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "Systray",
                             "I couldn't detect"
                             "any system tray on this system.")
        sys.exit(1)
    if not debug:
        QApplication.setQuitOnLastWindowClosed(False)

    window = LeapWindow(opts)

    # this dummy timer ensures that
    # control is given to the outside loop, so we
    # can hook our sigint handler.
    timer = QtCore.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    sigint_window = partial(sigint_handler, window, logger=logger)
    signal.signal(signal.SIGINT, sigint_window)

    if debug:
        # we only show the main window
        # if debug mode active.
        # if not, it will be set visible
        # from the systray menu.
        window.show()
        if sys.platform == "darwin":
            window.raise_()

    # run main loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
