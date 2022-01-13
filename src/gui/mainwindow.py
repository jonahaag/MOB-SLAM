from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from sofaviewer.widgets.glviewer import SofaGLViewer
from sofaviewer.widgets.sim import SofaSim
from sofaviewer.widgets.keyboardviewcontroller import QSofaViewKeyboardController
from gui.orb import EngineORB
from feature_graph import network as nxs
import os
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import sys
import qdarkstyle


class EmittingStream(QObject):
    textWritten = Signal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


class CustomDialog(QDialog):
    def __init__(
        self,
        colortheme,
        young_modulus,
        poisson_ratio,
        visual_flags,
        n_of_keypoints,
        max_distance,
        skip_images_slam,
        skip_images_network,
    ):
        super(CustomDialog, self).__init__()

        ### initialize each tab as QWidget, then add Layout and Widgets to that QWidget
        # first some general settings, so far only the option to switch between
        # 1) "fixed" view of the slam results plot and
        # 2) following the estimated camera position based on the slam results, so the view should be similar to the real world view
        self.general_tab = QWidget()
        self.general_tab_layout = QGridLayout()
        self.follow_camera_checkbox = QCheckBox(
            "Sync up SLAM Plot view and estimated camera position (does not work properly yet)"
        )
        self.follow_camera_checkbox.setChecked(False)
        # change the number of simulation steps to be skipped before new screenshot is recorded for the SLAM
        self.skip_images_slam_label = QLabel(
            "Number of simulation steps to be skipped before new SLAM step:"
        )
        self.skip_images_slam_label_line_edit = QLineEdit(str(skip_images_slam))
        self.skip_images_slam_label_line_edit.setAlignment(Qt.AlignRight)
        self.skip_images_slam_label_line_edit.textChanged.connect(
            self.on_skip_images_slam_changed
        )
        self.skip_images_slam = skip_images_slam
        # set layout etc.
        self.general_tab_layout.addWidget(self.follow_camera_checkbox, 0, 0, 1, 2)
        self.general_tab_layout.addWidget(self.skip_images_slam_label, 1, 0, 1, 1)
        self.general_tab_layout.addWidget(self.skip_images_slam_label_line_edit, 1, 1)
        self.general_tab_layout.setColumnStretch(0, 4)
        self.general_tab_layout.setColumnStretch(1, 1)
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
        self.poisson_ratio_label = QLabel("Poisson Ratio:")
        self.poisson_ratio_line_edit = QLineEdit(str(poisson_ratio))
        self.poisson_ratio_line_edit.setAlignment(Qt.AlignRight)
        self.poisson_ratio_line_edit.textChanged.connect(self.on_poisson_ratio_changed)
        self.poisson_ratio = poisson_ratio
        # sofa visual flags
        self.visual_checkbox = QCheckBox("Visual")
        self.visual_checkbox.setChecked(visual_flags[0])
        self.collision_checkbox = QCheckBox("Collision")
        self.collision_checkbox.setChecked(visual_flags[1])
        self.behaviour_checkbox = QCheckBox("Behaviour")
        self.behaviour_checkbox.setChecked(visual_flags[2])
        self.force_fields_checkbox = QCheckBox("Force Fields")
        self.force_fields_checkbox.setChecked(visual_flags[3])
        # set layout etc.
        self.sofa_tab_layout.addWidget(self.young_modulus_label, 0, 0, 1, 2)
        self.sofa_tab_layout.addWidget(self.young_modulus_line_edit, 0, 2, 1, 2)
        self.sofa_tab_layout.addWidget(self.poisson_ratio_label, 1, 0, 1, 2)
        self.sofa_tab_layout.addWidget(self.poisson_ratio_line_edit, 1, 2, 1, 2)
        self.sofa_tab_layout.addWidget(self.visual_checkbox, 2, 0, 1, 1)
        self.sofa_tab_layout.addWidget(self.collision_checkbox, 2, 1, 1, 1)
        self.sofa_tab_layout.addWidget(self.behaviour_checkbox, 2, 2, 1, 1)
        self.sofa_tab_layout.addWidget(self.force_fields_checkbox, 2, 3, 1, 1)
        self.sofa_tab_layout.setColumnStretch(0, 1)
        self.sofa_tab_layout.setColumnStretch(1, 1)
        self.sofa_tab_layout.setColumnStretch(2, 1)
        self.sofa_tab_layout.setColumnStretch(3, 1)
        self.sofa_tab.setLayout(self.sofa_tab_layout)

        ### NETWORKX TAB
        self.networkx_tab = QWidget()
        self.networkx_tab_layout = QGridLayout()
        # change the number of orb keypoints to use for the networkx graph, simulation gets slow for large values
        self.n_of_keypoints_label = QLabel(
            "Number of ORB features for graph extraction:"
        )
        self.n_of_keypoints_line_edit = QLineEdit(str(n_of_keypoints))
        self.n_of_keypoints_line_edit.setAlignment(Qt.AlignRight)
        self.n_of_keypoints_line_edit.textChanged.connect(
            self.on_n_of_keypoints_changed
        )
        self.n_of_keypoints = n_of_keypoints
        # change the maximum distance betwenn two connected orb keypoints when extracting the graph, simulation gets slow for large values
        self.max_distance_label = QLabel("Maximum distance for connection of features:")
        self.max_distance_label_line_edit = QLineEdit(str(max_distance))
        self.max_distance_label_line_edit.setAlignment(Qt.AlignRight)
        self.max_distance_label_line_edit.textChanged.connect(
            self.on_max_distance_changed
        )
        self.max_distance = max_distance
        # change the number of simulation steps to be skipped before new screenshot is recorded for the feature graph
        self.skip_images_network_label = QLabel(
            "Number of simulation steps to be skipped before new feature graph update:"
        )
        self.skip_images_network_label_line_edit = QLineEdit(str(skip_images_network))
        self.skip_images_network_label_line_edit.setAlignment(Qt.AlignRight)
        self.skip_images_network_label_line_edit.textChanged.connect(
            self.on_skip_images_network_changed
        )
        self.skip_images_network = skip_images_network
        # set layout etc.
        self.networkx_tab_layout.addWidget(self.n_of_keypoints_label, 0, 0)
        self.networkx_tab_layout.addWidget(self.n_of_keypoints_line_edit, 0, 1)
        self.networkx_tab_layout.addWidget(self.max_distance_label, 1, 0)
        self.networkx_tab_layout.addWidget(self.max_distance_label_line_edit, 1, 1)
        self.networkx_tab_layout.addWidget(self.skip_images_network_label, 2, 0, 1, 1)
        self.networkx_tab_layout.addWidget(
            self.skip_images_network_label_line_edit, 2, 1
        )
        self.networkx_tab_layout.setColumnStretch(0, 4)
        self.networkx_tab_layout.setColumnStretch(1, 1)
        self.networkx_tab.setLayout(self.networkx_tab_layout)

        # add tabs to tab-widget
        self.tab = QTabWidget()
        # tab.setTabPosition(QTabWidget.West)
        self.tab.addTab(self.general_tab, "General/SLAM")
        self.tab.addTab(self.sofa_tab, "SOFA")
        self.tab.addTab(self.networkx_tab, "NetworkX")

        # set layout for the window that contains the qtabwidget, add buttons, resize, ...
        self.main_layout = (
            QVBoxLayout()
        )  # cannot set widget directly, so this layout just contains the QTabWidget
        self.main_layout.addWidget(self.tab)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.main_layout.addWidget(self.buttonBox)
        self.setLayout(self.main_layout)
        self.resize(640, 360)
        if colortheme == "dark":
            self.setStyleSheet(
                qdarkstyle.load_stylesheet(qdarkstyle.dark.palette.DarkPalette)
            )
        else:
            self.setStyleSheet(
                qdarkstyle.load_stylesheet(qdarkstyle.light.palette.LightPalette)
            )

    def get_is_following_camera(self):
        return self.follow_camera_checkbox.isChecked()

    def on_skip_images_slam_changed(self, text):
        self.skip_images_slam = int(float(text))

    def get_skip_images_slam(self):
        return self.skip_images_slam

    def on_young_modulus_changed(self, text):
        self.young_modulus = float(text)

    def get_young_modulus(self):
        return self.young_modulus

    def on_poisson_ratio_changed(self, text):
        self.poisson_ratio = float(text)

    def get_poisson_ratio(self):
        return self.poisson_ratio

    def get_visual_flags(self):
        return [
            self.visual_checkbox.isChecked(),
            self.collision_checkbox.isChecked(),
            self.behaviour_checkbox.isChecked(),
            self.force_fields_checkbox.isChecked(),
        ]

    def on_n_of_keypoints_changed(self, text):
        self.n_of_keypoints = int(float(text))

    def get_n_of_keypoints(self):
        return self.n_of_keypoints

    def on_max_distance_changed(self, text):
        self.max_distance = int(float(text))

    def get_max_distance(self):
        return self.max_distance

    def on_skip_images_network_changed(self, text):
        self.skip_images_network = int(float(text))

    def get_skip_images_network(self):
        return self.skip_images_network


class MainWindow(QMainWindow):
    def __init__(self, mode, slam, navigation, trajectory_path):
        super(MainWindow, self).__init__()

        # class to hold the scene, simulation representing the real world
        self.real_world = SofaSim()

        # initialize the scene
        self.real_world.init_sim()

        # create an opengl view to display a node from sofa and control a camera
        self.view_real = SofaGLViewer(
            sofa_visuals_node=self.real_world.root, camera=self.real_world.root.camera
        )

        # set a qt signal to update the view after sim step
        self.real_world.animation_end.connect(self.view_real.update)

        # create instance of keyboard controller
        self.view_control = QSofaViewKeyboardController(
            translate_rate_limit=1, rotate_rate_limit=5, update_rate=20
        )
        # set the opengl view to be controlled
        self.view_control.set_viewer(self.view_real)

        # draw the scene at a constant update rate
        # this is done so the scene is drawn even if nothing is being animated
        self.view_control.start_auto_update()

        # create an opengl view to display sofa simulation for model-based slam
        # self.simWindow = SecondWindow()
        # self.sofa_sim = self.simWindow.sofa_sim
        # self.view_sim = self.simWindow.view_sim
        self.sofa_sim = SofaSim()  # class to hold the scene
        self.sofa_sim.init_sim()  # initialize the scene
        self.view_sim = SofaGLViewer(
            sofa_visuals_node=self.sofa_sim.root, camera=self.sofa_sim.root.camera
        )
        self.sofa_sim.animation_end.connect(self.view_sim.update)

        # which parts of the sofa model to display initially, here only the visual model
        self.visual_flags = [
            True,
            False,
            False,
            False,
        ]
        # number of keypoints of networkx graph
        self.n_of_keypoints = 200
        # max distance in pixels between two keypoints to be connected in networkx graph
        self.max_distance = 100

        ### maybe add sofa_view seperately once real camera_data is used
        # requires some layout redesign though
        # layout.addWidget(self.sofa_view_sim)
        # widget = QWidget()
        # widget.setLayout(layout)
        # self.setCentralWidget(widget)

        # alternative plotting library: https://github.com/marcomusy/vedo
        # add gl view widget to layout, this widget consists of...
        self.slam_results_plot = gl.GLViewWidget()
        # ...scatter plot item for worldpoints
        self.worldpoint_plot = gl.GLScatterPlotItem()
        # ...line plot items for estimated and actual camera positions
        self.cam_pos_plot = gl.GLLinePlotItem()
        self.ground_truth_plot = gl.GLLinePlotItem()
        self.axis = gl.GLAxisItem()
        self.grid = gl.GLGridItem()
        # add camera position and ground truth to results plot
        self.slam_results_plot.addItem(self.cam_pos_plot)
        self.slam_results_plot.addItem(self.ground_truth_plot)
        self.slam_results_plot.addItem(self.axis)
        self.slam_results_plot.addItem(self.grid)
        self.slam_results_plot.setBackgroundColor("#19232D")
        # distance of camera from center
        self.slam_results_plot.opts["distance"] = 3.5
        # horizontal field of view in degrees
        self.slam_results_plot.opts["fov"] = 60
        # camera's angle of elevation in degrees
        self.slam_results_plot.opts["elevation"] = -65
        # camera's azimuthal angle in degrees
        self.slam_results_plot.opts["azimuth"] = 30
        self.slam_results_plot.pan(dx=0, dy=0, dz=0.3, relative="global")
        # flag for the plot function, changes based on getter-function from the settings dialog
        # hint: do not use, very buggy
        self.is_following_camera = False

        # add graphics window to layout, this widget consists of...
        self.feature_graph_window = pg.GraphicsWindow()
        # ...viewbox, which consist of...
        self.feature_graph_viewbox = self.feature_graph_window.addViewBox()
        # invert image along the y axis, else img is upside down
        self.feature_graph_viewbox.invertY(True)
        # set major, default is column-major
        pg.setConfigOption("imageAxisOrder", "row-major")
        # ...image item to display image
        self.image_item = pg.ImageItem()
        self.feature_graph_viewbox.addItem(self.image_item)
        # ...graph item to display networkx graph
        self.graph_item = pg.GraphItem()
        self.feature_graph_viewbox.addItem(self.graph_item)
        # display graph item ontop of image
        self.graph_item.setZValue(10)
        # self.feature_graph_viewbox.setContentsMargins(0,0,0,0)
        self.skip_counter_network = 0
        self.skip_images_network = 20
        self.is_extracting_graph = True
        self.real_world.animation_end.connect(self.extract_network)

        # install the custom output stream
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

        # text edit to which the console output is redirected
        self.text_edit_console = QTextEdit()
        self.text_edit_console.setCursorWidth(0)
        self.text_edit_console.setReadOnly(True)
        # Welcome message
        print("Welcome to SLAM Dashboard!")
        print(
            "When starting the simulation the camera follows the keypoint-navigation specified in 'SofaViewer/Trajectories/navigation/keypoints1b.txt'. After that you can move around using the w-a-s-d and arrowkeys!"
        )

        # button to start/stop the simulation
        self.sim_start_button = QPushButton("Start Simulation")
        self.sim_start_button.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.sim_start_button.clicked.connect(self.on_click_button_sim_start)

        # button to start/stop slam
        self.slam_start_button = QPushButton("Start SLAM")
        self.slam_start_button.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
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
        self.volume_slider.setRange(0.5, 200)
        self.volume_slider.setValue(1)
        self.volume_slider.setFocusPolicy(Qt.NoFocus)
        self.volume_slider.setPageStep(1)
        self.volume_slider.valueChanged.connect(self.on_value_changed_slider)
        self.slider_label = QLabel()
        self.slider_label.setText("SOFA deformation")
        self.slider_label.setAlignment(Qt.AlignCenter)
        self.slider_hbox.addWidget(self.slider_label)
        self.slider_hbox.addWidget(self.volume_slider)

        # add checkboxes inside a horizontal layout
        self.networkx_checkbox = QCheckBox()
        self.networkx_checkbox.setText("Extract Networkx Graph")
        self.networkx_checkbox.setChecked(True)
        self.networkx_checkbox.stateChanged.connect(self.on_networkx_checkbox_change)
        self.colormode_checkbox = QCheckBox()
        self.colormode_checkbox.setText("Darkmode")
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
        self.options_layout.setStretch(0, 1)
        self.options_layout.setStretch(1, 1)
        self.options_layout.setStretch(2, 1)
        self.options_layout.setStretch(3, 2)
        self.options_layout.setStretch(4, 1)
        self.options_layout.setStretch(5, 2)
        self.options_frame = QFrame()
        self.options_frame.setLayout(self.options_layout)

        self.create_layout(mode=mode)

        # hint: for some weird reason this needs to be added later else python crashes on my mac (only true for GLScatterPlotItem and GLImageItem)
        self.slam_results_plot.addItem(self.worldpoint_plot)
        # add legend to plot, fails due to GLViewWidget not having 'scene' attribute
        # legend = pg.LegendItem()
        # legend.addItem(self.cam_pos_plot, "Estimated camera position")
        # legend.addItem(self.ground_truth_plot, "Ground truth")
        # legend.setParentItem(self.slam_results_plot)

        # initialize matlab engine and slam tracking/mapping of the "real" world
        current_dir = os.path.dirname(__file__)
        mat_dir = os.path.join(current_dir, "../slam/")
        self.mat_engine = EngineORB(
            slam=slam,
            mat_dir=mat_dir,
            skip_images_init=4,
            skip_images_main=10,
            mode=navigation,
            trajectory_path=trajectory_path
        )
        self.mat_engine.set_image_source(self.real_world)
        self.mat_engine.set_viewer(self.view_real)
        self.mat_engine.set_sim(self.sofa_sim)
        self.mat_engine.set_main_window(self)

    def create_layout(self, mode):
        if mode == "main":
            # add grid as main layout, stretch rows and columns
            self.main_grid = QGridLayout()
            self.main_grid.setRowStretch(0, 1)
            self.main_grid.setRowStretch(1, 5)
            self.main_grid.setRowStretch(2, 5)
            self.main_grid.setColumnStretch(0, 1)
            self.main_grid.setColumnStretch(1, 1)
            self.main_grid.addWidget(self.options_frame, 0, 0, 1, 2)
            self.main_grid.addWidget(self.view_real, 1, 0)
            self.main_grid.addWidget(self.view_sim, 2, 0)
            self.main_grid.addWidget(self.slam_results_plot, 1, 1)
            self.main_grid.addWidget(self.feature_graph_window, 2, 1)
            self.main_grid.setContentsMargins(0, 0, 0, 0)
            self.main_grid.setSpacing(1)

            # create QWidget to contain the first level grid layout, set as central widget in main window
            self.widget = QWidget()
            self.widget.setLayout(self.main_grid)
            self.setCentralWidget(self.widget)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # window settings (size, stylesheet, ...)
            self.setWindowTitle("SLAM Dashboard")
            self.colortheme = "dark"
            if self.colortheme == "dark":
                self.set_dark_theme()
            else:
                self.set_light_theme()
            self.showFullScreen()

        elif mode == "test":
            self.options_dockWidget = QDockWidget(self)
            self.options_dockWidget.setWidget(self.options_frame)
            self.options_dockWidget.setFeatures(QDockWidget.NoDockWidgetFeatures)
            self.options_dockWidget.setTitleBarWidget(QWidget(self.options_dockWidget))

            self.slam_plot_dockWidget = QDockWidget(self)
            self.slam_plot_dockWidget.setWidget(self.slam_results_plot)
            self.slam_plot_dockWidget.setWindowTitle("SLAM Results")

            self.feature_graph_dockWidget = QDockWidget(self)
            self.feature_graph_dockWidget.setWidget(self.feature_graph_window)
            self.feature_graph_dockWidget.setWindowTitle("Feature Graph Plot")

            # create QWidget to contain the first level grid layout, set as central widget in main window
            self.widget = QWidget()
            self.view_layout = QVBoxLayout()
            self.view_layout.addWidget(self.view_real)
            self.view_layout.setContentsMargins(0, 0, 0, 0)
            self.widget.setLayout(self.view_layout)
            self.setCentralWidget(self.widget)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # add the dock widgets, options on the top, plots tabified on the right
            self.addDockWidget(Qt.RightDockWidgetArea, self.slam_plot_dockWidget)
            self.addDockWidget(Qt.RightDockWidgetArea, self.feature_graph_dockWidget)
            self.tabifyDockWidget(
                self.slam_plot_dockWidget, self.feature_graph_dockWidget
            )
            self.addDockWidget(Qt.TopDockWidgetArea, self.options_dockWidget)
            self.slam_plot_dockWidget.raise_()

            # window settings (size, stylesheet, ...)
            self.setWindowTitle("SLAM Dashboard")
            self.colortheme = "dark"
            if self.colortheme == "dark":
                self.set_dark_theme()
            else:
                self.set_light_theme()
            self.showFullScreen()

            # resize widgets
            self.screen_height = self.height()
            self.screen_width = self.width()
            print(
                "Window size: " + str(self.screen_width) + "x" + str(self.screen_height)
            )
            options_height_ratio = 0.05
            self.widget.setFixedSize(
                self.screen_width / 2, self.screen_height * (1 - options_height_ratio)
            )
            self.options_frame.resize(
                self.screen_width, self.screen_height * options_height_ratio
            )
            self.options_dockWidget.resize(
                self.screen_width, self.screen_height * options_height_ratio
            )
            self.slam_results_plot.resize(
                self.screen_width / 2, self.screen_height * (1 - options_height_ratio)
            )
            self.feature_graph_window.resize(
                self.screen_width / 2, self.screen_height * (1 - options_height_ratio)
            )

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
            self.sim_start_button.setText("Start Simulation")
            self.sim_start_button.setStyleSheet(self.buttonstyle_not_clicked)
        else:
            print("Simulation started")
            self.real_world.start_sim()
            self.sofa_sim.start_sim()
            self.mat_engine.start_sim()
            self.slam_start_button.setDisabled(False)
            self.sim_start_button.setText("Stop Simulation")
            self.sim_start_button.setStyleSheet(self.buttonstyle_clicked)

    def on_click_button_slam_start(self):
        if self.mat_engine.is_mapping:
            print("SLAM stopped")
            self.mat_engine.stop_slam()
            self.slam_start_button.setText("Start SLAM")
            self.slam_start_button.setStyleSheet(self.buttonstyle_not_clicked)
        else:
            print("SLAM started")
            self.mat_engine.start_slam()
            self.slam_start_button.setText("Stop SLAM")
            self.slam_start_button.setStyleSheet(self.buttonstyle_clicked)

    def on_click_button_settings(self):
        # open custom dialog when settings button is clicked
        settings_dialog = CustomDialog(
            colortheme=self.colortheme,
            young_modulus=self.real_world.root.ellipsoid.fem.youngModulus.value[0],
            poisson_ratio=self.real_world.root.ellipsoid.fem.poissonRatio.value,
            visual_flags=self.visual_flags,
            n_of_keypoints=self.n_of_keypoints,
            max_distance=self.max_distance,
            skip_images_slam=self.mat_engine.skip_images,
            skip_images_network=self.skip_images_network,
        )
        # if dialog is accepted (ok clicked) then get all the relevant values via getter-functions
        if settings_dialog.exec_() == QDialog.Accepted:
            self.is_following_camera = settings_dialog.get_is_following_camera()
            self.mat_engine.skip_images = settings_dialog.get_skip_images_slam()
            self.real_world.root.ellipsoid.fem.youngModulus.value = [
                settings_dialog.get_young_modulus()
            ]
            self.real_world.root.ellipsoid.fem.poissonRatio.value = (
                settings_dialog.get_poisson_ratio()
            )
            self.visual_flags = (
                settings_dialog.get_visual_flags()
            )  # [visual, collision, behavior, forcefields]
            flags_strings = [
                ["hideVisual", "showVisual"],
                ["hideCollisionModels", "showCollisionModels"],
                ["hideBehaviorModels", "showBehaviorModels"],
                ["hideForceFields", "showForceFields"],
            ]
            flag_string = ""
            i = 0
            for flag in self.visual_flags:
                flag_string = flag_string + " " + flags_strings[i][int(flag == True)]
                i += 1
            self.real_world.root.VisualStyle.displayFlags = flag_string
            self.n_of_keypoints = settings_dialog.get_n_of_keypoints()
            self.max_distance = settings_dialog.get_max_distance()
            self.skip_images_network = settings_dialog.get_skip_images_network()

    def on_value_changed_slider(self, value):
        # pressure = self.real_world.root.ellipsoid.surfaceConstraint.pressure.value
        self.real_world.root.ellipsoid.surfaceConstraint.pressure.value = value
        # probably do this for the sim as well in the future (right now only the sim that is supposed to be the real world)

    def extract_network(self):
        if self.skip_counter_network == self.skip_images_network:
            self.skip_counter_network = 0
            nxs.draw_img_and_graph(
                image_item=self.image_item,
                image=self.view_real.get_screen_shot(),
                graph_item=self.graph_item,
                n_of_keypoints=self.n_of_keypoints,
                max_distance=self.max_distance,
            )
        else:
            self.skip_counter_network += 1

    def on_networkx_checkbox_change(self):
        if self.is_extracting_graph:
            self.real_world.animation_end.disconnect(self.extract_network)
        else:
            self.real_world.animation_end.connect(self.extract_network)
        self.is_extracting_graph = not self.is_extracting_graph

    def on_colormode_checkbox_change(self):
        if self.colortheme == "dark":
            self.colortheme = "light"
            self.set_light_theme()
        else:
            self.colortheme = "dark"
            self.set_dark_theme()

    def set_light_theme(self):
        self.setStyleSheet(
            qdarkstyle.load_stylesheet(qdarkstyle.light.palette.LightPalette)
        )
        self.feature_graph_window.setBackground("#CED1D4")
        self.slam_results_plot.setBackgroundColor("#CED1D4")
        self.view_real.set_background_color([206 / 255, 209 / 255, 212 / 255, 1])
        self.view_sim.set_background_color([206 / 255, 209 / 255, 212 / 255, 1])
        self.buttonstyle_not_clicked = "QPushButton {color:#19232D}"
        self.buttonstyle_clicked = "QPushButton {color:red}"
        self.text_edit_console.setStyleSheet(
            "QTextEdit {background-color:white; color:#19232D}"
        )

    def set_dark_theme(self):
        self.setStyleSheet(
            qdarkstyle.load_stylesheet(qdarkstyle.dark.palette.DarkPalette)
        )
        self.feature_graph_window.setBackground("#37414F")
        self.slam_results_plot.setBackgroundColor("#37414F")
        self.view_real.set_background_color([55 / 255, 65 / 255, 79 / 255, 1])
        self.view_sim.set_background_color([55 / 255, 65 / 255, 79 / 255, 1])
        self.buttonstyle_not_clicked = "QPushButton {color:white}"
        self.buttonstyle_clicked = "QPushButton {color:red}"
        self.text_edit_console.setStyleSheet(
            "QTextEdit {background-color:#19232D; color:white}"
        )

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
