# -*- coding: utf-8 -*-
from PyQt4.QtGui import QMainWindow
from kidelib.gui.ui.main import Ui_MainWindow
from kidelib.helpers import System


class MainWindow(QMainWindow):

    def __init__(self, *args, **kargs):
        super(MainWindow, self).__init__(*args, **kargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        System.log.info(System.config)
