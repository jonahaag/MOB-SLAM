# SLAM

## SLAM basics

Simultaneous Localization and Mapping (SLAM) is a term describing a more or less broad class of algorithms that aim at reconstructing the surrounding (mapping) and providing precise position information (localization) of a mobile agent simultaneously using the agent's sensory input data.
This project considers the probably most-studied case of a monocular camera, i.e. a single camera image is supplied to the algorithm continuously.
However, in the literature many different sensor configurations can be found.

For the classic monocular case in a rigid enviroment, many different solution schemes have been developed and studied extensively.
One of the most well-known of these is ORB-SLAM, an algorithm that relies on ORB feature detection and has been proven to deliver very good results using common public datasets and real-world data.

## ORB-SLAM extension for deformable enviroments

In this project deformable environments are considered, which can cause the estimated and actual camera position to diverge and also leads to inaccurate mapping of the environment when using the "standard" (unmodified) ORB-SLAM.
To act upon these emerging diffuculties, this proof-of-concept tries to use an existing environment model to predict the ongoing deformation.
The predictions are then used to update the results of the standard algorithm to still produce satisfactory results.

## MATLAB implementation

The `src/slam` folder contains a MATLAB implementation of ORB-SLAM that is available via [MathWorks](https://de.mathworks.com/help/vision/ug/monocular-visual-simultaneous-localization-and-mapping.html).
While the predicted deformation is computed in Python using SOFA, incorporating that information into the ongoing SLAM process is done in MATLAB.
The main contributions are located in the [projectionAndPrediction folder](../src/slam/projectionAndPrediction).
The basic concept of the model-based approach contains methods and scripts to perform the following steps:

* projecting new map points on the surface of the environment model
    * `projectMapPoints.m`
    * `cameraViewProjection.m`
* updating the position of points that were projected at previous iterations based on new predictions of the deformation (forward prediction)
    * `forwardPrediction.m`
* updating the correspondend 2D position of the feature in the image
    * `updateFeaturePosition.m`
* keeping track of projected points, removing points that are no longer considered
    * `addProjectedPoints.m`
    * `removeProjectedPoints.m`
    * `removeUnprojectedPoints.m`

The remaining functions are used as helper functions or are deprecated but kept for testing purposes.