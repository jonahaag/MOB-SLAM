from mayavi.tools import camera
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import networkx as nx
import numpy as np

def plot_slam_results(worldpoint_plot, cam_pos_plot, worldpoints, camera_positions):
    worldpoint_plot.setData(pos=worldpoints, color=(0.5,0.7,1.0,1.0), size=2.5, pxMode=True)
    cam_pos_plot.setData(pos=camera_positions, color=(0.8,0.4,0.8,1.0), width=10.0, antialias=True)

def plot_ground_truth(ground_truth_plot, camera_positions):
    ground_truth_plot.setData(pos=camera_positions, color=(0.0,0.8,0.2,1.0), width=10.0, antialias=True)
    
