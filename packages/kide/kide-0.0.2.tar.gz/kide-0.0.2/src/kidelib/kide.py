# -*- coding: utf-8 -*-
from kidelib.gui.main import MainWindow
from kidelib.helpers import System
from PyQt4.QtGui import QApplication

import sys

__version_conf__ = {
    'major': 0,
    'minor': 0,
    'build': 2
}

__version__ = '%(major)d.%(minor)d.%(build)d' % __version_conf__


def main():
    System.log.info(' '.join(['-' * 3, 'Start of KIDE', '-' * 3]))
    System.log.info('Loadind global configuration ...')
    System.read_configuration()

    app = QApplication(sys.argv)
    wnd = MainWindow()
    wnd.show()
    rst = app.exec_()

    System.log.info('End of code %d' % rst)
    System.log.info(' '.join(['-' * 3, 'Stop of KIDE', '-' * 3]))
    sys.exit(rst)

if __name__ == '__main__':
    main()
