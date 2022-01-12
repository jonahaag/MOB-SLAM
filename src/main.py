import sys
from gui.mainwindow import MainWindow
from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *
import qdarkstyle


class CustomDialog(QDialog):
    def __init__(self):
        super(CustomDialog, self).__init__()

        self.label = QLabel(
            "Welcome to Model based SLAM!\n\nPlease select the desired mode."
        )
        self.label.setAlignment(Qt.AlignCenter)

        self.main_mode_button = QRadioButton("Main")
        self.main_mode_button.setChecked(True)
        self.test_mode_button = QRadioButton("Test")
        self.mode_button_group = QButtonGroup(self)
        self.mode_button_group.addButton(self.main_mode_button)
        self.mode_button_group.addButton(self.test_mode_button)

        self.orb_slam_button = QRadioButton("ORB")
        self.orb_slam_button.setChecked(True)
        self.mob_slam_button = QRadioButton("MOB")
        self.slam_button_group = QButtonGroup(self)
        self.slam_button_group.addButton(self.orb_slam_button)
        self.slam_button_group.addButton(self.mob_slam_button)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.setCenterButtons(True)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.label)
        self.button_layout = QHBoxLayout()
        self.button_layout.setAlignment(Qt.AlignCenter)
        self.button_layout.addWidget(self.main_mode_button)
        self.button_layout.addWidget(QLabel(""))
        self.button_layout.addWidget(self.test_mode_button)
        self.button_layout2 = QHBoxLayout()
        self.button_layout2.setAlignment(Qt.AlignCenter)
        self.button_layout2.addWidget(self.orb_slam_button)
        self.button_layout2.addWidget(QLabel(""))
        self.button_layout2.addWidget(self.mob_slam_button)
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addLayout(self.button_layout2)
        self.main_layout.addWidget(self.buttonBox)
        self.main_layout.setStretch(0, 2)
        self.main_layout.setStretch(1, 1)
        self.main_layout.setStretch(2, 1)
        self.setLayout(self.main_layout)
        self.setFixedSize(300, 200)
        self.setStyleSheet(
            qdarkstyle.load_stylesheet(qdarkstyle.dark.palette.DarkPalette)
        )

    def get_mode(self):
        if self.main_mode_button.isChecked() == True:
            return "main"
        elif self.test_mode_button.isChecked() == True:
            return "test"
    
    def get_slam(self):
        if self.orb_slam_button.isChecked() == True:
            return "orb"
        elif self.mob_slam_button.isChecked() == True:
            return "mob"


if __name__ == "__main__":
    app = QApplication(["Yo"])
    mode_dialog = CustomDialog()
    if mode_dialog.exec_() == QDialog.Accepted:
        mode = mode_dialog.get_mode()
        slam = mode_dialog.get_slam()
        window = MainWindow(mode=mode, slam=slam)
        window.show()
        sys.exit(app.exec())