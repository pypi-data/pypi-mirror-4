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
from PyQt4.QtGui import QDialog
from kidelib.gui.ui.about import Ui_About

import webbrowser


class About(QDialog):

    def open_site(self):
        from kidelib import kide
        webbrowser.open(kide.REPOSITORY)

    def __init__(self, *args, **kargs):
        from kidelib import kide

        super(About, self).__init__(*args, **kargs)
        self.ui = Ui_About()
        self.ui.setupUi(self)

        self.ui.pbOk.clicked.connect(self.close)
        self.ui.pbSite.clicked.connect(self.open_site)

        self.ui.lbVersion.setText(kide.__version__)
