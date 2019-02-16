# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(676, 497)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.openGLWidget = QtWidgets.QOpenGLWidget(self.centralwidget)
        self.openGLWidget.setObjectName("openGLWidget")
        self.horizontalLayout.addWidget(self.openGLWidget)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.primitiveComboBox = QtWidgets.QComboBox(self.groupBox)
        self.primitiveComboBox.setGeometry(QtCore.QRect(10, 50, 151, 27))
        self.primitiveComboBox.setObjectName("primitiveComboBox")
        self.primitiveComboBox.addItem("")
        self.primitiveComboBox.addItem("")
        self.primitiveComboBox.addItem("")
        self.primitiveComboBox.addItem("")
        self.primitiveComboBox.addItem("")
        self.primitiveComboBox.addItem("")
        self.primitiveComboBox.addItem("")
        self.primitiveComboBox.addItem("")
        self.primitiveComboBox.addItem("")
        self.primitiveComboBox.addItem("")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(10, 30, 161, 17))
        self.label.setObjectName("label")
        self.updateButton = QtWidgets.QPushButton(self.groupBox)
        self.updateButton.setGeometry(QtCore.QRect(10, 90, 85, 27))
        self.updateButton.setObjectName("updateButton")
        self.horizontalLayout.addWidget(self.groupBox)
        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 676, 25))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.actionExit.triggered.connect(MainWindow.close)
        self.updateButton.clicked.connect(self.openGLWidget.update)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Примитивы openGL"))
        self.groupBox.setTitle(_translate("MainWindow", "Элементы управления"))
        self.primitiveComboBox.setItemText(0, _translate("MainWindow", "GL_POINTS"))
        self.primitiveComboBox.setItemText(1, _translate("MainWindow", "GL_LINES"))
        self.primitiveComboBox.setItemText(2, _translate("MainWindow", "GL_LINE_STRIP"))
        self.primitiveComboBox.setItemText(3, _translate("MainWindow", "GL_LINE_LOOP"))
        self.primitiveComboBox.setItemText(4, _translate("MainWindow", "GL_TRIANGLES"))
        self.primitiveComboBox.setItemText(5, _translate("MainWindow", "GL_TRIANGLE_STRIP"))
        self.primitiveComboBox.setItemText(6, _translate("MainWindow", "GL_TRIANGLE_FAN"))
        self.primitiveComboBox.setItemText(7, _translate("MainWindow", "GL_QUADS"))
        self.primitiveComboBox.setItemText(8, _translate("MainWindow", "GL_QUAD_STRIP"))
        self.primitiveComboBox.setItemText(9, _translate("MainWindow", "GL_POLYGON"))
        self.label.setText(_translate("MainWindow", "Выберите примитив"))
        self.updateButton.setText(_translate("MainWindow", "Обновить"))
        self.menuFile.setTitle(_translate("MainWindow", "Файл"))
        self.actionExit.setText(_translate("MainWindow", "Выход"))


