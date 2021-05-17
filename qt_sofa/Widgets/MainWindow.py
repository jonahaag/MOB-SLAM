from qtpy.QtCore import *
from qtpy.QtWidgets import *
from .SofaGLViewer import SofaGLViewer
from .SofaSim import SofaSim
from .QXBoxViewController import QXBoxViewController
from .QSofaViewKeyboardController import QSofaViewKeyboardController
from .engineORB import EngineORB
import os

class SecondWindow(QMainWindow):
    def __init__(self):
        super(SecondWindow, self).__init__()
        self.sofa_sim = SofaSim()  # class to hold the scene
        self.sofa_sim.init_sim()  # initialize the scene
        self.view_sim = SofaGLViewer(sofa_visuals_node=self.sofa_sim.root, camera=self.sofa_sim.root.camera)
        # self.setCentralWidget(self.view_sim)
        # self.setWindowTitle("Simulated scene")
        
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.real_world = SofaSim()  # class to hold the scene, simulation representing the real world
        self.real_world.init_sim()  # initialize the scene

        # create an opengl view to display a node from sofa and control a camera
        self.view_real = SofaGLViewer(sofa_visuals_node=self.real_world.root, camera=self.real_world.root.camera)

        # set the view to be the main widget of the window. In the future, this should be done in a layout
        self.setCentralWidget(self.view_real)
        self.setWindowTitle("'Real world' view")

        self.real_world.animation_end.connect(self.view_real.update)  # set a qt signal to update the view after sim step

        # Add a class to control a view's camera using an xbox controller
        # self.view_control = QXBoxViewController(dead_zone=0.3, translate_rate_limit=1.5, rotate_rate_limit=20)
        # self.view_control.set_viewer(self.sofa_view)  # set the active view to control
        self.view_control = QSofaViewKeyboardController(translate_rate_limit=1, rotate_rate_limit=5, update_rate=20)
        self.view_control.set_viewers(self.view_real)

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
        
        # TODO add plots to Window, in a layout
        # layout = QHBoxLayout()
        # layout.addWidget(self.sofa_view_real)
        # layout.addWidget(self.sofa_view_sim)
        # widget = QWidget()
        # widget.setLayout(layout)
        # self.setCentralWidget(widget)
        
        # initialize matlab engine and slam tracking/mapping the real world
        current_dir = os.path.dirname(__file__)
        mat_dir = os.path.join(current_dir,"../../matlab_slam/")
        self.mat_engine = EngineORB(mat_dir=mat_dir,
                                    skip_images_init=4, 
                                    skip_images_main=2, 
                                    mode="keypoint_navigation", #tofile, fromfile, keypoint_navigation 
                                    trajectory_path="./trajectories/navigation/")
        self.mat_engine.set_image_source(self.real_world)
        self.mat_engine.set_viewer(self.view_real)
        self.mat_engine.set_sim(self.sofa_sim)
        

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Space:
            if self.real_world.is_animating:
                self.real_world.stop_sim()
                self.sofa_sim.stop_sim()
            else:
                print("Start simulation")
                self.real_world.start_sim()
                self.sofa_sim.start_sim()
                

    

                

                