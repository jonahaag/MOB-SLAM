import Sofa
import Sofa.Core
from Sofa.constants import *
import math


class controller(Sofa.Core.Controller):
    """ This is a custom controller to perform actions when events are triggered """
    def __init__(self, *args, **kwargs):
        # These are needed (and the normal way to override from a python class)
        Sofa.Core.Controller.__init__(self, *args, **kwargs)

        self.node = kwargs.get("node")
        self.camera = self.node.camera
        self.totalTime = 0.0
        self.object = self.node.getChild('ellipsoid')
        self.startForce = 0
        self.endForce = 15
        self.startTime = False
        self.endTime = 20
        self.startForces = False
        self.immediateForce1 = False
        self.immediateForce2 = False
        

    def onAnimateEndEvent(self, event):
        self.totalTime += event['dt'] # dt = 0.01     
        
        if self.startForces and not self.startTime:
            self.startTime = self.totalTime
            self.endTime = self.startTime + self.endTime
            
        if self.startForces and self.totalTime <= self.endTime:
            n = len(self.object.boxROI.findData("indices").value)
            forces = []
            xForce = self.startForce + (self.endForce-self.startForce) * (self.totalTime-self.startTime)/(self.endTime-self.startTime)
            xForce = 0
            yForce = self.startForce + (self.endForce-self.startForce) * (self.totalTime-self.startTime)/(self.endTime-self.startTime)
            yForce = -yForce
            zForce = self.startForce + (self.endForce-self.startForce) * (self.totalTime-self.startTime)/(self.endTime-self.startTime)
            for i in range(1,n+1):
                forces.append([xForce,yForce,zForce])
            self.object.CFF.findData('indices').value = self.object.boxROI.findData("indices").value
            self.object.CFF.findData('forces').value = forces
            
        if self.immediateForce1:
            n = len(self.object.boxROI.findData("indices").value)
            forces = []
            for i in range(1,n+1):
                forces.append([5,5,5])
                self.object.CFF.findData('indices').value = self.object.boxROI.findData("indices").value
                self.object.CFF.findData('forces').value = forces
       
        if self.immediateForce2:
            n = len(self.object.boxROI.findData("indices").value)
            forces = []
            for i in range(1,n+1):
                forces.append([10,10,10])
                self.object.CFF.findData('indices').value = self.object.boxROI.findData("indices").value
                self.object.CFF.findData('forces').value = forces


    # def onKeypressedEvent(self, event):
