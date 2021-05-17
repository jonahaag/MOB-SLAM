from Widgets import MainWindow
from qtpy.QtWidgets import QApplication
import sys


if __name__ == '__main__':
    app = QApplication(['Yo'])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
