# Feature Graph

## Feature matching basics

A big challenge of operating in deformable environments is the compromising of feature matching, which is a important part of the standard SLAM processing.
Feature matching refers to the act of finding the same features across a series of images such that in later steps the scene can be reconstructed based on the overlap between multiple images using triangulation.
Typically, performance as well as precision of the entire algorithm relies heavily on the accuracy of the matching.

## Problems in deformable enviroments

In the presence of deformations, finding suitable matches betwenn the set of detected features usually is hard due to two main reasons:
1. Changes in the relative position of the features. This might not be too big of an issue for the matching itself, but definitely can lead to errors when trying to find the proper alignment of the images based on those matches.
1. Visual appearance of the features might change between recordings.

## Concept of graph-based feature matching

One way to deal with this is to use a graph-based approaches.
The main idea here is to create a graph using the features as vertices and defining the edges e.g. based on some visual markers.
This allows for the additional definition of constraints regardings the edge and vertex positions and connections and can therefore increse robustness and performance of the feature matching in challenging scenarios.

## Contents

However, implementing this completely was out of scope for this project, which is why only the basics of creating a feature graph are considered here.
For this, ORB features are detected in the current image and used as vertices for the graph.
Then, each vertex is connected to all other vertices that lie within a certain distance of that vertex and the final graph is drawn on top of the image and displayed in the GUI.
User settings regarding the maximum distance for two vertices to be connected, the maximum number of features, and the frequency of the graph extraction exist.
