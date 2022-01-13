# GUI

## Basic GUI layout

There exist two basic layout modes: `Main` (left) and `Test` (right) that, for the most part, consist of the same elements.
The only real difference is that `Test` doesn't distinguish between the real world view and the simulation view (at least in terms of visualization) and therefore shows the environment only once.

<img src="images/main_gui1.png" alt="Main Mode" height="300"/> <img src="images/test_gui.png" alt="Test Mode" height="300"/>

## Option Bar

The options bar consists of the following elements:

* **start/stop button** for simulation
* **start/stop button** for SLAM
* **settings button** to open settings dialog (see below)
* **deformation slider** to deform the sofa object
* **graph extraction checkbox** to switch on/turn off the graph extraction as described in [feature_graph.md](feature_graph.md)
* **colortheme checkbox** to switch between light and dark mode
* **text editor** to which the console output (e.g. print statements) is redirected

![](images/gui.gif)

## Settings dialog

Following values can be set by the user:

* abc

