#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from qtpy.QtCore import *
from qtpy.QtWidgets import *
import matlab.engine
import numpy as np
from scipy.io import savemat
from sofaviewer.widgets.glviewer import SofaGLViewer
from sofaviewer.widgets.sim import SofaSim
import csv
import os
import math
from . import plotter


def compute_trajectory(keypoints):
    """Function to compute a trajectory out of a set of keypoints using linear interpolation

    Args:
        keypoints (list): Contains the time (step), position, and orientation of a keypoint in each row

    Returns:
        np.array: Position and orientation at each time step between t=0 and last keypoint
    """
    # get list of keytimes and corresponding positions/orientations
    # returns np.arrays of complete trajectory, connecting all keypoints and reaching them at the specified times
    key_times = np.array(keypoints)[:, 0]
    key_positions = np.array(keypoints)[:, 1:4]
    key_orientations = np.array(keypoints)[:, 4:8]
    end_time = int(key_times[-1])
    positions = np.zeros([end_time + 1, 3])
    orientations = np.zeros([end_time + 1, 4])
    for i in range(len(key_times) - 1):
        time_0 = int(key_times[i])
        time_1 = int(key_times[i + 1])
        pos_0 = key_positions[i, :]
        pos_1 = key_positions[i + 1, :]
        ori_0 = key_orientations[i, :]
        ori_1 = key_orientations[i + 1, :]
        time_n = np.arange(time_0, time_1 + 1)
        time_n = time_n.reshape([time_1 + 1 - time_0, 1])
        positions[time_0 : time_1 + 1, :] = (time_n - time_0) * (pos_1 - pos_0) / (
            time_1 - time_0
        ) + pos_0
        orientations[time_0 : time_1 + 1, :] = (time_n - time_0) * (ori_1 - ori_0) / (
            time_1 - time_0
        ) + ori_0
        orientations = orientations / np.linalg.norm(
            orientations, axis=1, keepdims=True
        )
    return positions, orientations


class EngineORB:
    """
    Class to handle the data transfer between SOFA simulation (Python) and SLAM (MATLAB)
    """
    def __init__(
        self,
        slam,
        mat_dir,
        skip_images_init=2,
        skip_images_main=0,
        mode="fromfile",
        trajectory_path="sofaviewer/trajectories/navigation/",
    ):
        """Constructor of EngineORB

        Args:
            slam (str): Switch between ORB-SLAM ("orb") and Model-based SLAM ("mob")
            mat_dir (str): Path to MATLAB SLAM root directory
            skip_images_init (int, optional): Number of simulation steps to skip between two images during the initalization phase. Defaults to 2.
            skip_images_main (int, optional): Number of simulation steps to skip between two images during the main phase. Defaults to 0.
            mode (str, optional): Navigation mode. Defaults to "fromfile".
            trajectory_path (str, optional): Path to directory to write/read trajectory. Defaults to "sofaviewer/trajectories/navigation/".
        """
        print("Starting MATLAB engine ...")
        # Start matlab engine
        self.mat = matlab.engine.start_matlab()  # "-desktop -r 'format short'"
        print("MATLAB engine started successfully!")
        # currentEngine = matlab.engine.find_matlab()
        # print(currentEngine)
        # try:
        #     self.mat = matlab.engine.connect_matlab(currentEngine[0])
        # except:
        #     print("No shared MATLAB session was found. Share by running 'matlab.engine.shareEngine' in the MATLAB command prompt.")
        # Go to slam directory
        self.mat.cd(mat_dir, nargout=0)
        self.mat_dir = mat_dir
        self.slam = slam
        self.skip_images = skip_images_init
        self.skip_images_main = skip_images_main
        self.skip_counter = skip_images_init  # start immediately
        self.is_mapping = False
        self.is_initialized = False
        self.slam_step = 0
        self.sim_step = 0
        self.positions = []
        self.orientations = []
        self.ground_truth_positions = np.zeros(shape=(100, 3))
        self.ground_truth_orientations = np.zeros(shape=(100, 4))
        self.mode = mode
        self.trajectory_path = trajectory_path
        self.navigation_path = "trajectories/navigation/"
        if mode == "fromfile":
            print("Reading camera trajectory")
            with open(
                os.path.join(self.trajectory_path, "camera_positions.txt"), "r"
            ) as f:
                reader = csv.reader(f, delimiter=" ", quoting=csv.QUOTE_NONNUMERIC)
                for row in reader:
                    self.positions.append(list(row))
            with open(
                os.path.join(self.trajectory_path, "camera_orientations.txt"), "r"
            ) as f:
                reader = csv.reader(f, delimiter=" ", quoting=csv.QUOTE_NONNUMERIC)
                for row in reader:
                    self.orientations.append(list(row))
            self.positions = np.array(self.positions)
            self.orientations = np.array(self.orientations)
            self.n_positions = self.positions.shape[0]
            self.current_line = 0
        elif mode == "tofile":
            if not os.path.exists(trajectory_path):
                os.makedirs(trajectory_path)
                print("Directory created")
            print(
                "Trajectory will be written to "
                + trajectory_path
                + " when the simulation is stopped (space pressed)"
            )
            if self.trajectory_path == self.navigation_path:
                print(
                    "Navigate to desired keypoint with arrow keys and 'wasd', then press H to add camera position to keypoint-list."
                )
                self.keypoints = []
        elif mode == "keypoint_navigation":
            print("Reading camera trajectory keypoints and -times")
            keypoints = []
            with open(self.trajectory_path, "r") as f:
                reader = csv.reader(f, delimiter=" ", quoting=csv.QUOTE_NONNUMERIC)
                for row in reader:
                    keypoints.append(list(row))
            self.positions, self.orientations = compute_trajectory(keypoints)
            self.n_positions = self.positions.shape[0]
            self.current_line = 0
        keyframes_dir = os.path.join(self.mat_dir, "keyframes")
        try:
            for f in os.listdir(keyframes_dir):
                os.remove(os.path.join(keyframes_dir, f))
        except:
            pass

    def set_viewer(self, viewer: SofaGLViewer):
        """Function to set OpenGL viewer of the SOFA simulation

        Args:
            viewer (SofaGLViewer): OpenGL viewer of the SOFA simulation
        """
        self.viewer = viewer
        self._viewer_set = True
        self.viewer.key_pressed.connect(self.keyPressEvent)
        # self.viewer.key_released.connect(self.keyReleaseEvent)

    def set_image_source(self, sim1: SofaSim):
        """Function to set the real world camera

        Args:
            sim1 (SofaSim): SOFA simulation
        """
        self.real_world = sim1
        self.camera = sim1.root.camera
        self.cam_pos = self.camera.position
        self.cam_ori = self.camera.orientation
        self._world_set = True

    def set_sim(self, sim2: SofaSim):
        """Function to set the simulated environment used for predicting the deformation

        Args:
            sim2 (SofaSim): SOFA simulation
        """
        self.sofa_sim = sim2
        self._sim_set = True

    def set_main_window(self, window: QMainWindow):
        """Function to set the main window

        Args:
            window (QMainWindow): Main window
        """
        self.main_window = window
        self._main_window_set = True

    def update_sim_step(self):
        """Function to keep track of simulation steps. Function call needed to connnect signal.
        """
        self.sim_step += 1

    def viewer_info(self, viewer_size, intrinsics):
        """Function to write information about the viewer to class variables

        Args:
            viewer_size (tuple): (width, height) of the viewer
            intrinsics (list): focal length and principal point of the viewer's camera
        """
        self.viewer_size = viewer_size
        self.intrinsics = intrinsics
        self.width = self.viewer_size[0]
        self.height = self.viewer_size[1]

    def add_pos_to_gt(self, row):
        """Function to add a camera pose (position and orientation) to ground truth list

        Args:
            row (int): Index of the pose
        """
        # add new row if predetermined size is not sufficient
        if row < self.ground_truth_positions.shape[0]:
            self.ground_truth_positions[row] = self.cam_pos.value
            self.ground_truth_orientations[row] = self.cam_ori.value
        else:
            self.ground_truth_positions = np.vstack(
                (self.ground_truth_positions, self.cam_pos.value)
            )
            self.ground_truth_orientations = np.vstack(
                (self.ground_truth_orientations, self.cam_ori.value)
            )

    def initialize_slam(self, image):
        """Function to initialize the SLAM by calling the corresponding MATLAB functions

        Args:
            image (np.array): Image of the real world
        """
        # use first image to initalize slam, then use every image to try to initialize the map
        self.slam_step += 1
        if self.slam_step == 1:
            self.add_pos_to_gt(
                0
            )  # save camera position corresponding to first initilization frame
            # set stuff for matlab: init_image, focalLength, principalPoint, viewer_size
            initdic = {
                "currI": image,
                "focalLength": np.array([self.intrinsics[0], self.intrinsics[1]]),
                "principalPoint": np.array([self.intrinsics[2], self.intrinsics[3]]),
                "viewerWidth": self.width,
                "viewerHeight": self.height,
            }
            savemat(os.path.join(self.mat_dir, "initI.mat"), initdic)
            self.mat.initialize_slam(nargout=0)
            if self.slam == "orb":
                self.mat.workspace["doProjections"] = 0
            elif self.slam == "mob":
                self.mat.workspace["doProjections"] = 1
        else:
            initdic = {"currI": image}
            savemat(os.path.join(self.mat_dir, "currI.mat"), initdic)
            self.mat.map_initialization(nargout=0)
            if self.mat.workspace["isMapInitialized"]:
                print("Map initialized")
                self.mat.initialize_slam_2(nargout=0)
                self.is_initialized = True  # call main_slam from now on
                self.skip_images = self.skip_images_main
                self.n_keyFrames = 2
                self.add_pos_to_gt(
                    self.n_keyFrames - 1
                )  # save camera position corresponding to second initilization frame
                # Initialize and plot Networkx graph
                # self.pts = nxs.initialize_network_3D(self.mat.workspace['worldpoints'])

    def main_slam(self, image):
        """Function to call the main loop of the SLAM in MATLAB

        Args:
            image (np.array): Image of the real world
        """
        self.slam_step += 1
        maindic = {"currI": image}
        savemat(os.path.join(self.mat_dir, "currI.mat"), maindic)
        sim_nodes = self.sofa_sim.root.ellipsoid.visual.VisualModel.position.value
        nodedic = {"currentNodePositions": sim_nodes}
        savemat(os.path.join(self.mat_dir, "currentNodePositions.mat"), nodedic)
        self.mat.main_loop_slam(nargout=0)
        if self.mat.workspace[
            "isKeyFrame"
        ]:  # save camera position corresponding to keyframes
            self.n_keyFrames += 1
            self.add_pos_to_gt(self.n_keyFrames - 1)
            # instead call evaluate ground truth
            self.ground_truth_positions = self.ground_truth_positions[
                : self.n_keyFrames, :
            ]
            self.ground_truth_orientations = self.ground_truth_orientations[
                : self.n_keyFrames, :
            ]
            gtdic = {
                "sofaGroundTruth_pos": self.ground_truth_positions,
                "sofaGroundTruth_ori": self.ground_truth_orientations,
            }
            savemat(os.path.join(self.mat_dir, "groundTruth/groundTruth.mat"), gtdic)
            self.mat.main_loop_slam2(nargout=0)

            # self.pts = nxs.initialize_network_3D(self.mat.workspace['worldpoints'])
            plotter.plot_slam_results(
                worldpoint_plot=self.main_window.worldpoint_plot,
                cam_pos_plot=self.main_window.cam_pos_plot,
                worldpoints=np.array(list(self.mat.workspace["worldpoints"])),
                camera_positions=np.array(list(self.mat.workspace["camera_positions"])),
                slam_results_plot=self.main_window.slam_results_plot,
                follow_camera=self.main_window.is_following_camera,
            )

    def stop_slam(self):
        """Function to call the MATLAB scripts to stop the SLAM and compare the ground truth
        """
        # save ground truth of key frames as mat-file
        self.is_mapping = False
        self.real_world.animation_end.disconnect(
            self.update_slam
        )  # set a qt signal to update slam after sim step
        self.ground_truth_positions = self.ground_truth_positions[: self.n_keyFrames, :]
        self.ground_truth_orientations = self.ground_truth_orientations[
            : self.n_keyFrames, :
        ]
        finishdic = {
            "sofaGroundTruth_pos": self.ground_truth_positions,
            "sofaGroundTruth_ori": self.ground_truth_orientations,
        }
        savemat(os.path.join(self.mat_dir, "groundTruth/groundTruth.mat"), finishdic)
        self.mat.finish_slam(nargout=0)
        plotter.plot_ground_truth(
            ground_truth_plot=self.main_window.ground_truth_plot,
            camera_positions=np.array(
                list(self.mat.workspace["sofaGroundTruth_pos_slam"])
            ),
        )
        if self.mat.workspace["rmse1"] < self.mat.workspace["rmse1"]:
            print(f'Absolute RMSE for key frame trajectory (m): {self.mat.workspace["rmse1"]}')
        else:
            print(f'Absolute RMSE for key frame trajectory (m): {self.mat.workspace["rmse2"]}')

    def start_slam(self):
        """Function to connect the end of an simulation step to a SLAM update
        """
        # print("Start SLAM")
        self.is_mapping = True
        self.real_world.animation_end.connect(
            self.update_slam
        )  # set a qt signal to update slam after sim step
        self.viewer_info(
            viewer_size=self.viewer.get_viewer_size(),
            intrinsics=self.viewer.get_intrinsic_parameters(),
        )

    def start_sim(self):
        """Function to connect the simulation start to corresponding navigation mode
        """
        self.real_world.animation_start.connect(self.update_sim_step)
        self.real_world.animation_start.connect(self.update_sim_camera)
        # self.real_world.animation_start.connect(self.viewer.paintGL)
        if self.mode == "fromfile":
            self.real_world.animation_start.connect(self.read_camera_position)
        elif self.mode == "tofile" and self.trajectory_path != self.navigation_path:
            self.real_world.animation_end.connect(self.write_camera_position)
        elif self.mode == "keypoint_navigation":
            self.real_world.animation_end.connect(self.enforce_trajectory)
            # self.real_world.animation_end.connect(self.write_camera_position)

    def stop_sim(self):
        """Function to write trajectory to file when the simulation is stopped and in "tofile" mode
        """
        if self.mode == "tofile":
            if self.trajectory_path == self.navigation_path:
                with open(
                    os.path.join(self.trajectory_path, "keypoints_new.txt"), "w"
                ) as f:
                    wr = csv.writer(f, delimiter=" ", quoting=csv.QUOTE_NONNUMERIC)
                    wr.writerows(self.keypoints)
            else:
                with open(
                    os.path.join(self.trajectory_path, "camera_positions.txt"), "w"
                ) as f:
                    wr = csv.writer(f, delimiter=" ", quoting=csv.QUOTE_NONNUMERIC)
                    wr.writerows(self.positions)
                with open(
                    os.path.join(self.trajectory_path, "camera_orientations.txt"), "w"
                ) as f:
                    wr = csv.writer(f, delimiter=" ", quoting=csv.QUOTE_NONNUMERIC)
                    wr.writerows(self.orientations)

    def read_camera_position(self):
        """Function to set the camera position to next predefined value
        """
        if self.current_line < self.n_positions:
            self.cam_pos.value = self.positions[self.current_line, :]
            self.cam_ori.value = self.orientations[self.current_line, :]
            # print(np.linalg.norm(self.orientations[self.current_line,:], keepdims=True))
            self.current_line += 1

    def enforce_trajectory(self):
        """Function to set the camera position to follow a certain trajectory (cirle) before following the trajectory of the input file
        """
        # # start with circle
        # if self.sim_step <= 50:
        #     self.cam_pos -= [0., 0.01, 0.]
        # elif self.sim_step <= 150:
        #     self.cam_pos -= [0., -0.005, 0.01]
        # elif self.sim_step <= 850:
        #     x_pos = 0.5*math.sin(2*math.pi*(self.sim_step-150)/400) * math.sin(2*math.pi*(self.sim_step-150)/2800)
        #     y_pos = -0.8*math.cos(2*math.pi*(self.sim_step-150)/400) * math.sin(2*math.pi*(self.sim_step-150)/2800)
        #     z_pos = 4 - 1.5*(self.sim_step-150)/700
        #     self.cam_pos.value = [x_pos, y_pos, z_pos]
        # # elif self.sim_step <= 1040:
        # #     self.cam_pos += [0., 0., 0.01]
        # # then follow keypoints
        # else:
        #     self.read_camera_position()

        # start with circle
        if self.sim_step <= 100:
            self.cam_pos += [0.01, 0.0, 0.0]
        elif self.sim_step <= 400:
            x_pos = math.cos(2 * math.pi * (self.sim_step - 100) / 400)
            y_pos = math.sin(2 * math.pi * (self.sim_step - 100) / 400)
            self.cam_pos.value = [x_pos, y_pos, 5.0]
        elif self.sim_step <= 500:
            self.cam_pos += [0.0, 0.01, 0.0]
        # then follow keypoints
        else:
            self.read_camera_position()

    def write_camera_position(self):
        """Function to append current camera pose to list of poses
        """
        if self.trajectory_path == self.navigation_path:
            keypoint = np.empty([1, 8])
            keypoint[0, 0] = self.sim_step
            keypoint[0, 1:4] = self.cam_pos.value
            keypoint[0, 4:8] = self.cam_ori.value
            print(keypoint[0, :])
            self.keypoints.append(list(keypoint[0, :]))
        else:
            self.positions.append(list(self.cam_pos.value))
            self.orientations.append(list(self.cam_ori.value))

    def keyPressEvent(self, QKeyEvent):
        """Function to map some keyboard inputs to actions

        Args:
            QKeyEvent: Key pressed event
        """
        if QKeyEvent.key() == Qt.Key_Space:
            # if animating
            # stop slam, if running
            # write trajectories, if in tofile-mode
            # else just stop the simulation
            if self.real_world.is_animating:
                self.stop_sim()
            # when starting the animation
            # get new position from inputfile, if in fromfile-mode
            # append position to array, if in tofile-mode (write to file at the end)
            # else use computed trajctory
            else:
                self.start_sim()

        if QKeyEvent.key() == Qt.Key_G:  # G for GO
            # start/stop slam only if animating
            if self.is_mapping:
                self.stop_slam()
            elif self.real_world.is_animating:
                self.start_slam()

        if QKeyEvent.key() == Qt.Key_F:  # F for forces
            if self.real_world.is_animating:
                print("Start Forces")
                self.real_world.root.CameraController.startForces = True
                self.sofa_sim.root.CameraController.startForces = True

        if QKeyEvent.key() == Qt.Key_K:  # F for forces
            if self.real_world.is_animating:
                print("Start Displacement")
                self.real_world.root.CameraController.displaceNode = True
                # self.real_world.root.CameraController.indices = [1]

        if QKeyEvent.key() == Qt.Key_H:
            if self.mode == "tofile" and self.trajectory_path == self.navigation_path:
                self.write_camera_position()

        if QKeyEvent.key() == Qt.Key_L:
            pressure = self.real_world.root.ellipsoid.surfaceConstraint.pressure.value
            self.real_world.root.ellipsoid.surfaceConstraint.pressure.value = (
                pressure + 1
            )
            # print(self.real_world.root.ellipsoid.cavity.surfaceConstraint.pressure)
            # print(self.real_world.root.ellipsoid.cavity.surfaceConstraint.pressure.value)

    def update_slam(self):
        """Function to update the SLAM if enough simulation steps have gone by since the last update
        """
        # at every animation_end-event, either do nothing or pass image
        # try initialization until map is initialized, then call main_slam
        if self.skip_counter == self.skip_images:
            self.skip_counter = 0
            if self.is_initialized:
                self.main_slam(image=self.viewer.get_screen_shot())
            else:
                self.initialize_slam(image=self.viewer.get_screen_shot())
        else:
            self.skip_counter += 1

    def update_sim_camera(self):
        """Function to update the pose of the camera of the simulation view. Not properly implemented at the moment.
        """
        # update the camera of the simulation real world camera position measurement
        # unnecessary atm, since simulation view is not displayed
        # self.sofa_sim.root.camera.position = self.cam_pos
        # self.sofa_sim.root.camera.orientation = self.cam_ori
        return
