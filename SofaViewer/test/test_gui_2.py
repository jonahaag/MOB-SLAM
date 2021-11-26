from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from PyQt5 import QtCore, QtGui
import os
import pyqtgraph as pg
import pyqtgraph.widgets
import pyqtgraph.opengl as gl
import pyqtgraph.dockarea as da
import numpy as np
import sys
import qdarkstyle

class CustomDialog(QDialog):
    def __init__(self):
        super(CustomDialog, self).__init__()

        
        self.tab_1 = QWidget()
        self.tab_2 = QWidget()
        self.tab_3 = QWidget()

        self.tab = QTabWidget()
        #tab.setTabPosition(QTabWidget.West)
        self.tab.addTab(self.tab_1,'A')
        self.tab.addTab(self.tab_2,'B')
        self.tab.addTab(self.tab_3,'C')

        self.main_layout = QVBoxLayout() # cannot set widget directly, so this layout just contains the QTabWidget
        self.main_layout.addWidget(self.tab)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.main_layout.addWidget(self.buttonBox)
        self.setLayout(self.main_layout)
        self.setStyleSheet(qdarkstyle.load_stylesheet(qdarkstyle.dark.palette.DarkPalette))
    
    def button_press(self):
        print('Trying to close')
        self.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__() 
        self.button = QPushButton('Click me')
        self.button.clicked.connect(self.button_clicked)
        self.setCentralWidget(self.button)
    
    def button_clicked(self):
        dialog = CustomDialog()
        dialog.exec()

if __name__ == '__main__':
    app = QApplication(['Yo'])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())