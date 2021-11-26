import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QTextEdit, QDockWidget, QListWidget, QLabel)
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)

        dockWidget = QDockWidget('Dock', self)

        self.textEdit = QTextEdit()
        self.textEdit.setFontPointSize(16)

        self.listWidget = QListWidget()
        self.listWidget.addItem('Google')
        self.listWidget.addItem('Facebook')
        self.listWidget.addItem('Microsoft')
        self.listWidget.addItem('Apple')
        self.listWidget.itemDoubleClicked.connect(self.get_list_item)

        dockWidget.setWidget(self.listWidget)
        dockWidget.setFloating(False)

        another_dock = QDockWidget('Dock', self)
        another_label = QLabel('Hallo')
        another_list = QListWidget()
        another_list.addItem('This is a List item')
        #another_dock.setTitleBarWidget(another_label)
        another_dock.setWidget(another_list)
        another_dock.setFloating(False)
        self.addDockWidget(Qt.BottomDockWidgetArea, another_dock)


        self.setCentralWidget(self.textEdit)
        self.addDockWidget(Qt.RightDockWidgetArea, dockWidget)

    def get_list_item(self):
        self.textEdit.setPlainText(self.listWidget.currentItem().text())

if __name__ == '__main__':
	app = QApplication(sys.argv)

	window = MainWindow()
	window.show()

	sys.exit(app.exec_())