import sys
from gui.mainwindow import MainWindow
from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *
import qdarkstyle


class CustomDialog(QDialog):
    """Popup dialog for some basic settings when starting the GUI, inherits from QDialog
    """
    def __init__(self):
        """Constructor of class CustomDialog
        """
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

        self.keypoint_navigation_button = QRadioButton("Keypoint Navigation")
        self.keypoint_navigation_button.setChecked(True)
        self.from_file_navigation_button = QRadioButton("From File")
        self.to_file_navigation_button = QRadioButton("To File")
        self.navigation_button_group = QButtonGroup(self)
        self.navigation_button_group.addButton(self.keypoint_navigation_button)
        self.navigation_button_group.addButton(self.from_file_navigation_button)
        self.navigation_button_group.addButton(self.to_file_navigation_button)

        self.path = "trajectories/navigation/keypoints1.txt"
        self.path_label = QLabel("Trajectory Path:")
        self.path_edit = QLineEdit(self.path)
        self.path_edit.setAlignment(Qt.AlignRight)
        self.path_edit.textChanged.connect(
            self.on_path_changed
        )

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
        self.button_layout3 = QHBoxLayout()
        self.button_layout3.setAlignment(Qt.AlignCenter)
        self.button_layout3.addWidget(self.keypoint_navigation_button)
        self.button_layout3.addWidget(self.from_file_navigation_button)
        self.button_layout3.addWidget(self.to_file_navigation_button)
        self.path_layout = QHBoxLayout()
        self.path_layout.addWidget(self.path_label)
        self.path_layout.addWidget(self.path_edit)
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addLayout(self.button_layout2)
        self.main_layout.addLayout(self.button_layout3)
        self.main_layout.addLayout(self.path_layout)
        self.main_layout.addWidget(self.buttonBox)
        self.main_layout.setStretch(0, 2)
        self.main_layout.setStretch(1, 1)
        self.main_layout.setStretch(2, 1)
        self.setLayout(self.main_layout)
        self.setFixedSize(400, 300)
        self.setStyleSheet(
            qdarkstyle.load_stylesheet(qdarkstyle.dark.palette.DarkPalette)
        )

    def on_path_changed(self, text):
        self.path = text

    def get_mode(self):
        """Getter-function for the selected layout mode

        Returns:
            str: "main" or "test" to signal the desired layout
        """
        if self.main_mode_button.isChecked() == True:
            return "main"
        elif self.test_mode_button.isChecked() == True:
            return "test"
    
    def get_slam(self):
        """Getter-function for the selected slam mode

        Returns:
            str: "orb" or "mob" to signal the desired slam
        """
        if self.orb_slam_button.isChecked() == True:
            return "orb"
        elif self.mob_slam_button.isChecked() == True:
            return "mob"

    def get_navigation(self):
        """Getter-function for the selected navigation mode

        Returns:
            str: "keypoint_navigation" or "fromfile" or "tofile" to signal the desired mode
        """
        if self.keypoint_navigation_button.isChecked() == True:
            return "keypoint_navigation"
        elif self.from_file_navigation_button.isChecked() == True:
            return "fromfile"
        elif self.to_file_navigation_button.isChecked() == True:
            return "tofile"

    def get_trajectory_path(self):
        return self.path

if __name__ == "__main__":
    app = QApplication(["Yo"])
    mode_dialog = CustomDialog()
    if mode_dialog.exec_() == QDialog.Accepted:
        mode = mode_dialog.get_mode()
        slam = mode_dialog.get_slam()
        navigation = mode_dialog.get_navigation()
        trajectory_path = mode_dialog.get_trajectory_path()
        window = MainWindow(mode=mode, slam=slam, navigation=navigation, trajectory_path=trajectory_path)
        window.show()
        sys.exit(app.exec())
