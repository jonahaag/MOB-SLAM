#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 11:55:53 2021

@author: jona
"""
from qtpy.QtCore import *
from qtpy.QtWidgets import *
import matlab.engine
import numpy as np
from scipy.io import savemat
from .SofaGLViewer import SofaGLViewer
from .SofaSim import SofaSim
import csv
import os
import math


def compute_trajectory(keypoints):
    # get list of keytimes and corresponding positions/orientations
    # returns np.arrays of complete trajectory, connecting all keypoints and reaching them at the specified times
    key_times = np.array(keypoints)[:,0]
    key_positions = np.array(keypoints)[:,1:4]
    key_orientations = np.array(keypoints)[:,4:8]
    end_time = int(key_times[-1])
    positions = np.zeros([end_time+1,3])
    orientations = np.zeros([end_time+1,4])
    for i in range(len(key_times)-1):
        time_0 = int(key_times[i])
        time_1 = int(key_times[i+1])
        pos_0 = key_positions[i,:]
        pos_1 = key_positions[i+1,:]
        ori_0 = key_orientations[i,:]
        ori_1 = key_orientations[i+1,:]
        time_n = np.arange(time_0, time_1+1)
        time_n = time_n.reshape([time_1+1-time_0,1])
        positions[time_0:time_1+1,:] = (time_n-time_0) * (pos_1-pos_0)/(time_1-time_0) + pos_0
        orientations[time_0:time_1+1,:] = (time_n-time_0) * (ori_1-ori_0)/(time_1-time_0) + ori_0
        orientations = orientations / np.linalg.norm(orientations, axis=1, keepdims=True) 
    return positions, orientations


class EngineORB:
   
    def __init__(self, mat_dir, skip_images_init=2, skip_images_main=0, mode="fromfile", trajectory_path="./trajectories/test/"):   
        # print("starting matlab engine ...")
        # # Start matlab engine
        # self.mat = matlab.engine.start_matlab() #"-desktop -r 'format short'"
        # print("started successfully")
        currentEngine = matlab.engine.find_matlab()
        self.mat = matlab.engine.connect_matlab(currentEngine[0]) # share by running "matlab.engine.shareEngine" in matlab command prompt
        # Go to slam directory
        self.mat.cd(mat_dir, nargout=0)
        self.mat_dir = mat_dir
        self.skip_images = skip_images_init
        self.skip_images_main = skip_images_main
        self.skip_counter = skip_images_init #start immediately
        self.is_mapping = False
        self.is_initialized = False
        self.slam_step = 0
        self.sim_step = 0
        self.positions = []
        self.orientations = []
        self.ground_truth_positions = np.zeros(shape=(100,3))
        self.ground_truth_orientations = np.zeros(shape=(100,4))
        self.mode = mode
        self.trajectory_path = trajectory_path
        if mode == "fromfile":
            print("Reading camera trajectory")
            with open(os.path.join(self.trajectory_path,"camera_positions.txt"), 'r') as f:
                reader = csv.reader(f, delimiter=" ", quoting=csv.QUOTE_NONNUMERIC)
                for row in reader:
                    self.positions.append(list(row))
            with open(os.path.join(self.trajectory_path,"camera_orientations.txt"), 'r') as f:
                reader = csv.reader(f, delimiter=" ", quoting=csv.QUOTE_NONNUMERIC)
                for row in reader:
                    self.orientations.append(list(row))
            #TODO funktioniert auch ohne np.array???
            self.positions = np.array(self.positions)
            self.orientations = np.array(self.orientations)
            self.n_positions = self.positions.shape[0]
            self.current_line = 0
        elif mode == "tofile":
            if not os.path.exists(trajectory_path):
                os.makedirs(trajectory_path)
                print("Directory created")
            print("Trajectory will be written to " + trajectory_path + " when the simulation is stopped (space pressed)")
            if self.trajectory_path == "./trajectories/navigation/":
                print("Navigate to desired keypoint with arrow keys and 'wasd', then press H to add camera position to keypoint-list.")
                self.keypoints = []
        elif mode == "keypoint_navigation":
            print("Reading camera trajectory keypoints and -times")
            keypoints = []
            with open(os.path.join("./trajectories/navigation/keypoints1b.txt"), 'r') as f:
                reader = csv.reader(f, delimiter=" ", quoting=csv.QUOTE_NONNUMERIC)
                for row in reader:
                    keypoints.append(list(row))
            self.positions, self.orientations = compute_trajectory(keypoints)
            self.n_positions = self.positions.shape[0]
            self.current_line = 0
        keyframes_dir = os.path.join(self.mat_dir,"keyframes")
        for f in os.listdir(keyframes_dir):
            os.remove(os.path.join(keyframes_dir, f))
            
    def set_viewer(self, viewer: SofaGLViewer):
        self.viewer = viewer
        self._viewer_set = True
        # try:
        #     self._update_timer.disconnect()
        # except TypeError:
        #     pass
        # self._update_timer.timeout.connect(self.viewer.update)
        self.viewer.key_pressed.connect(self.keyPressEvent)
        # self.viewer.key_released.connect(self.keyReleaseEvent)
        
    def set_image_source(self, sim1: SofaSim):
        self.real_world = sim1
        self.camera = sim1.root.camera
        self.cam_pos = self.camera.position
        self.cam_ori = self.camera.orientation
        self._world_set = True
    
    def set_sim(self, sim2: SofaSim):
        self.sofa_sim = sim2
        self._sim_set = True
        
    def update_sim_step(self):
        #keep track of number of simulation steps
        self.sim_step += 1

    def viewer_info(self, viewer_size, intrinsics):
        self.viewer_size = viewer_size
        self.intrinsics = intrinsics
        self.width = self.viewer_size[0]
        self.height = self.viewer_size[1]
    
    def add_pos_to_gt(self, row):
        # add new row if predetermined size is not sufficient
        if row < self.ground_truth_positions.shape[0]:
            self.ground_truth_positions[row] = self.cam_pos.value
            self.ground_truth_orientations[row] = self.cam_ori.value
        else:
            self.ground_truth_positions = np.vstack((self.ground_truth_positions,self.cam_pos.value))
            self.ground_truth_orientations = np.vstack((self.ground_truth_orientations,self.cam_ori.value))
    
    def initialize_slam(self, image):
        # use first image to initalize slam, then use every image to try to initialize the map
        self.slam_step += 1
        if self.slam_step == 1:
            self.add_pos_to_gt(0) # save camera position corresponding to first initilization frame
            # set stuff for matlab: init_image, focalLength, principalPoint, viewer_size
            initdic = {"currI": image,
                    "focalLength": np.array([self.intrinsics[0],self.intrinsics[1]]),
                    "principalPoint": np.array([self.intrinsics[2],self.intrinsics[3]]),
                    "viewerWidth": self.width,
                    "viewerHeight": self.height}
            savemat(os.path.join(self.mat_dir,"initI.mat"), initdic)
            self.mat.initialize_slam(nargout=0)
        else:
            initdic = {"currI": image}
            savemat(os.path.join(self.mat_dir,"currI.mat"), initdic)
            self.mat.map_initialization(nargout=0)
            if self.mat.workspace["isMapInitialized"]:
                print("Map initialized")
                self.mat.initialize_slam_2(nargout=0)
                self.is_initialized = True # call main_slam from now on
                self.skip_images = self.skip_images_main
                self.n_keyFrames = 2
                self.add_pos_to_gt(self.n_keyFrames-1) # save camera position corresponding to second initilization frame
            
                
    def main_slam(self, image):
        self.slam_step += 1
        maindic = {"currI": image}
        savemat(os.path.join(self.mat_dir,"currI.mat"), maindic)
        sim_nodes = self.sofa_sim.root.ellipsoid.visual.VisualModel.position.value
        nodedic = {"currentNodePositions": sim_nodes}
        savemat(os.path.join(self.mat_dir,"currentNodePositions.mat"), nodedic)
        self.mat.main_loop_slam(nargout=0)
        if self.mat.workspace['isKeyFrame']: # save camera position corresponding to keyframes
            self.n_keyFrames += 1
            self.add_pos_to_gt(self.n_keyFrames-1)
            # instead call evaluate ground truth
            self.ground_truth_positions = self.ground_truth_positions[:self.n_keyFrames,:]
            self.ground_truth_orientations = self.ground_truth_orientations[:self.n_keyFrames,:]
            gtdic = {"sofaGroundTruth_pos": self.ground_truth_positions,
                     "sofaGroundTruth_ori": self.ground_truth_orientations}
            savemat(os.path.join(self.mat_dir,"groundTruth/groundTruth.mat"), gtdic)
            self.mat.main_loop_slam2(nargout=0)
            # min_n = 5
            # if self.n_keyFrames == min_n: 
            #     self.mat.scale_map_and_initialize_projection(nargout=0)
            # elif self.n_keyFrames >= min_n+1:
            #     # projection stuff
            #     # self.map_prediction() # first forward predict previsouly projected points
            #     self.mat.project_map_points(nargout=0) # then project new points
            
        
        
    def stop_slam(self):
        # save ground truth of key frames as mat-file
        self.is_mapping = False
        self.ground_truth_positions = self.ground_truth_positions[:self.n_keyFrames,:]
        self.ground_truth_orientations = self.ground_truth_orientations[:self.n_keyFrames,:]
        finishdic = {"sofaGroundTruth_pos": self.ground_truth_positions,
                     "sofaGroundTruth_ori": self.ground_truth_orientations}
        savemat(os.path.join(self.mat_dir,"groundTruth/groundTruth.mat"), finishdic)
        self.mat.finish_slam(nargout=0)
        
    def read_camera_position(self):
        if self.current_line < self.n_positions:
            self.cam_pos.value = self.positions[self.current_line,:]
            self.cam_ori.value = self.orientations[self.current_line,:]
            # print(np.linalg.norm(self.orientations[self.current_line,:], keepdims=True))
            self.current_line += 1
    
    def enforce_trajectory(self):
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
            self.cam_pos += [0.01, 0., 0.]
        elif self.sim_step <= 400:
            x_pos = math.cos(2*math.pi*(self.sim_step-100)/400)
            y_pos = math.sin(2*math.pi*(self.sim_step-100)/400)
            self.cam_pos.value = [x_pos, y_pos, 5.0]
        elif self.sim_step <= 500:
            self.cam_pos += [0., 0.01, 0.]
        # then follow keypoints
        else:
            self.read_camera_position()

    def write_camera_position(self):
        if self.trajectory_path == "./trajectories/navigation/":
            keypoint = np.empty([1,8])
            keypoint[0,0] = self.sim_step
            keypoint[0,1:4] = self.cam_pos.value
            keypoint[0,4:8] = self.cam_ori.value
            print(keypoint[0,:])
            self.keypoints.append(list(keypoint[0,:]))
        else: 
            self.positions.append(list(self.cam_pos.value))
            self.orientations.append(list(self.cam_ori.value))
        
            
            
    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Space:
            # if animating
            # stop slam, if running
            # write trajectories, if in tofile-mode
            # else just stop the simulation 
            if self.real_world.is_animating:
                if self.is_mapping: 
                    self.stop_slam()
                if self.mode == "tofile":
                    if self.trajectory_path == "./trajectories/navigation/":
                        with open(os.path.join(self.trajectory_path,"keypoints3.txt"),"w") as f:
                            wr = csv.writer(f,delimiter=" ",quoting=csv.QUOTE_NONNUMERIC)
                            wr.writerows(self.keypoints)
                    else:
                        with open(os.path.join(self.trajectory_path,"camera_positions.txt"),"w") as f:
                            wr = csv.writer(f,delimiter=" ",quoting=csv.QUOTE_NONNUMERIC)
                            wr.writerows(self.positions)
                        with open(os.path.join(self.trajectory_path,"camera_orientations.txt"),"w") as f:
                            wr = csv.writer(f,delimiter=" ",quoting=csv.QUOTE_NONNUMERIC)
                            wr.writerows(self.orientations)
            # when starting the animation
            # get new position from inputfile, if in fromfile-mode
            # append position to array, if in tofile-mode (write to file at the end)
            # else use computed trajctory
            else:
                self.real_world.animation_start.connect(self.update_sim_step)
                self.real_world.animation_start.connect(self.update_sim_camera)
                # self.real_world.animation_start.connect(self.viewer.paintGL)
                if self.mode == "fromfile":
                    self.real_world.animation_start.connect(self.read_camera_position)
                elif self.mode == "tofile" and self.trajectory_path != "./trajectories/navigation/":
                    self.real_world.animation_end.connect(self.write_camera_position)
                elif self.mode == "keypoint_navigation":
                    self.real_world.animation_end.connect(self.enforce_trajectory)
                    # self.real_world.animation_end.connect(self.write_camera_position)
                
        if QKeyEvent.key() == Qt.Key_G: # G for GO
            # start/stop slam only if animating
            if self.is_mapping:
                self.stop_slam()
            elif self.real_world.is_animating:
                print("Start SLAM")
                self.is_mapping = True
                self.real_world.animation_end.connect(self.update_slam) # set a qt signal to update slam after sim step
                self.viewer_info(viewer_size=self.viewer.get_viewer_size(), intrinsics=self.viewer.get_intrinsic_parameters())
                
        if QKeyEvent.key() == Qt.Key_F: # F for forces
            if self.real_world.is_animating:
                print("Start Forces")   
                self.real_world.root.CameraController.startForces = True
                self.sofa_sim.root.CameraController.startForces = True
                
        if QKeyEvent.key() == Qt.Key_K: # F for forces
            if self.real_world.is_animating:
                print("Start Forces")   
                if self.real_world.root.CameraController.immediateForce1: 
                    self.real_world.root.CameraController.immediateForce1 = False
                    self.sofa_sim.root.CameraController.immediateForce1 = False
                    self.real_world.root.CameraController.immediateForce2 = True
                    self.sofa_sim.root.CameraController.immediateForce2 = True
                else:
                    self.real_world.root.CameraController.immediateForce1 = True
                    self.sofa_sim.root.CameraController.immediateForce1 = True
                    self.real_world.root.CameraController.immediateForce2 = False
                    self.sofa_sim.root.CameraController.immediateForce2 = False
                
        if QKeyEvent.key() == Qt.Key_H:
            if self.mode == "tofile" and self.trajectory_path == "./trajectories/navigation/":
                self.write_camera_position()
    
    def update_slam(self):
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
            
            
    def map_prediction(self):
        # input: slam_map, forces/simulation nodes
        # projects new map points onto geometry
        # updates position of previously-projected points based on simulated deformation
        # output: new slam map
        # just call matlab scripts as a start
        sim_nodes = self.sofa_sim.root.ellipsoid.visual.VisualModel.position.value
        # real_nodes = self.real_world.root.ellipsoid.visual.VisualModel.position.value
        # diff = sim_nodes - real_nodes 
        # print(np.linalg.norm(diff, axis=0, keepdims=True))
        nodedic = {"currentNodePositions": sim_nodes}
        savemat(os.path.join(self.mat_dir,"currentNodePositions.mat"), nodedic)
        self.mat.forward_predict_map_points(nargout=0)
        
    def update_sim_camera(self): 
        # update the camera of the simulation based on current Slam results (estimated camera pose)
        # option 2: use real world camera position measurement instead (avoid backwards transformation of slam data/coordinates)
        # do only when keyframe is detected?
        self.sofa_sim.root.camera.position = self.cam_pos
        self.sofa_sim.root.camera.orientation = self.cam_ori
