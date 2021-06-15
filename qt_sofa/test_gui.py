from itertools import filterfalse
import sys
from qtpy.QtCore import *
from PyQt5 import QtCore, QtGui
from qtpy.QtWidgets import *
from qtpy.QtGui import *

color_range =['#e7f0fd','#accbee','#bac8e0']
            
def get_groove_color(color_range):

    groove_color_range = 'stop:0 ' + color_range[0]
    current_color = color_range[0]
    for i in range(0,len(color_range),1):
        if color_range[i] == current_color :
            continue
        else:
            current_color = color_range[i]
            groove_color_range += ', stop:'+ str((2*i-1)/2/len(color_range)) + ' ' + color_range[i-1] + ', stop:'+ str((2*i)/2/len(color_range)) + ' ' + color_range[i] 

    groove_color_range += ', stop:1 ' + color_range[-1]        
    return groove_color_range

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
    def write(self, text):
        self.textWritten.emit(str(text))

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # TODO add functionality to everything inside options grid
        # font and background settings
        self.font_size = 20
        self.font = 'Helvetica'
        self.background_color = 'black'
        self.text_color = 'white'
        self.simulating = False
        self.mapping = False
        self.buttonstyle_not_clicked = 'QPushButton { background-color: '+self.background_color+'; border-style: outset; border-width: 2px; border-radius: 10px; border-color: red; color: lightgray; min-width: 10em; padding: 6px;}'
        self.buttonstyle_clicked = 'QPushButton { background-color: '+self.background_color+'; border-style: outset; border-width: 2px; border-radius: 10px; border-color: green; color: lightgray; min-width: 10em; padding: 6px;}'
        # Install the custom output stream
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        # add nested layout with options
        options_grid = QVBoxLayout()
        #options_grid.setRowStretch(0,1)
        #options_grid.setRowStretch(1,1)
        #options_grid.setColumnStretch(0,1)
        #options_grid.setColumnStretch(1,1)

        # text edit to which the console output is redirected
        self.text_edit_console = QTextEdit()
        self.text_edit_console.setStyleSheet('QTextEdit {background-color:black; color:white}')
        self.text_edit_console.setCursorWidth(0)
        self.text_edit_console.setReadOnly(True)
        self.text_edit_console.setAlignment(Qt.AlignCenter)
        self.text_edit_console.setFont(QFont(self.font, 14))
        print('Welcome to SLAM Dashboard!')
        options_grid.addWidget(self.text_edit_console)


        # button to start/stop the simulation
        self.button_sim_start = QPushButton("Start Simulation")
        self.button_sim_start.setFont(QFont(self.font, self.font_size, QFont.Bold))
        self.button_sim_start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_sim_start.clicked.connect(self.on_click_button_sim_start)
        options_grid.addWidget(self.button_sim_start)
        # button to start/stop slam
        self.button_slam_start = QPushButton("Start SLAM")
        self.button_slam_start.setFont(QFont(self.font, self.font_size, QFont.Bold))
        self.button_slam_start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_slam_start.setDisabled(True)
        self.button_slam_start.clicked.connect(self.on_click_button_slam_start)
        options_grid.addWidget(self.button_slam_start)
        # TODO checkbox for networkx graph extraction
        #---------
        # slider to adjust volume of the sofa object
        slider_frame = QFrame()
        slider_hbox = QHBoxLayout()
        slider_frame.setLayout(slider_hbox)
        slider_frame.setStyleSheet('border-style: outset; border-width: 2px; border-radius: 10px; border-color: #a9a9a9; min-width: 10em; padding: 6px;')
        options_grid.addWidget(slider_frame, 2)
        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setRange(0,100)
        self.volume_slider.setValue(33)
        self.volume_slider.setFocusPolicy(Qt.NoFocus)
        self.volume_slider.setPageStep(1)
        self.volume_slider.setStyleSheet(\
        "QSlider::groove:horizontal {\
        border: 1px solid #999999;\
        height: 8px; \
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:2, y2:0, "+get_groove_color(color_range)+");\
        margin: -4px 0;\
        border-radius: 4px\
        }QSlider::handle:horizontal {\
        background-color: black;\
        border: 1px solid #5c5c5c;\
        border-color: white;\
        border-radius: 4px;\
        width: 8px;\
        margin: -2px 0;\
        }\
        QSlider{border-width:0px}")
        self.volume_slider.valueChanged.connect(self.on_value_changed_slider)

        #QSlider::sub-page:horizontal {\
        #background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, "+self.groove_color+");\
        #border: 1px solid #999999;\
        #height: 8px;\
        #margin: -4px 0; \
        #}QSlider::add-page:horizontal {\
        #background: white;\
        #border: 1px solid #999999;\
        #height: 8px;\
        #margin: -4px 0; \
        #}
        #self.volume_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.volume_slider.valueChanged.connect(self.updateSliderLabel)
        

        slider_label = QLabel()
        slider_label.setText('SOFA object cavity')
        slider_label.setStyleSheet('QLabel {background-color: '+self.background_color+'; color: lightgray; border-width:0px}')
        slider_label.setFont(QFont(self.font, self.font_size, QFont.Bold))
        slider_hbox.setSpacing(0)
        slider_hbox.setContentsMargins(0,0,0,0)
        slider_hbox.addWidget(slider_label)
        slider_hbox.addWidget(self.volume_slider)




        # set widget as central widget
        widget = QWidget()
        widget.setLayout(options_grid)
        self.setCentralWidget(widget)
        self.resize(500,150)
        options_grid.setContentsMargins(0,0,0,0)
        options_grid.setSpacing(0)
        self.setStyleSheet('QMainWindow{background-color: black;}' + self.buttonstyle_not_clicked)
        self.show()

    def on_click_button_sim_start(self):
        if self.simulating:
            self.simulating = False
            self.button_slam_start.setDisabled(True)
            if self.mapping:
                self.on_click_button_slam_start()
            self.button_sim_start.setText('Start Simulation')
            self.button_sim_start.setStyleSheet(self.buttonstyle_not_clicked)
        else: 
            self.simulating = True
            self.button_slam_start.setDisabled(False)
            self.button_sim_start.setText('Stop Simulation')
            self.button_sim_start.setStyleSheet(self.buttonstyle_clicked)
            print('This should show in the window as well')
        

    def on_click_button_slam_start(self):
        if self.mapping:
            self.mapping = False
            self.button_slam_start.setText('Start SLAM')
            self.button_slam_start.setStyleSheet(self.buttonstyle_not_clicked)
        else: 
            self.mapping = True
            self.button_slam_start.setText('Stop SLAM')
            self.button_slam_start.setStyleSheet(self.buttonstyle_clicked)
    
    def on_value_changed_slider(self,value):
        self.volume_slider.setStyleSheet(\
        "QSlider::groove:horizontal {\
        border: 1px solid #999999;\
        height: 8px; \
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:2, y2:0, "+get_groove_color(color_range)+");\
        margin: -4px 0;\
        border-radius: 4px\
        }QSlider::handle:horizontal {\
        background-color: black;\
        border: 1px solid #5c5c5c;\
        border-color: white;\
        border-radius:" + str(value//11+4) +"px;\
        width:" + str(value//5+8) +"px;\
        margin: -" + str(value//14+2) +"px 0;\
        }\
        QSlider{border-width:0px}")
    
    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__

    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        cursor = self.text_edit_console.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.text_edit_console.setTextCursor(cursor)
        


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())