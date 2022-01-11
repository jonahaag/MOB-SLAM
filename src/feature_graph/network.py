#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 27 10:19:20 2021

@author: jona
"""
import numpy as np
import networkx as nx
import cv2 as cv
import math
from . import ssc
from random import shuffle

def extract_feature_graph(img_rgb, n_of_keypoints, max_distance):
    # convert rgb image to greyscale
    img = np.dot(img_rgb[...,:3], [0.299, 0.587, 0.114])
    img = cv.normalize(src=img, dst=None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)
    
    # Initiate ORB detector
    orb = cv.ORB_create()
    
    # compute the descriptors with ORB
    kp, descriptors = orb.detectAndCompute(img, None)

    shuffle(kp)  # simulating sorting by score with random shuffle

    selected_keypoints = ssc.ssc(
        kp, n_of_keypoints, 0.01, img.shape[1], img.shape[0]
    )

    # draw only keypoints location,not size and orientation
    pts = cv.KeyPoint_convert(selected_keypoints)
    ####
    G = nx.Graph()
    # add all keypoints as nodes
    for i in range(0,len(selected_keypoints)):
        G.add_node(i,pos=selected_keypoints[i].pt)
        # add edge between every node
        for j in range(0,i):
            if math.sqrt((pts[i][0]-pts[j][0])**2+(pts[i][1]-pts[j][1])**2) <= max_distance:
                G.add_edge(i,j)
    
    # return keypoint positions (2D), orb descriptors, and feature graph
    return selected_keypoints, pts, descriptors, G

def draw_img_and_graph(image_item, image, graph_item, n_of_keypoints, max_distance):
    #image_item.setImage(np.dot(image[...,:3], [0.299, 0.587, 0.114]))
    image_item.setImage(image)
    kp, pts, descriptors, G = extract_feature_graph(image, n_of_keypoints, max_distance)
    edges = np.array([list(edge) for edge in nx.edges(G)])
    graph_item.setData(pos=pts,adj=edges,pxMode=True,size=7.0,brush='r',pen='y')

# def plot_feature_graph_onto_image(img, kp, G):
#     img_with_kp = cv.drawKeypoints(img,kp,outImage=None,color=(0,255,0),flags=0)
#     # cv.imshow("Image", img2)
#     # cv.waitKey(0)
#     # cv.destroyAllWindows()
#     plt.imshow(img_with_kp)

#     ## draw nodes on top of image
#     ## alternatively use image as node and draw other nodes on top
#     pos=nx.get_node_attributes(G,'pos')
#     nx.draw(G,pos,node_size=10,node_color='red',edgecolors='red',edge_color='blue',width=0.1)
#     plt.show()

# def initialize_network_3D(worldpoints):
    # # input: matched features (and their position) within those images, corresponding 3D worldpoints
    # # output: network of 3D points, edges between all points since they all have been detected in both images
    # begin_time = datetime.datetime.now()
    # G = nx.Graph()
    # # add all keypoints as nodes
    # for i in range(0,len(worldpoints)):
    #     G.add_node(i,pos=list(worldpoints[i][:]))
    #     # add edge between every node
    #     for j in range(0,i):
    #         if math.sqrt((worldpoints[i][0]-worldpoints[j][0])**2+(worldpoints[i][1]-worldpoints[j][1])**2+(worldpoints[i][2]-worldpoints[j][2])**2) <= 0.08: # only add edge if distance between keypoints <= 500
    #             G.add_edge(i,j)
                
    # print(datetime.datetime.now() - begin_time)            
    # ##### complete graph
    # # worldpoints = list(worldpoints)
    # # G = nx.complete_graph(len(worldpoints))
    # # dictOfPoints = { i : worldpoints[i] for i in range(0, len(worldpoints) ) }
    # # nx.set_node_attributes(G,dictOfPoints,'pos')
    
    # # plot network
    # # plot_network_3D(G,0)
    # pts = alternative_plot_network_3D(G)
    # return pts
    
#def update_network_3D():
    # update position of exisiting nodes
    # delete old nodes
    # add new nodes and edges
    
    return 0

#def plot_network_3D(G, angle):

    # # Get node positions
    # pos = nx.get_node_attributes(G, 'pos')
    
    # # Get number of nodes
    # n = G.number_of_nodes()

    # # Get the maximum number of edges adjacent to a single node
    # edge_max = max([G.degree(i) for i in range(n)])

    # # Define color range proportional to number of edges adjacent to a single node
    # colors = [plt.cm.plasma(G.degree(i)/edge_max) for i in range(n)] 

    # # 3D network plot
    # with plt.style.context(('ggplot')):
        
    #     fig = plt.figure(figsize=(10,7))
    #     ax = Axes3D(fig)
        
    #     # Loop on the pos dictionary to extract the x,y,z coordinates of each node
    #     for key, value in pos.items():
    #         xi = value[0]
    #         yi = value[1]
    #         zi = value[2]
            
    #         # Scatter plot
    #         ax.scatter(xi, yi, zi, color=colors[key], s=10, edgecolors='k', alpha=0.7)
        
    #     # Loop on the list of edges to get the x,y,z, coordinates of the connected nodes
    #     # Those two points are the extrema of the line to be plotted
    #     for i,j in enumerate(G.edges()):

    #         x = np.array((pos[j[0]][0], pos[j[1]][0]))
    #         y = np.array((pos[j[0]][1], pos[j[1]][1]))
    #         z = np.array((pos[j[0]][2], pos[j[1]][2]))
        
    #     # Plot the connecting lines
    #         ax.plot(x, y, z, color='black', alpha=0.5)
    
    # # Set the initial view
    # ax.view_init(30, angle)

    # # Hide the axes
    # ax.set_axis_off()

    # plt.show()

        
##########################################
# import matlab.engine
# import sys
# import os
# sys.path.append(os.path.abspath("/Users/jona/Documents/Uni/HIWI/SLAM/SLAM/Model_based_SLAM/qt_sofa/Widgets"))
# import NetworkSLAM as nxs
# currentEngine = matlab.engine.find_matlab() 
# mat = matlab.engine.connect_matlab(currentEngine[0])

# nxs.initialize_network_3D(mat.workspace['worldpoints'])