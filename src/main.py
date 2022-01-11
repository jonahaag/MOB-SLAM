import sys
from gui.mainwindow import MainWindow
from qtpy.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(['Yo'])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
