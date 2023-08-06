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

# Form implementation generated from reading ui file 'src/kidelib/gui/ui/about.ui'
#
# Created: Fri Jan 11 12:27:11 2013
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_About(object):
    def setupUi(self, About):
        About.setObjectName(_fromUtf8("About"))
        About.setWindowModality(QtCore.Qt.ApplicationModal)
        About.resize(450, 337)
        About.setMinimumSize(QtCore.QSize(450, 270))
        About.setMaximumSize(QtCore.QSize(450, 600))
        self.verticalLayout = QtGui.QVBoxLayout(About)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.frame = QtGui.QFrame(About)
        self.frame.setMinimumSize(QtCore.QSize(350, 200))
        self.frame.setMaximumSize(QtCore.QSize(450, 200))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout.addWidget(self.frame)
        self.frame_2 = QtGui.QFrame(About)
        self.frame_2.setMinimumSize(QtCore.QSize(0, 0))
        self.frame_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame_2.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.frame_4 = QtGui.QFrame(self.frame_2)
        self.frame_4.setMinimumSize(QtCore.QSize(0, 30))
        self.frame_4.setMaximumSize(QtCore.QSize(16777215, 30))
        self.frame_4.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_4.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_4.setObjectName(_fromUtf8("frame_4"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.frame_4)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label = QtGui.QLabel(self.frame_4)
        self.label.setMinimumSize(QtCore.QSize(75, 0))
        self.label.setMaximumSize(QtCore.QSize(75, 16777215))
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_3.addWidget(self.label)
        self.lbVersion = QtGui.QLabel(self.frame_4)
        self.lbVersion.setObjectName(_fromUtf8("lbVersion"))
        self.horizontalLayout_3.addWidget(self.lbVersion)
        self.verticalLayout_2.addWidget(self.frame_4)
        self.frame_5 = QtGui.QFrame(self.frame_2)
        self.frame_5.setMinimumSize(QtCore.QSize(0, 30))
        self.frame_5.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame_5.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_5.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_5.setObjectName(_fromUtf8("frame_5"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.frame_5)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(self.frame_5)
        self.label_2.setMinimumSize(QtCore.QSize(75, 0))
        self.label_2.setMaximumSize(QtCore.QSize(75, 16777215))
        self.label_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.lblAuthor = QtGui.QLabel(self.frame_5)
        self.lblAuthor.setTextFormat(QtCore.Qt.RichText)
        self.lblAuthor.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblAuthor.setObjectName(_fromUtf8("lblAuthor"))
        self.horizontalLayout_2.addWidget(self.lblAuthor)
        self.verticalLayout_2.addWidget(self.frame_5)
        self.verticalLayout.addWidget(self.frame_2)
        self.frame_3 = QtGui.QFrame(About)
        self.frame_3.setMinimumSize(QtCore.QSize(0, 40))
        self.frame_3.setMaximumSize(QtCore.QSize(16777215, 40))
        self.frame_3.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_3.setLineWidth(0)
        self.frame_3.setObjectName(_fromUtf8("frame_3"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame_3)
        self.horizontalLayout.setSpacing(-1)
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setContentsMargins(4, 0, 4, 0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pbSite = QtGui.QPushButton(self.frame_3)
        self.pbSite.setMinimumSize(QtCore.QSize(0, 35))
        self.pbSite.setMaximumSize(QtCore.QSize(16777215, 35))
        self.pbSite.setObjectName(_fromUtf8("pbSite"))
        self.horizontalLayout.addWidget(self.pbSite)
        self.pbOk = QtGui.QPushButton(self.frame_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pbOk.sizePolicy().hasHeightForWidth())
        self.pbOk.setSizePolicy(sizePolicy)
        self.pbOk.setMinimumSize(QtCore.QSize(75, 35))
        self.pbOk.setMaximumSize(QtCore.QSize(16777215, 35))
        self.pbOk.setObjectName(_fromUtf8("pbOk"))
        self.horizontalLayout.addWidget(self.pbOk)
        self.verticalLayout.addWidget(self.frame_3)

        self.retranslateUi(About)
        QtCore.QMetaObject.connectSlotsByName(About)

    def retranslateUi(self, About):
        About.setWindowTitle(_translate("About", "About", None))
        self.label.setText(_translate("About", "Version :", None))
        self.lbVersion.setText(_translate("About", "TextLabel", None))
        self.label_2.setText(_translate("About", "Authors :", None))
        self.lblAuthor.setText(_translate("About", "<html><head/><body><p><a href=\"mailto:rodrigopmatias@gmail.com\"><span style=\" text-decoration: underline; color:#0057ae;\">Rodrigo Pinheiro Matias</span></a></p></body></html>", None))
        self.pbSite.setText(_translate("About", "Go to the Site", None))
        self.pbOk.setText(_translate("About", "Ok", None))

