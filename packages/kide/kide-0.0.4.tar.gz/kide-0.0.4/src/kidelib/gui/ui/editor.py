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
from PyQt4.QtGui import QWidget, QFont, QFontMetrics
from PyQt4.QtGui import QVBoxLayout
from PyQt4.Qsci import QsciScintilla, QsciLexerPython
from kidelib.helpers import System


class Editor(QWidget):

    _lexer = {
        'python': QsciLexerPython
    }

    def factory_lexer(self, name):
        Lexer = self._lexer.get(name, None)

        if Lexer is not None:
            lexer = Lexer()
        else:
            lexer = None
            System.log.warn('Default lexer %s does not exist!' % name)

        return lexer

    def config_editor(self):
        config = System.config.get('editor', {})
        lexer = self.factory_lexer(config.get('default_lexer'))
        self.editor.setLexer(lexer)

        font = QFont(config.get('font_family', 'Monospaced'))
        font.setPointSizeF(float(config.get('font_size', 0) or 0))
        font.setFixedPitch(True)
        fontmetrics = QFontMetrics(font)

        lexer.setDefaultFont(font)

        self.editor.setCaretLineVisible(True)
        self.editor.setBackspaceUnindents(config.get('unindent_backspace'))
        self.editor.setAutoIndent(config.get('indent_auto'))
        self.editor.setIndentationsUseTabs(config.get('indent_use_tabs'))
        self.editor.setIndentationWidth(config.get('indent_width'))
        self.editor.setIndentationGuides(config.get('indent_guides'))

        self.editor.setMarginLineNumbers(0, True)
        self.editor.setMarginsFont(font)
        self.editor.setMarginWidth(0, fontmetrics.width("000000"))

    def __init__(self, *args, **kargs):
        QWidget.__init__(self, *args, **kargs)

        self.editor = QsciScintilla()
        layout = QVBoxLayout()
        layout.addWidget(self.editor)

        self.setLayout(layout)
        self.config_editor()
