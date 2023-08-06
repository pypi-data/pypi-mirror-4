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
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QKeySequence
from kidelib.gui.ui.main import Ui_MainWindow
from kidelib.gui.ui.editor import Editor
from kidelib.gui.about import About
from kidelib.gui.dockproject import DockProject
from kidelib.helpers import System

import webbrowser
import re


class MainWindow(QMainWindow):

    editor_count = 0

    def call_command(self):
        params = {
            'scope': self,
            'current_tab': self.ui.tabWidget.currentWidget(),
            'tabs': self.ui.tabWidget
        }

        System.log.debug(params)

    def tab_close(self, index):
        System.log.info('Close tab with index %d' % index)
        self.ui.tabWidget.removeTab(index)

    def show_about(self):
        System.log.info('Show about Window')
        about = About(parent=self)
        about.show()

    def new_editor(self):
        System.log.info('Create new Editor')
        self.editor_count += 1
        widget = Editor(self)
        self.ui.tabWidget.addTab(widget, 'Editor %d' % self.editor_count)
        self.ui.tabWidget.setCurrentWidget(widget)

    def open_site(self, resource):
        re_http = re.compile(r'^http(|s)://(\w|_|\d)+(\.(\w|_|\d)+)+/?.+$')

        if re_http.match(resource):
            webbrowser.open(resource)

    def _createMenu(self, menu, conf):
        for item in conf.get('menu', []):
            menu_type = item.get('type', 'empty')
            if menu_type == 'action':
                self._createAction(
                    menu.addAction(item.get('text')),
                    item
                )
            elif menu_type == 'menu':
                self._createMenu(
                    menu.addMenu(item.get('text')),
                    item
                )
            elif menu_type == 'separator':
                menu.addSeparator()
            elif menu_type == 'empty':
                pass

    def fn_proxy(self, fn, args, kargs):
        def proxy():
            fn(*args, **kargs)
        return proxy

    def _createAction(self, menu, conf):
        slots = conf.get('slots', {})

        for key in slots.keys():
            slot = slots.get(key, {})
            fn = None
            fn_slot = None
            code = 'fn = %s\nfn_slot = menu.%s' % (slot.get('fn'), key)

            try:
                exec(code)
            except:
                fn = None
                fn_slot = None
            finally:
                fn_slot.connect(
                    self.fn_proxy(
                        fn,
                        slot.get('args'),
                        slot.get('kargs')
                    )
                )

            shortcuts = [
                QKeySequence(keys)
                for keys in conf.get('shortcuts', [])
            ]
            menu.setShortcuts(shortcuts)

    def tab_changed(self, *args, **kargs):
        System.log.debug(args)
        System.log.debug(kargs)

    def __init__(self, *args, **kargs):
        super(MainWindow, self).__init__(*args, **kargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.menu = self.menuBar()

        self.addDockWidget(1, DockProject())
        self._createMenu(self.menu, System.config)

        self.ui.tabWidget.currentChanged.connect(self.tab_changed)
        self.ui.tabWidget.tabCloseRequested.connect(self.tab_close)
