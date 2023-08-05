# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'boing/nodes/uiRecorder.ui'
#
# Created: Tue Sep 18 18:50:09 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_recorder(object):
    def setupUi(self, recorder):
        recorder.setObjectName(_fromUtf8("recorder"))
        recorder.resize(439, 83)
        recorder.setWindowTitle(QtGui.QApplication.translate("recorder", "Recorder", None, QtGui.QApplication.UnicodeUTF8))
        self.mainLayout = QtGui.QHBoxLayout(recorder)
        self.mainLayout.setMargin(3)
        self.mainLayout.setObjectName(_fromUtf8("mainLayout"))
        self.frame = QtGui.QFrame(recorder)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.framelayout = QtGui.QHBoxLayout(self.frame)
        self.framelayout.setMargin(0)
        self.framelayout.setObjectName(_fromUtf8("framelayout"))
        self.mainLayout.addWidget(self.frame)
        self.startstop = QtGui.QPushButton(recorder)
        self.startstop.setMinimumSize(QtCore.QSize(50, 50))
        self.startstop.setMaximumSize(QtCore.QSize(50, 50))
        self.startstop.setFocusPolicy(QtCore.Qt.NoFocus)
        self.startstop.setText(QtGui.QApplication.translate("recorder", "Record", None, QtGui.QApplication.UnicodeUTF8))
        self.startstop.setShortcut(QtGui.QApplication.translate("recorder", "Space", None, QtGui.QApplication.UnicodeUTF8))
        self.startstop.setCheckable(True)
        self.startstop.setChecked(True)
        self.startstop.setObjectName(_fromUtf8("startstop"))
        self.mainLayout.addWidget(self.startstop)

        self.retranslateUi(recorder)
        QtCore.QMetaObject.connectSlotsByName(recorder)

    def retranslateUi(self, recorder):
        pass

