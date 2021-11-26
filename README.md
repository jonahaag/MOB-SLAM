# Model-based SLAM GUI

MobSLAM is a Simultaneous Localization and Mapping system for deformable environments.
This repository contains a graphical user interface that enables 

- the display of a [SOFA simulation](https://www.sofa-framework.org)
- different options to record and select different paths as well as a keyboard controller for the simulation camera
- different options to deform the simulated object
- use of a Simultaneous Localization and Mapping (SLAM) algorithm to 
	1. track the camera movement within the simulation 
	2. generate a map of the scene
	3. incorporate deformation information based on the parallel simulation
	
It is designed to be modular and easily extensible and aims at providing a reliable and replicable code base for future work on this topic.

The model-based approach enables the SLAM algorithm to produce good results even in the presence of deformations e.g. caused by external forces or changes in volume.
The aim of this work is to provide a more reliable geometric representation of deformable structures based on a monocular camera by directly incorporating information about the deformation into the mapping.
The basic idea is to run a parallel FEM simulation predicting the deformation based on measurements and then use the simulated surface information, i.e. vertex positions, to continuously update the SLAM results.
At this stage there is no distinction between the "real world" and the simulation which basically equals perfect predictions of the deformation.
This is obviously almost impossible to achieve in real life which is why the interface is designed to easily separate between the two views - more information on this can be found below.
This repository was created as part of the research area B1 concerning [Intraoperative Navigation of Multimodal sensors](https://www.grk2543.uni-stuttgart.de/en/research/b-modeling-and-classification/b1-modeling/) of the [RTG 2543: Intraoperative Multisensory Tissue Differentiation in Oncology](https://www.grk2543.uni-stuttgart.de/en/) at the [Institute for System Dynamics (ISYS)](https://www.isys.uni-stuttgart.de/en/), University of Stuttgart, Germany.

It builds on top of [QSofaGLViewTools](https://github.com/psomers3/QSofaGLViewTools) and [MATLAB Monocular Visual Simultaneous Localization and Mapping](https://www.mathworks.com/help/vision/ug/monocular-visual-simultaneous-localization-and-mapping.html).

## Repository overview
A small overview of recent changes of the GUI to improve user experience:

1. Docker Widget Layout consisting of: 
	- Options bar at the top (fixed position and size)
	- Sofa GL Viewer showing the simulation on the left side (right now also fixed position and size)
	- SLAM Results Plot and Feature Graph Plot as a Tab Widgets (can be undocked and resized, design to be improved). Double click on the top of the widget to (un)dock or drag and drop

2. Light Mode / Dark Mode with qdarkstyle, though some things need to be improved
3. Slider to deform the Sofa object and possibly test future versions of the Model-based approach
4. Settings Dialog with some initial ideas regarding what might be interesting to play around with, some visual settings

## Prerequisites

1. Sofa Python3 bindings
2. qtpy, PyQt5
3. pyqtgraph
4. networkx
5. cv2
6. qdarkstyle

## How to get going / Demo / Tutorial

## Docker container

## Further resources
