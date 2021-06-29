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
from Widgets import NetworkSLAM as nxs
import qdarkstyle
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

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
    def write(self, text):
        self.textWritten.emit(str(text))

class CustomDialog(QDialog):
    def __init__(self,colortheme):
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
        if colortheme == 'dark':
            self.setStyleSheet(qdarkstyle.load_stylesheet(qdarkstyle.dark.palette.DarkPalette))
        else:
            self.setStyleSheet(qdarkstyle.load_stylesheet(qdarkstyle.light.palette.LightPalette))

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
        self.sofa_sim.animation_end.connect(self.view_sim.update) 
        

        # font and background settings, stylesheets
        self.font_size = 20
        self.font = 'Helvetica'
        self.background_color = 'black'
        self.text_color = 'white'
        self.colortheme = 'dark'
        self.buttonstyle_not_clicked = 'QPushButton {color:white}'
        self.buttonstyle_clicked = 'QPushButton {color:red}'
        

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
        self.sim_start_button = QPushButton("Start Simulation")
        self.sim_start_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.sim_start_button.clicked.connect(self.on_click_button_sim_start)
        

        # button to start/stop slam
        self.slam_start_button = QPushButton("Start SLAM")
        self.slam_start_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.slam_start_button.setDisabled(True)
        self.slam_start_button.clicked.connect(self.on_click_button_slam_start)

        # settings button
        self.settings_button = QPushButton("Settings")
        self.settings_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.settings_button.clicked.connect(self.on_click_button_settings)

        # slider to adjust volume of the sofa object
        # TODO actually add cavity and sofa controller functions
        self.slider_frame = QFrame()
        self.slider_hbox = QHBoxLayout()
        self.slider_frame.setLayout(self.slider_hbox)
        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setRange(0,100)
        self.volume_slider.setValue(33)
        self.volume_slider.setFocusPolicy(Qt.NoFocus)
        self.volume_slider.setPageStep(1)
        self.volume_slider.valueChanged.connect(self.on_value_changed_slider)
        self.slider_label = QLabel()
        self.slider_label.setText('SOFA object cavity')
        self.slider_label.setAlignment(Qt.AlignCenter)
        self.slider_hbox.addWidget(self.slider_label)
        self.slider_hbox.addWidget(self.volume_slider)

        # add checkboxes inside a horizontal layout
        self.networkx_checkbox = QCheckBox()
        self.networkx_checkbox.setText('Extract Networkx Graph')
        self.networkx_checkbox.stateChanged.connect(self.on_networkx_checkbox_change)
        self.colormode_checkbox = QCheckBox()
        self.colormode_checkbox.setText('Darkmode')
        self.colormode_checkbox.setChecked(True)
        self.colormode_checkbox.stateChanged.connect(self.on_colormode_checkbox_change)
        self.checkbox_layout = QHBoxLayout()
        self.checkbox_layout.addWidget(self.networkx_checkbox)
        self.checkbox_layout.addWidget(self.colormode_checkbox)


        # add nested layout with options
        self.options_layout = QHBoxLayout()
        self.options_layout.addWidget(self.sim_start_button)
        self.options_layout.addWidget(self.slam_start_button)
        self.options_layout.addWidget(self.settings_button)
        self.options_layout.addWidget(self.slider_frame)
        self.options_layout.addLayout(self.checkbox_layout)
        self.options_layout.addWidget(self.text_edit_console)
        self.options_frame = QFrame()
        self.options_frame.setLayout(self.options_layout)

        # add grid as main layout, stretch rows and columns
        # self.main_grid = QGridLayout()
        # self.main_grid.setRowStretch(0, 1)
        # self.main_grid.setRowStretch(1, 1)
        # self.main_grid.setColumnStretch(0,1)
        # self.main_grid.setColumnStretch(1,1)
        # self.main_grid.addWidget(self.view_real, 0, 0)
        # self.main_grid.addWidget(self.slam_results_plot, 0, 1)
        # self.main_grid.addWidget(self.feature_graph_window, 1, 0)
        # self.main_grid.addWidget(self.options_frame,1,1)
        # self.main_grid.setContentsMargins(0,0,0,0)
        # self.main_grid.setSpacing(1)

        #create dock widgets for options and plots that contain the previously created widgets/layouts
        self.options_dockWidget = QDockWidget(self)
        self.options_dockWidget.setWidget(self.options_frame)
        self.options_dockWidget.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.slam_plot_dockWidget = QDockWidget(self)
        self.slam_plot_dockWidget.setWidget(self.slam_results_plot)
        self.slam_plot_dockWidget.setTitleBarWidget(QLabel(''))
        self.slam_plot_dockWidget.setWindowTitle('SLAM Results')

        self.feature_graph_dockWidget = QDockWidget(self)
        self.feature_graph_dockWidget.setWidget(self.feature_graph_window)
        self.feature_graph_dockWidget.setTitleBarWidget(QLabel(''))
        self.feature_graph_dockWidget.setWindowTitle('Feature Graph Plot')


        # create QWidget to contain the first level grid layout, set as central widget in main window
        self.widget = QWidget()
        self.view_layout = QVBoxLayout()
        self.view_layout.addWidget(self.view_real)
        self.widget.setLayout(self.view_layout)
        self.setCentralWidget(self.widget)
        #self.setCentralWidget(self.view_real)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.addDockWidget(Qt.TopDockWidgetArea,self.options_dockWidget)
        self.addDockWidget(Qt.RightDockWidgetArea,self.slam_plot_dockWidget)
        self.addDockWidget(Qt.RightDockWidgetArea,self.feature_graph_dockWidget)
        self.tabifyDockWidget(self.slam_plot_dockWidget,self.feature_graph_dockWidget)
        self.slam_plot_dockWidget.raise_()

        # window settings (size, stylesheet, ...)
        self.setWindowTitle("SLAM Dashboard")
        self.setStyleSheet(qdarkstyle.load_stylesheet(qdarkstyle.dark.palette.DarkPalette))
        self.showFullScreen()
        self.resize_widgets()

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
                                    trajectory_path="./trajectories/navigation/")
        self.mat_engine.set_image_source(self.real_world)
        self.mat_engine.set_viewer(self.view_real)
        self.mat_engine.set_sim(self.sofa_sim)
        self.mat_engine.set_main_window(self)
        

    def resize_widgets(self):
        self.screen_height = self.height()
        self.screen_width = self.width()
        print('Window is ' + str(self.screen_width) + 'x' + str(self.screen_height))
        # self.options_frame.setFixedSize(1920,120)
        # self.options_dockWidget.setFixedSize(1920,120)
        # self.view_real.setMaximumSize(960,960)
        # self.view_real.setMinimumHeight(960)
        # self.slam_results_plot.resize(960,960)
        # self.feature_graph_window.resize(960,960)
        self.options_frame.setFixedSize(self.screen_width,self.screen_height//9)
        self.options_dockWidget.setFixedSize(self.screen_width,self.screen_height//9)
        self.view_real.setMaximumSize(self.screen_width//2,self.screen_height-self.screen_height//9)
        self.view_real.setMinimumHeight(self.screen_height-self.screen_height//9)
        self.slam_results_plot.resize(self.screen_width//2,self.screen_height-self.screen_height//9)
        self.feature_graph_window.resize(self.screen_width//2,self.screen_height-self.screen_height//9)

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
            print(self.view_real.get_viewer_size())

    def on_click_button_sim_start(self):
        if self.real_world.is_animating:
            print("Simulation stopped")
            if self.mat_engine.is_mapping:
                self.on_click_button_slam_start()
            self.real_world.stop_sim()
            self.sofa_sim.stop_sim()
            self.mat_engine.stop_sim()
            self.slam_start_button.setDisabled(True)
            self.sim_start_button.setText('Start Simulation')
            self.sim_start_button.setStyleSheet(self.buttonstyle_not_clicked)
        else: 
            print("Simulation started")
            self.real_world.start_sim()
            self.sofa_sim.start_sim()
            self.mat_engine.start_sim()
            self.slam_start_button.setDisabled(False)
            self.sim_start_button.setText('Stop Simulation')
            self.sim_start_button.setStyleSheet(self.buttonstyle_clicked)

    def on_click_button_slam_start(self):
        if self.mat_engine.is_mapping:
            print("SLAM stopped")
            self.mat_engine.stop_slam()
            self.slam_start_button.setText('Start SLAM')
            self.slam_start_button.setStyleSheet(self.buttonstyle_not_clicked)
        else: 
            print("SLAM started")
            self.mat_engine.start_slam()
            self.slam_start_button.setText('Stop SLAM')
            self.slam_start_button.setStyleSheet(self.buttonstyle_clicked)
    
    def on_click_button_settings(self):
        w = CustomDialog(self.colortheme)
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
        if self.mat_engine.is_extracting_graph:
            self.real_world.animation_end.disconnect(self.extract_network)
        else:
            self.real_world.animation_end.connect(self.extract_network)
        self.mat_engine.is_extracting_graph = not self.mat_engine.is_extracting_graph
    
    def on_colormode_checkbox_change(self):
        if self.colortheme == 'dark':
            self.colortheme = 'light'
            self.setStyleSheet(qdarkstyle.load_stylesheet(qdarkstyle.light.palette.LightPalette))
            self.feature_graph_window.setBackground(background='#CED1D4')
            self.slam_results_plot.setBackgroundColor('#CED1D4')
            self.view_real.set_background_color([1.0,1.0,1.0,1.0])
            self.buttonstyle_not_clicked = 'QPushButton {color:#19232D}'
            self.buttonstyle_clicked = 'QPushButton {color:red}'
            self.text_edit_console.setStyleSheet('QTextEdit {background-color:#CED1D4; color:#19232D}')
        else:
            self.colortheme = 'dark'
            self.setStyleSheet(qdarkstyle.load_stylesheet(qdarkstyle.dark.palette.DarkPalette))
            self.feature_graph_window.setBackground(background=None)
            self.slam_results_plot.setBackgroundColor('#19232D')
            self.view_real.set_background_color([25/255,35/255,45/255,1])
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
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.text_edit_console.setTextCursor(cursor)


                

    

                

                