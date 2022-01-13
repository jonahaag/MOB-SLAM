#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import networkx as nx
import cv2 as cv
import math
from . import ssc
from random import shuffle

def extract_feature_graph(img_rgb, n_of_keypoints, max_distance):
    """Function to extract ORB features from image and create a graph with those features as vertices

    Args:
        img_rgb (np.array): Image in which features should be detected
        n_of_keypoints (int): Number of features to extract
        max_distance (float): Maximum distance at which two keypoints still get connected via an edge in the graph

    Returns:
        list: detected keypoints, pixel position of detected keypoints, decriptors of the detected features, and NetworkX graph with keypoints as vertices
    """
    # convert rgb image to greyscale
    img = np.dot(img_rgb[..., :3], [0.299, 0.587, 0.114])
    img = cv.normalize(
        src=img, dst=None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U
    )

    # Initiate ORB detector
    orb = cv.ORB_create()

    # compute the descriptors with ORB
    kp, descriptors = orb.detectAndCompute(img, None)

    shuffle(kp)  # simulating sorting by score with random shuffle

    selected_keypoints = ssc.ssc(kp, n_of_keypoints, 0.01, img.shape[1], img.shape[0])

    # draw only keypoints location,not size and orientation
    pts = cv.KeyPoint_convert(selected_keypoints)
    ####
    G = nx.Graph()
    # add all keypoints as nodes
    for i in range(0, len(selected_keypoints)):
        G.add_node(i, pos=selected_keypoints[i].pt)
        # add edge between every node
        for j in range(0, i):
            if (
                math.sqrt((pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2)
                <= max_distance
            ):
                G.add_edge(i, j)

    # return keypoint positions (2D), orb descriptors, and feature graph
    return selected_keypoints, pts, descriptors, G

def draw_img_and_graph(image_item, image, graph_item, n_of_keypoints, max_distance):
    """Function to draw image and graph using pyqtgraph items

    Args:
        image_item: pyqtgraph image item
        image (np.array): RGB image
        graph_item: pyqtgraph graph item
        n_of_keypoints (int): Number of ORB features to extract from image
        max_distance (float): Maximum distance at which two keypoints still get connected via an edge in the graph
    """
    # image_item.setImage(np.dot(image[...,:3], [0.299, 0.587, 0.114]))
    image_item.setImage(image)
    kp, pts, descriptors, G = extract_feature_graph(image, n_of_keypoints, max_distance)
    edges = np.array([list(edge) for edge in nx.edges(G)])
    graph_item.setData(pos=pts, adj=edges, pxMode=True, size=7.0, brush="r", pen="y")
