from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from PyQt5 import QtCore, QtGui
from .SofaGLViewer import SofaGLViewer
from .SofaSim import SofaSim
from .QXBoxViewController import QXBoxViewController
from .QSofaViewKeyboardController import QSofaViewKeyboardController
from .engineORB import EngineORB
import os
import pyqtgraph as pg
import pyqtgraph.widgets
import pyqtgraph.opengl as gl
import numpy as np
import sys
#sys.path.append("Widgets")
#import NetworkSLAM as nxs
#import networkx as nx

class SecondWindow(QMainWindow):
    def __init__(self):
        super(SecondWindow, self).__init__()
        self.sofa_sim = SofaSim()  # class to hold the scene
        self.sofa_sim.init_sim()  # initialize the scene
        self.view_sim = SofaGLViewer(sofa_visuals_node=self.sofa_sim.root, camera=self.sofa_sim.root.camera)
        # self.setCentralWidget(self.view_sim)
        # self.setWindowTitle("Simulated scene")

    ## create Mayavi Widget and show

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
    def __init__(self):
        super(MainWindow, self).__init__()
        self.real_world = SofaSim()  # class to hold the scene, simulation representing the real world
        self.real_world.init_sim()  # initialize the scene

        # create an opengl view to display a node from sofa and control a camera
        self.view_real = SofaGLViewer(sofa_visuals_node=self.real_world.root, camera=self.real_world.root.camera)

        # set the view to be the main widget of the window. In the future, this should be done in a layout
        #self.setCentralWidget(self.view_real)
        #self.setWindowTitle("'Real world' view")

        self.real_world.animation_end.connect(self.view_real.update)  # set a qt signal to update the view after sim step

        # Add a class to control a view's camera using an xbox controller
        # self.view_control = QXBoxViewController(dead_zone=0.3, translate_rate_limit=1.5, rotate_rate_limit=20)
        # self.view_control.set_viewer(self.sofa_view)  # set the active view to control
        self.view_control = QSofaViewKeyboardController(translate_rate_limit=1, rotate_rate_limit=5, update_rate=20)
        self.view_control.set_viewer(self.view_real)

        # draw the scene at a constant update rate. This is done so the scene is drawn even if nothing is being animated
        self.view_control.start_auto_update()
        
        # create an opengl view to display sofa simulation for model-based slam             
        self.simWindow = SecondWindow()
        # self.simWindow.show() # views do not update correctly
        self.sofa_sim = self.simWindow.sofa_sim
        self.view_sim = self.simWindow.view_sim
        # right now view of the second window is updated after every simulation step of the first window (aka the real world)
        # later measurement data can be used to adjust the position of the simulated camera accordingly or the tracking results can be used as well
        # ??? views do not update correctly
        self.sofa_sim.animation_end.connect(self.view_sim.update) 
        

        # font and background settings, stylesheets
        self.font_size = 20
        self.font = 'Helvetica'
        self.background_color = 'black'
        self.text_color = 'white'
        self.buttonstyle_not_clicked = 'QPushButton { background-color: '+self.background_color+'; border-style: outset; border-width: 2px; border-radius: 10px; border-color: red; color: lightgray; min-width: 10em; padding: 6px;}'
        self.buttonstyle_clicked = 'QPushButton { background-color: '+self.background_color+'; border-style: outset; border-width: 2px; border-radius: 10px; border-color: green; color: lightgray; min-width: 10em; padding: 6px;}'
        

        ### maybe add sofa_view seperately once real camera_data is used
        # requires some layout redesign though
        # layout.addWidget(self.sofa_view_sim)
        # widget = QWidget()
        # widget.setLayout(layout)
        # self.setCentralWidget(widget)

        # add gl view widget to layout, this widget consists of...
        # ...scatter plot item for worldpoints
        # ...line plot items for estimated and actual camera positions
        # alternative plotting library: https://github.com/marcomusy/vedo 
        self.slam_results_plot = gl.GLViewWidget()
        self.worldpoint_plot = gl.GLScatterPlotItem()
        self.cam_pos_plot = gl.GLLinePlotItem()
        self.ground_truth_plot = gl.GLLinePlotItem()
        axis = gl.GLAxisItem()
        self.slam_results_plot.addItem(self.cam_pos_plot)
        self.slam_results_plot.addItem(self.ground_truth_plot)
        self.slam_results_plot.addItem(axis)

        # add graphics window to layout, this widget consists of...
        # ...viewbox, which consist of...
        # ...image item to display image
        # ...graph item to display networkx graph
        self.feature_graph_window = pg.GraphicsWindow()
        self.feature_graph_viewbox = self.feature_graph_window.addViewBox()
        self.feature_graph_viewbox.invertY(True) # else img is upside down
        pg.setConfigOption('imageAxisOrder', 'row-major') # default is column-major
        self.image_item = pg.ImageItem()
        self.feature_graph_viewbox.addItem(self.image_item)
        self.graph_item = pg.GraphItem()
        self.feature_graph_viewbox.addItem(self.graph_item)
        self.graph_item.setZValue(10) # display graph item ontop of image
        #self.feature_graph_viewbox.setContentsMargins(0,0,0,0)
        

        # Install the custom output stream
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

        # text edit to which the console output is redirected
        self.text_edit_console = QTextEdit()
        self.text_edit_console.setStyleSheet('QTextEdit {background-color:black; color:white, border-width:0px;}')
        self.text_edit_console.setCursorWidth(0)
        self.text_edit_console.setReadOnly(True)
        self.text_edit_console.setAlignment(Qt.AlignCenter)
        self.text_edit_console.setFont(QFont(self.font, 14))
        print('Welcome to SLAM Dashboard!')

        # button to start/stop the simulation
        self.button_sim_start = QPushButton("Start Simulation")
        self.button_sim_start.setFont(QFont(self.font, self.font_size, QFont.Bold))
        self.button_sim_start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_sim_start.clicked.connect(self.on_click_button_sim_start)
        

        # button to start/stop slam
        self.button_slam_start = QPushButton("Start SLAM")
        self.button_slam_start.setFont(QFont(self.font, self.font_size, QFont.Bold))
        self.button_slam_start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_slam_start.setDisabled(True)
        self.button_slam_start.clicked.connect(self.on_click_button_slam_start)

        # TODO menu for light/dark mode selection, networkx graph extraction, skip_images_main, navigation_mode etc.
        #---------

        # slider to adjust volume of the sofa object
        # TODO actually add cavity and sofa controller functions
        slider_frame = QFrame()
        slider_hbox = QHBoxLayout()
        slider_frame.setLayout(slider_hbox)
        slider_frame.setStyleSheet('border-style: outset; border-width: 2px; border-radius: 10px; border-color: #a9a9a9; min-width: 10em; padding: 6px;')
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
        slider_label = QLabel()
        slider_label.setText('SOFA object cavity')
        slider_label.setStyleSheet('QLabel {background-color: '+self.background_color+'; color: lightgray; border-width:0px}')
        slider_label.setFont(QFont(self.font, self.font_size, QFont.Bold))
        slider_hbox.setSpacing(0)
        slider_hbox.setContentsMargins(0,0,0,0)
        slider_hbox.addWidget(slider_label)
        slider_hbox.addWidget(self.volume_slider)

        # add checkboxes inside a horizontal layout
        self.networkx_checkbox = QCheckBox()
        self.networkx_checkbox.setText('Extract Networkx Graph')
        self.networkx_checkbox.stateChanged.connect(self.on_networkx_checkbox_change)
        self.colormode_checkbox = QCheckBox()
        self.colormode_checkbox.setText('Darkmode')
        self.colormode_checkbox.setChecked(True)
        self.networkx_checkbox.stateChanged.connect(self.on_colormode_checkbox_change)
        self.checkbox_layout = QHBoxLayout()
        self.checkbox_layout.addWidget(self.networkx_checkbox)
        self.checkbox_layout.addWidget(self.colormode_checkbox)


        # add nested layout with options
        self.options_layout = QVBoxLayout()
        self.options_layout.addWidget(self.text_edit_console)
        self.options_layout.addWidget(self.button_sim_start)
        self.options_layout.addWidget(self.button_slam_start)
        self.options_layout.addWidget(slider_frame)
        self.options_layout.addLayout(self.checkbox_layout)
        self.options_frame = QFrame()
        self.options_frame.setLayout(self.options_layout)
        self.options_frame.setStyleSheet('background-color:black;')
        self.networkx_checkbox.setStyleSheet('QCheckBox{background-color:black; color: lightgray;}')
        self.colormode_checkbox.setStyleSheet('QCheckBox{background-color:black; color: lightgray;}')

        # add grid as main layout, stretch rows and columns
        self.main_grid = QGridLayout()
        self.main_grid.setRowStretch(0, 1)
        self.main_grid.setRowStretch(1, 1)
        self.main_grid.setColumnStretch(0,1)
        self.main_grid.setColumnStretch(1,1)
        self.main_grid.addWidget(self.view_real, 0, 0)
        self.main_grid.addWidget(self.slam_results_plot, 0, 1)
        self.main_grid.addWidget(self.feature_graph_window, 1, 0)
        self.main_grid.addWidget(self.options_frame,1,1)
        self.main_grid.setContentsMargins(0,0,0,0)
        self.main_grid.setSpacing(1)

        # TODO dynamic layout design
        # create QWidget to contain the first level grid layout, set as central widget in main window
        self.widget = QWidget()
        self.widget.setLayout(self.main_grid)
        self.setCentralWidget(self.widget)
        self.setWindowTitle("SLAM Dashboard")
        self.setStyleSheet('QMainWindow{background-color: white;}' + self.buttonstyle_not_clicked)
        self.showFullScreen()

        # for some weird reason this needs to be added later else python crashes on my mac (only true for GLScatterPlotItem and GLImageItem)
        self.slam_results_plot.addItem(self.worldpoint_plot)
        # TODO change initial view of plot, maybe update automatically based on slam results
        # TODO add legend to plots
        #self.slam_results_plot.orbit(0, 1.5708)
        #self.slam_results_plot.pan(0.0,0.0,0.0,relative='global')
        
        # initialize matlab engine and slam tracking/mapping the real world
        current_dir = os.path.dirname(__file__)
        mat_dir = os.path.join(current_dir,"../../matlab_slam/")
        self.mat_engine = EngineORB(mat_dir=mat_dir,
                                    skip_images_init=4, 
                                    skip_images_main=10, 
                                    mode="keypoint_navigation", #tofile, fromfile, keypoint_navigation 
                                    trajectory_path="./trajectories/navigation/",
                                    worldpoint_plot = self.worldpoint_plot,
                                    cam_pos_plot = self.cam_pos_plot,
                                    ground_truth_plot = self.ground_truth_plot,
                                    image_item = self.image_item,
                                    graph_item = self.graph_item)
        self.mat_engine.set_image_source(self.real_world)
        self.mat_engine.set_viewer(self.view_real)
        self.mat_engine.set_sim(self.sofa_sim)
        

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Space:
            if self.real_world.is_animating:
                self.real_world.stop_sim()
                self.sofa_sim.stop_sim()
            else:
                print("Simulation started")
                self.real_world.start_sim()
                self.sofa_sim.start_sim()
        if QKeyEvent.key() == Qt.Key_P:
            print(self.slam_results_plot.cameraPosition())

    def on_click_button_sim_start(self):
        if self.real_world.is_animating:
            print("Simulation stopped")
            if self.mat_engine.is_mapping:
                print('Mapping has been stopped as the simulation was stopped')
                self.button_slam_start.setText('Start SLAM')
                self.button_slam_start.setStyleSheet(self.buttonstyle_not_clicked)
            self.real_world.stop_sim()
            self.sofa_sim.stop_sim()
            self.mat_engine.stop_sim()
            self.button_slam_start.setDisabled(True)
            self.button_sim_start.setText('Start Simulation')
            self.button_sim_start.setStyleSheet(self.buttonstyle_not_clicked)
        else: 
            print("Simulation started")
            self.real_world.start_sim()
            self.sofa_sim.start_sim()
            self.mat_engine.start_sim()
            self.button_slam_start.setDisabled(False)
            self.button_sim_start.setText('Stop Simulation')
            self.button_sim_start.setStyleSheet(self.buttonstyle_clicked)

    def on_click_button_slam_start(self):
        if self.mat_engine.is_mapping:
            print("SLAM stopped")
            self.mat_engine.stop_slam()
            self.button_slam_start.setText('Start SLAM')
            self.button_slam_start.setStyleSheet(self.buttonstyle_not_clicked)
        else: 
            print("SLAM started")
            self.mat_engine.start_slam()
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
    
    def on_networkx_checkbox_change(self):
        self.mat_engine.is_extracting_graph = not self.mat_engine.is_extracting_graph

    def on_colormode_checkbox_change(self):
        return 0
    
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


                

    

                

                