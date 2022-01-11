from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *
#from PyQt5 import QtCore, QtGui
import os
import pyqtgraph as pg
import pyqtgraph.widgets
import pyqtgraph.opengl as gl
import pyqtgraph.dockarea as da
import numpy as np
import sys
from Widgets import NetworkSLAM as nxs
import qdarkstyle
#sys.path.append("Widgets")
#import NetworkSLAM as nxs
#import networkx as nx

class CustomDialog(QDialog):
    def __init__(self):
        super(CustomDialog, self).__init__()
        # set initials values to widgets
        self.general_tab = QWidget()
        self.general_tab_layout = QVBoxLayout()
        self.general_tab.setLayout(self.general_tab_layout)

        self.slam_tab = QWidget()
        self.slam_tab_layout = QVBoxLayout()
        self.slam_tab.setLayout(self.slam_tab_layout)

        self.sofa_tab = QWidget()
        self.sofa_tab_layout = QVBoxLayout()
        self.sofa_tab.setLayout(self.sofa_tab_layout)

        self.networkx_tab = QWidget()
        self.networkx_tab_layout = QVBoxLayout()
        self.networkx_tab.setLayout(self.networkx_tab_layout)


        self.tab = QTabWidget()
        #tab.setTabPosition(QTabWidget.West)
        self.tab.addTab(self.general_tab,'General')
        self.tab.addTab(self.slam_tab,'SLAM')
        self.tab.addTab(self.sofa_tab,'SOFA')
        self.tab.addTab(self.networkx_tab,'NetworkX')

        self.main_layout = QVBoxLayout() # cannot set widget directly, so this layout just contains the QTabWidget
        self.main_layout.addWidget(self.tab)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.rejected)
        self.main_layout.addWidget(self.buttonBox)
        self.setLayout(self.main_layout)
        self.resize(640,360)
        self.setStyleSheet(qdarkstyle.load_stylesheet(qdarkstyle.dark.palette.DarkPalette))
        
class EmittingStream(QObject):
    textWritten = Signal(str)
    def write(self, text):
        self.textWritten.emit(str(text))

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()  

        # font and background settings, stylesheets
        self.font_size = 20
        self.font = 'Helvetica'
        self.background_color = 'black'
        self.text_color = 'white'
        self.colortheme = 'dark'
        self.buttonstyle_not_clicked = 'QPushButton {color:white}'
        self.buttonstyle_clicked = 'QPushButton {color:red}'
        self.is_mapping = False
        self.is_animating = False
        

        # add gl view widget to layout, this widget consists of...
        # ...scatter plot item for worldpoints
        # ...line plot items for estimated and actual camera positions
        # alternative plotting library: https://github.com/marcomusy/vedo 
        self.slam_results_plot = gl.GLViewWidget()
        self.worldpoint_plot = gl.GLScatterPlotItem()
        self.cam_pos_plot = gl.GLLinePlotItem()
        self.ground_truth_plot = gl.GLLinePlotItem()
        self.axis = gl.GLAxisItem()
        self.grid = gl.GLGridItem()
        self.slam_results_plot.addItem(self.cam_pos_plot)
        self.slam_results_plot.addItem(self.ground_truth_plot)
        self.slam_results_plot.addItem(self.axis)
        self.slam_results_plot.addItem(self.grid)
        self.slam_results_plot.setBackgroundColor('#19232D')
        self.slam_results_plot.opts['distance'] = 3.5         ## distance of camera from center
        self.slam_results_plot.opts['fov'] = 60                ## horizontal field of view in degrees
        self.slam_results_plot.opts['elevation'] = -65          ## camera's angle of elevation in degrees
        self.slam_results_plot.opts['azimuth'] = 30            ## camera's azimuthal angle in degrees 
        self.slam_results_plot.pan(dx=0,dy=0,dz=0.3,relative='global')
        

        # add graphics window to layout, this widget consists of...
        # ...viewbox, which consist of...
        # ...image item to display image
        # ...graph item to display networkx graph
        self.feature_graph_window = pg.GraphicsLayoutWidget()
        self.feature_graph_viewbox = self.feature_graph_window.addViewBox()
        self.feature_graph_viewbox.invertY(True) # else img is upside down
        pg.setConfigOption('imageAxisOrder', 'row-major') # default is column-major
        self.image_item = pg.ImageItem()
        self.feature_graph_viewbox.addItem(self.image_item)
        self.graph_item = pg.GraphItem()
        self.feature_graph_viewbox.addItem(self.graph_item)
        self.graph_item.setZValue(10) # display graph item ontop of image
        #self.feature_graph_viewbox.setContentsMargins(0,0,0,0)
        self.feature_graph_window.setBackground(background=None)
        

        # Install the custom output stream
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

        # text edit to which the console output is redirected
        self.text_edit_console = QTextEdit()
        self.text_edit_console.setCursorWidth(0)
        self.text_edit_console.setReadOnly(True)
        #self.text_edit_console.setAlignment(Qt.AlignCenter)
        #self.text_edit_console.setFont(QFont(self.font, 14))
        print('Welcome to SLAM Dashboard!')

        # button to start/stop the simulation
        self.button_sim_start = QPushButton("Start Simulation")
        self.button_sim_start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_sim_start.clicked.connect(self.on_click_button_sim_start)
        

        # button to start/stop slam
        self.button_slam_start = QPushButton("Start SLAM")
        self.button_slam_start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_slam_start.setDisabled(True)
        self.button_slam_start.clicked.connect(self.on_click_button_slam_start)

        # settings button
        self.button_settings = QPushButton("Settings")
        self.button_settings.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_settings.clicked.connect(self.on_click_button_settings)

        # slider to adjust volume of the sofa object
        # TODO actually add cavity and sofa controller functions
        slider_frame = QFrame()
        slider_hbox = QVBoxLayout()
        slider_frame.setLayout(slider_hbox)
        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setRange(0,100)
        self.volume_slider.setValue(33)
        self.volume_slider.setFocusPolicy(Qt.NoFocus)
        self.volume_slider.setPageStep(1)
        self.volume_slider.valueChanged.connect(self.on_value_changed_slider)
        slider_label = QLabel()
        slider_label.setText('SOFA object cavity')
        slider_label.setAlignment(Qt.AlignCenter)
        slider_hbox.addWidget(slider_label)
        slider_hbox.addWidget(self.volume_slider)

        # add checkboxes inside a horizontal layout
        self.networkx_checkbox = QCheckBox()
        self.networkx_checkbox.setText('Extract Networkx Graph')
        self.networkx_checkbox.stateChanged.connect(self.on_networkx_checkbox_change)
        self.colormode_checkbox = QCheckBox()
        self.colormode_checkbox.setText('Darkmode')
        self.colormode_checkbox.setChecked(True)
        self.colormode_checkbox.stateChanged.connect(self.on_colormode_checkbox_change)
        self.checkbox_layout = QVBoxLayout()
        self.checkbox_layout.addWidget(self.networkx_checkbox)
        self.checkbox_layout.addWidget(self.colormode_checkbox)


        # add nested layout with options
        self.options_layout = QHBoxLayout()
        self.options_layout.addWidget(self.button_sim_start)
        self.options_layout.addWidget(self.button_slam_start)
        self.options_layout.addWidget(self.button_settings)
        self.options_layout.addWidget(slider_frame)
        self.options_layout.addLayout(self.checkbox_layout)
        self.options_layout.addWidget(self.text_edit_console)
        self.options_frame = QFrame()
        self.options_frame.setLayout(self.options_layout)
        

        # add grid as main layout, stretch rows and columns
        self.main_grid = QGridLayout()
        self.main_grid.setRowStretch(0, 1)
        self.main_grid.setRowStretch(1, 1)
        self.main_grid.setColumnStretch(0,1)
        self.main_grid.setColumnStretch(1,1)

        self.view_real = QLabel()
        self.view_real.setText('Hier ist eigentlich die Sofa Ansicht')
        self.view_real.setAlignment(Qt.AlignCenter)

        self.dockWidget_0 = QDockWidget(self)
        self.dockWidget_1 = QDockWidget(self)
        self.dockWidget_2 = QDockWidget(self)
        self.dockWidget_0.setWidget(self.options_frame)
        self.dockWidget_0.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dockWidget_1.setWidget(self.slam_results_plot)
        label = QLabel('')
        label.setAlignment(Qt.AlignCenter)
        self.dockWidget_1.setTitleBarWidget(label)
        self.dockWidget_1.setWindowTitle('SLAM Results')
        self.dockWidget_2.setWidget(self.feature_graph_window)
        label2 = QLabel('')
        label2.setAlignment(Qt.AlignCenter)
        self.dockWidget_2.setTitleBarWidget(label2)
        self.dockWidget_2.setWindowTitle('Feature Graph Plot')
        
        

        self.main_grid.addWidget(self.view_real, 0, 0)
        self.main_grid.addWidget(self.slam_results_plot, 0, 1)
        self.main_grid.addWidget(self.feature_graph_window, 1, 0)
        self.main_grid.addWidget(self.options_frame,1,1)
        self.main_grid.setContentsMargins(0,0,0,0)
        self.main_grid.setSpacing(1)

        # TODO dynamic layout design
        # create QWidget to contain the first level grid layout, set as central widget in main window
        self.widget = QWidget()
        #self.widget.setLayout(self.main_grid)
        self.setCentralWidget(self.widget)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        

        self.addDockWidget(Qt.TopDockWidgetArea,self.dockWidget_0)
        self.addDockWidget(Qt.RightDockWidgetArea,self.dockWidget_1)
        self.addDockWidget(Qt.RightDockWidgetArea,self.dockWidget_2)
        self.tabifyDockWidget(self.dockWidget_1,self.dockWidget_2)
        self.dockWidget_1.raise_()
        #self.addDockWidget(Qt.BottomDockWidgetArea,dockWidget_3)
        #self.setCentralWidget(self.view_real)


        self.setWindowTitle("SLAM Dashboard")
        self.setStyleSheet(qdarkstyle.load_stylesheet(qdarkstyle.dark.palette.DarkPalette))
        self.showFullScreen()
        self.options_frame.setFixedSize(1920,120)
        self.dockWidget_0.setFixedSize(1920,120)
        self.widget.setMaximumSize(960,960)
        self.widget.setMinimumHeight(960)
        self.feature_graph_window.resize(960,960)
        self.slam_results_plot.resize(960,960)

        # for some weird reason this needs to be added later else python crashes on my mac (only true for GLScatterPlotItem and GLImageItem)
        self.slam_results_plot.addItem(self.worldpoint_plot)
        # TODO change initial view of plot, maybe update automatically based on slam results
        # TODO add legend to plots
        #self.slam_results_plot.orbit(0, 1.5708)
        #self.slam_results_plot.pan(0.0,0.0,0.0,relative='global')
        
    def on_click_button_sim_start(self):
        if self.is_animating:
            print("Simulation stopped")
            self.is_animating = False
            if self.is_mapping:
                self.on_click_button_slam_start()
            self.button_slam_start.setDisabled(True)
            self.button_sim_start.setText('Start Simulation')
            self.button_sim_start.setStyleSheet(self.buttonstyle_not_clicked)
        else: 
            print("Simulation started")
            self.is_animating = True
            self.button_slam_start.setDisabled(False)
            self.button_sim_start.setText('Stop Simulation')
            self.button_sim_start.setStyleSheet(self.buttonstyle_clicked)

    def on_click_button_slam_start(self):
        if self.is_mapping:
            print("SLAM stopped")
            self.is_mapping = False
            self.button_slam_start.setText('Start SLAM')
            self.button_slam_start.setStyleSheet(self.buttonstyle_not_clicked)
        else: 
            print("SLAM started")
            self.is_mapping = True
            self.button_slam_start.setText('Stop SLAM')
            self.button_slam_start.setStyleSheet(self.buttonstyle_clicked)
    
    def on_click_button_settings(self):
        w = CustomDialog()
        w.exec()

    def on_value_changed_slider(self,value):
        # self.volume_slider.setStyleSheet(\
        # "QSlider::groove:horizontal {\
        # border: 1px solid #999999;\
        # height: 8px; \
        # background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:2, y2:0, "+get_groove_color(color_range)+");\
        # margin: -4px 0;\
        # border-radius: 4px\
        # }QSlider::handle:horizontal {\
        # background-color: black;\
        # border: 1px solid #5c5c5c;\
        # border-color: white;\
        # border-radius:" + str(value//11+4) +"px;\
        # width:" + str(value//5+8) +"px;\
        # margin: -" + str(value//14+2) +"px 0;\
        # }\
        # QSlider{border-width:0px}")
        return 0
    
    def extract_network(self):
        # TODO skip_counter
        nxs.draw_img_and_graph(image_item=self.image_item, image=self.view_real.get_screen_shot(), graph_item=self.graph_item)

    def on_networkx_checkbox_change(self):
        return 0
    
    def on_colormode_checkbox_change(self):
        if self.colortheme == 'dark':
            self.colortheme = 'light'
            self.setStyleSheet(qdarkstyle.load_stylesheet(qdarkstyle.light.palette.LightPalette))
            self.feature_graph_window.setBackground(background='#CED1D4')
            self.slam_results_plot.setBackgroundColor('#CED1D4')
            self.buttonstyle_not_clicked = 'QPushButton {color:#19232D}'
            self.buttonstyle_clicked = 'QPushButton {color:red}'
            self.text_edit_console.setStyleSheet('QTextEdit {background-color:#CED1D4; color:#19232D}')
        else:
            self.colortheme = 'dark'
            self.setStyleSheet(qdarkstyle.load_stylesheet(qdarkstyle.dark.palette.DarkPalette))
            self.feature_graph_window.setBackground(background=None)
            self.slam_results_plot.setBackgroundColor('#19232D')
            self.buttonstyle_not_clicked = 'QPushButton {color:white}'
            self.buttonstyle_clicked = 'QPushButton {color:red}'
            self.text_edit_console.setStyleSheet('QTextEdit {background-color:#19232D; color:white}')

    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__

    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        cursor = self.text_edit_console.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.text_edit_console.setTextCursor(cursor)

if __name__ == '__main__':
    app = QApplication(['Yo'])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
                

    

                

                