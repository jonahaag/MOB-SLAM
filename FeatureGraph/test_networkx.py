#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 14:50:11 2021

@author: jona
"""
# import networkx as nx
# import cv2 as cv
# from matplotlib import pyplot as plt
# import numpy as np
# import math
# from scipy.spatial.distance import euclidean

# img = cv.imread('suchbild.jpeg',cv.IMREAD_GRAYSCALE)
# img_rgb = cv.imread('suchbild.jpeg')
# img2 = np.dot(img_rgb[...,:3], [0.299, 0.587, 0.114])
# img2 = cv.normalize(src=img2, dst=None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)

# # Initiate STAR detector
# orb = cv.ORB_create(nfeatures = 50)

# # compute the descriptors with ORB
# kp, descriptors = orb.detectAndCompute(img2, None)
# # draw only keypoints location,not size and orientation
# img_with_kp = cv.drawKeypoints(img2,kp,outImage=None,color=(0,255,0),flags=0)
# # cv.imshow("Image", img2)
# # cv.waitKey(0)
# # cv.destroyAllWindows()

# plt.imshow(img_with_kp)

# ####
# G = nx.Graph()
# # positions = np.zeros(len(kp))
# # add all keypoints as nodes
# for i in range(0,len(kp)):
#     G.add_node(i,pos=kp[i].pt)
#     # positions[i,:] = kp[i].pt
#     # add edge between every node
#     for j in range(0,i):
#         if math.sqrt((kp[i].pt[0]-kp[j].pt[0])**2+(kp[i].pt[1]-kp[j].pt[1])**2) <= 500: # only add edge if distance between keypoints <= 500
#             G.add_edge(i,j)
# # add edge to 10 closest keypoints
# # for i in range(0,len(kp)):
# #     min(positions, key=lambda c : distance.euclidean(c, kp[i].pt)) 

# pos=nx.get_node_attributes(G,'pos')


# ## draw nodes on top of image
# ## alternatively use image as node and draw other nodes on top
# nx.draw(G,pos,node_size=10,node_color='red',edgecolors='red',edge_color='blue',width=0.1)
# plt.show()


