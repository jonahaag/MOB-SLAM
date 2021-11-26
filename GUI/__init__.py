from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from SofaViewer.Widgets.SofaGLViewer import SofaGLViewer
from SofaViewer.Widgets.SofaSim import SofaSim
# from SofaViewer.Widgets.QXBoxViewController import QXBoxViewController
from SofaViewer.Widgets.QSofaViewKeyboardController import QSofaViewKeyboardController
from GUI.EngineORB import EngineORB
from FeatureGraph import NetworkSLAM as nxs
import os
import pyqtgraph as pg
import pyqtgraph.widgets
import pyqtgraph.opengl as gl
import numpy as np
import sys
import qdarkstyle