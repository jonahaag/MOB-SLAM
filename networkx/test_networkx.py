#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 14:50:11 2021

@author: jona
"""
import networkx as nx
import cv2 as cv
from matplotlib import pyplot as plt

img = cv.imread('suchbild.jpeg',cv.IMREAD_GRAYSCALE)

# Initiate STAR detector
orb = cv.ORB_create(nfeatures = 50)

# compute the descriptors with ORB
kp, descriptors = orb.detectAndCompute(img, None)
# draw only keypoints location,not size and orientation
img2 = cv.drawKeypoints(img,kp,outImage=None,color=(0,255,0),flags=0)
# cv.imshow("Image", img2)
# cv.waitKey(0)
# cv.destroyAllWindows()

plt.imshow(img2)

####
G = nx.Graph()
# add all keypoints as nodes
for i in range(0,len(kp)):
    G.add_node(i,pos=kp[i].pt)
    # add edge between every node
    for j in range(0,i):
        G.add_edge(i,j)
pos=nx.get_node_attributes(G,'pos')

## draw nodes on top of image
## alternatively use image as node and draw other nodes on top
nx.draw(G,pos,node_size=10,node_color='red',edgecolors='red',edge_color='blue',width=0.1)
plt.show()


