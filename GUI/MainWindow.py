from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from SofaViewer.Widgets.SofaGLViewer import SofaGLViewer
from SofaViewer.Widgets.SofaSim import SofaSim
from SofaViewer.Widgets.QSofaViewKeyboardController import QSofaViewKeyboardController
from GUI.EngineORB import EngineORB
from FeatureGraph import NetworkSLAM as nxs
import os
import pyqtgraph as pg
# import pyqtgraph.widgets
import pyqtgraph.opengl as gl
# import numpy as np
import sys
import qdarkstyle

class SecondWindow(QMainWindow):
    def __init__(self):
        super(SecondWindow, self).__init__()
        self.sofa_sim = SofaSim()  # class to hold the scene
        self.sofa_sim.init_sim()  # initialize the scene
        self.view_sim = SofaGLViewer(sofa_visuals_node=self.sofa_sim.root, camera=self.sofa_sim.root.camera)
        # self.setCentralWidget(self.view_sim)
        # self.setWindowTitle("Simulated scene")

class EmittingStream(QObject):
    textWritten = Signal(str)
    def write(self, text):
        self.textWritten.emit(str(text))

class CustomDialog(QDialog):
    def __init__(self,colortheme,young_modulus,poisson_ratio,visual_flags,n_of_keypoints,max_distance,skip_images):
        super(CustomDialog, self).__init__()

        ### initialize each tab as QWidget, then add Layout and Widgets to that QWidget
        # first some general settings, so far only the option to switch between 
        # 1) "fixed" view of the slam results plot and
        # 2) following the estimated camera position based on the slam results, so the view should be similar to the real world view
        self.general_tab = QWidget()
        self.general_tab_layout = QGridLayout()
        self.follow_camera_checkbox = QCheckBox('Sync up SLAM Plot view and estimated camera position (does not work properly yet)')
        self.follow_camera_checkbox.setChecked(False)
        # change the number of simulation steps to be skipped before new screenshot is recorded for the SLAM
        self.skip_images_label = QLabel('Number of simulation steps to be skipped before new SLAM step:')
        self.skip_images_label_line_edit = QLineEdit(str(skip_images))
        self.skip_images_label_line_edit.setAlignment(Qt.AlignRight)
        self.skip_images_label_line_edit.textChanged.connect(self.on_skip_images_changed)
        self.skip_images = skip_images
        # set layout etc.
        self.general_tab_layout.addWidget(self.follow_camera_checkbox,0,0,1,2)
        self.general_tab_layout.addWidget(self.skip_images_label,1,0,1,1)
        self.general_tab_layout.addWidget(self.skip_images_label_line_edit,1,1)
        self.general_tab_layout.setColumnStretch(0,4)
        self.general_tab_layout.setColumnStretch(1,1)
        self.general_tab.setLayout(self.general_tab_layout)

        ### SOFA TAB
        self.sofa_tab = QWidget()
        self.sofa_tab_layout = QGridLayout()
        # change young modulus of the simulated material
        self.young_modulus_label = QLabel("Young's Modulus:")
        self.young_modulus_line_edit = QLineEdit(str(young_modulus))
        self.young_modulus_line_edit.setAlignment(Qt.AlignRight)
        self.young_modulus_line_edit.textChanged.connect(self.on_young_modulus_changed)
        self.young_modulus = young_modulus
        # change poisson ratio of the simulated material
        self.poisson_ratio_label = QLabel('Poisson Ratio:')
        self.poisson_ratio_line_edit = QLineEdit(str(poisson_ratio))
        self.poisson_ratio_line_edit.setAlignment(Qt.AlignRight)
        self.poisson_ratio_line_edit.textChanged.connect(self.on_poisson_ratio_changed)
        self.poisson_ratio = poisson_ratio
        # sofa visual flags
        self.visual_checkbox = QCheckBox('Visual')
        self.visual_checkbox.setChecked(visual_flags[0])
        self.collision_checkbox = QCheckBox('Collision')
        self.collision_checkbox.setChecked(visual_flags[1])
        self.behaviour_checkbox = QCheckBox('Behaviour')
        self.behaviour_checkbox.setChecked(visual_flags[2])
        self.force_fields_checkbox = QCheckBox('Force Fields')
        self.force_fields_checkbox.setChecked(visual_flags[3])
        # set layout etc.
        self.sofa_tab_layout.addWidget(self.young_modulus_label,0,0,1,2)
        self.sofa_tab_layout.addWidget(self.young_modulus_line_edit,0,2,1,2)
        self.sofa_tab_layout.addWidget(self.poisson_ratio_label,1,0,1,2)
        self.sofa_tab_layout.addWidget(self.poisson_ratio_line_edit,1,2,1,2)
        self.sofa_tab_layout.addWidget(self.visual_checkbox,2,0,1,1)
        self.sofa_tab_layout.addWidget(self.collision_checkbox,2,1,1,1)
        self.sofa_tab_layout.addWidget(self.behaviour_checkbox,2,2,1,1)
        self.sofa_tab_layout.addWidget(self.force_fields_checkbox,2,3,1,1)
        self.sofa_tab_layout.setColumnStretch(0,1)
        self.sofa_tab_layout.setColumnStretch(1,1)
        self.sofa_tab_layout.setColumnStretch(2,1)
        self.sofa_tab_layout.setColumnStretch(3,1)
        self.sofa_tab.setLayout(self.sofa_tab_layout)

        ### NETWORKX TAB
        self.networkx_tab = QWidget()
        self.networkx_tab_layout = QGridLayout()
        # change the number of orb keypoints to use for the networkx graph, simulation gets slow for large values
        self.n_of_keypoints_label = QLabel('Number of ORB features for graph extraction:')
        self.n_of_keypoints_line_edit = QLineEdit(str(n_of_keypoints))
        self.n_of_keypoints_line_edit.setAlignment(Qt.AlignRight)
        self.n_of_keypoints_line_edit.textChanged.connect(self.on_n_of_keypoints_changed)
        self.n_of_keypoints = n_of_keypoints
        # change the maximum distance betwenn two connected orb keypoints when extracting the graph, simulation gets slow for large values
        self.max_distance_label = QLabel('Maximum distance for connection of features:')
        self.max_distance_label_line_edit = QLineEdit(str(max_distance))
        self.max_distance_label_line_edit.setAlignment(Qt.AlignRight)
        self.max_distance_label_line_edit.textChanged.connect(self.on_max_distance_changed)
        self.max_distance = max_distance
        # set layout etc.
        self.networkx_tab_layout.addWidget(self.n_of_keypoints_label,0,0)
        self.networkx_tab_layout.addWidget(self.n_of_keypoints_line_edit,0,1)
        self.networkx_tab_layout.addWidget(self.max_distance_label,1,0)
        self.networkx_tab_layout.addWidget(self.max_distance_label_line_edit,1,1)
        self.networkx_tab_layout.setColumnStretch(0,4)
        self.networkx_tab_layout.setColumnStretch(1,1)
        self.networkx_tab.setLayout(self.networkx_tab_layout)

        # add tabs to tab-widget
        self.tab = QTabWidget()
        #tab.setTabPosition(QTabWidget.West)
        self.tab.addTab(self.general_tab,'General/SLAM')
        self.tab.addTab(self.sofa_tab,'SOFA')
        self.tab.addTab(self.networkx_tab,'NetworkX')

        # set layout for the window that contains the qtabwidget, add buttons, resize, ...
        self.main_layout = QVBoxLayout() # cannot set widget directly, so this layout just contains the QTabWidget
        self.main_layout.addWidget(self.tab)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.main_layout.addWidget(self.buttonBox)
        self.setLayout(self.main_layout)
        self.resize(640,360)
        if colortheme == 'dark':
            self.setStyleSheet(qdarkstyle.load_stylesheet(qdarkstyle.dark.palette.DarkPalette))
        else:
            self.setStyleSheet(qdarkstyle.load_stylesheet(qdarkstyle.light.palette.LightPalette))

    def get_is_following_camera(self):
        return self.follow_camera_checkbox.isChecked()

    def on_skip_images_changed(self,text):
        self.skip_images = int(float(text))

    def get_skip_images(self):
        return self.skip_images

    def on_young_modulus_changed(self,text):
        self.young_modulus = float(text)
    
    def get_young_modulus(self):
        return self.young_modulus
    
    def on_poisson_ratio_changed(self,text):
        self.poisson_ratio = float(text)
    
    def get_poisson_ratio(self):
        return self.poisson_ratio

    def get_visual_flags(self):
        return [self.visual_checkbox.isChecked(),
                 self.collision_checkbox.isChecked(), 
                 self.behaviour_checkbox.isChecked(), 
                 self.force_fields_checkbox.isChecked()]

    def on_n_of_keypoints_changed(self,text):
        self.n_of_keypoints = int(float(text)) 

    def get_n_of_keypoints(self):
        return self.n_of_keypoints
    
    def on_max_distance_changed(self,text):
        self.max_distance = int(float(text))

    def get_max_distance(self):
        return self.max_distance


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
        #self.font_size = 20
        #self.font = 'Helvetica'
        #self.background_color = 'black'
        #self.text_color = 'white'
        self.colortheme = 'dark'
        self.buttonstyle_not_clicked = 'QPushButton {color:white}'
        self.buttonstyle_clicked = 'QPushButton {color:red}'
        self.visual_flags = [True,False,False,False] # intially only show visual model
        self.n_of_keypoints = 200
        self.max_distance = 100 # in pixels
        

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
        self.is_following_camera = False # flag for the plot function, changes based on getter-function from the settings dialog

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
        print("When starting the simulation the camera follows the keypoint-navigation specified in '/trajectories/navigation/keypoints1b.txt'. After that you can move around using the w-a-s-d and arrowkeys!")

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

        # slider to adjust volume/pressure of the sofa object causing it to deform
        self.slider_frame = QFrame()
        self.slider_hbox = QVBoxLayout()
        self.slider_frame.setLayout(self.slider_hbox)
        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setRange(0.5,200)
        self.volume_slider.setValue(1)
        self.volume_slider.setFocusPolicy(Qt.NoFocus)
        self.volume_slider.setPageStep(1)
        self.volume_slider.valueChanged.connect(self.on_value_changed_slider)
        self.slider_label = QLabel()
        self.slider_label.setText('SOFA deformation')
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
        self.checkbox_layout = QVBoxLayout()
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
        self.options_layout.setStretch(0,1)
        self.options_layout.setStretch(1,1)
        self.options_layout.setStretch(2,1)
        self.options_layout.setStretch(3,2)
        self.options_layout.setStretch(4,1)
        self.options_layout.setStretch(5,2)
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
        self.view_layout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(self.view_layout)
        self.setCentralWidget(self.widget)
        #self.setCentralWidget(self.view_real)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # add the dock widgets, options on the top, plots tabified on the right
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
        # TODO add legend to plots
        
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
        print('Window size: ' + str(self.screen_width) + 'x' + str(self.screen_height))
        # self.options_frame.setFixedSize(1920,120)
        # self.options_dockWidget.setFixedSize(1920,120)
        # self.view_real.setMaximumSize(960,960)
        # self.view_real.setMinimumHeight(960)
        # self.slam_results_plot.resize(960,960)
        # self.feature_graph_window.resize(960,960)
        self.widget.setFixedSize(self.screen_width/2,self.screen_height-120)
        self.options_frame.setBaseSize(self.screen_width,120)
        self.options_dockWidget.setBaseSize(self.screen_width,120)
        #self.options_frame.setMinimumHeight(120)
        #self.options_dockWidget.setMinimumHeight(120)
        self.slam_results_plot.resize(self.screen_width/2,self.screen_height-120)
        self.feature_graph_window.resize(self.screen_width/2,self.screen_height-120)

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
            print(self.view_real.get_viewer_size())
            self.image_item.setImage(self.view_real.get_screen_shot())

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
        # open custom dialog when settings button is clicked
        settings_dialog = CustomDialog(colortheme=self.colortheme,
                                    young_modulus=self.real_world.root.ellipsoid.fem.youngModulus.value[0],
                                    poisson_ratio=self.real_world.root.ellipsoid.fem.poissonRatio.value,
                                    visual_flags=self.visual_flags,
                                    n_of_keypoints=self.n_of_keypoints,
                                    max_distance=self.max_distance,
                                    skip_images=self.mat_engine.skip_images_main)
        # if dialog is accepted (ok clicked) then get all the relevant values via getter-functions
        if settings_dialog.exec_() == QDialog.Accepted:
            self.is_following_camera = settings_dialog.get_is_following_camera()
            self.mat_engine.skip_images_main = settings_dialog.get_skip_images()
            self.real_world.root.ellipsoid.fem.youngModulus.value = [settings_dialog.get_young_modulus()]
            self.real_world.root.ellipsoid.fem.poissonRatio.value = settings_dialog.get_poisson_ratio()
            self.visual_flags = settings_dialog.get_visual_flags() # [visual, collision, behavior, forcefields]
            flags_strings = [['hideVisual','showVisual'],
                            ['hideCollisionModels','showCollisionModels'],
                            ['hideBehaviorModels','showBehaviorModels'],
                            ['hideForceFields','showForceFields']]
            flag_string = ''
            i = 0
            for flag in self.visual_flags:
                flag_string = flag_string + ' ' + flags_strings[i][int(flag==True)]
                i += 1
            self.real_world.root.VisualStyle.displayFlags=flag_string
            self.n_of_keypoints = settings_dialog.get_n_of_keypoints()
            self.max_distance = settings_dialog.get_max_distance()

    def on_value_changed_slider(self,value):
        #pressure = self.real_world.root.ellipsoid.surfaceConstraint.pressure.value
        self.real_world.root.ellipsoid.surfaceConstraint.pressure.value = value
        # probably do this for the sim as well in the future (right now only the sim that is supposed to be the real world)
    
    def extract_network(self):
        # TODO skip_counter
        nxs.draw_img_and_graph(image_item=self.image_item, 
                            image=self.view_real.get_screen_shot(), 
                            graph_item=self.graph_item, 
                            n_of_keypoints=self.n_of_keypoints,
                            max_distance=self.max_distance)

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
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.text_edit_console.setTextCursor(cursor)

