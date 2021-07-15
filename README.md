# Model_based_SLAM
MobSLAM is a Simultaneous Localization and Mapping system for deformable environments

# WHATS NEW
A small overview of recent changes of the GUI to improve user experience:
1. Docker Widget Layout consisting of: 
- Options bar at the top (fixed position and size)
- Sofa GL Viewer showing the simulation on the left side (right now also fixed position and size)
- SLAM Results Plot and Feature Graph Plot as a Tab Widgets (can be undocked and resized, design to be improved). Double click on the top of the widget to (un)dock or drag and drop
2. Light Mode / Dark Mode with qdarkstyle, though some things need to be improved
3. Slider to deform the Sofa object and possibly test future versions of the Model-based approach
4. Settings Dialog with some initial ideas regarding what might be interesting to play around with, some visual settings

# TODO
1. further cleanup
2. efficiency improvements: triangle selection, multithreading, projection,...
3. TODOs as in the code
4. uniform feature distribution for opencv orb detection
5. fix bugs: follow camera, change material properties at runtime, layout bug and possible get_screenshot issues on different sized screens 
6. error handling to be improved massively -> right now, virtually now exceptions thrown etc.
7. add settings for camera path in the simulation (e.g. which file to choose from for keypoint_navigation) 
8. add legend and more interactivity to the plots

# Prerequisites
1. Sofa Python3 bindings
2. qtpy, PyQt5
3. pyqtgraph
4. networkx 
5. cv2
6. qdarkstyle

# Troubleshooting
If the SLAM does not produce the expected results, most likely the get_screenshot function of SofaGLViewer.py does not work properly. 
To check, please check the 'Extract Networkx Graph'  checkbox and compare the images in the Feature Graph Plot to the GL Viewer (what you see in the simulation). This is easier in Light Mode since then the frame of the Feature Graph Plot is visible (the image is shown smaller). If the shown image does not match the viewer, please let me know.
