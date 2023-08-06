# -*- coding: utf-8 -*-
'''
    Copyright (C) 2013  Rodrigo Pinheiro Matias <rodrigopmatias@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
from kidelib.gui.main import MainWindow
from kidelib.helpers import System
from PyQt4.QtGui import QApplication

import sys

__version_conf__ = {
    'major': 0,
    'minor': 0,
    'build': 4
}

__version__ = '%(major)d.%(minor)d.%(build)d' % __version_conf__

REPOSITORY = 'https://github.com/rodrigopmatias/kide'


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
