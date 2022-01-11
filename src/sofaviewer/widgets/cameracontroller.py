import Sofa
import Sofa.Core
from Sofa.constants import *


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
        self.endForce = 50
        self.startTime = False
        self.endTime = 20
        self.startForces = False

        self.displaceNode = False
        

    def onAnimateEndEvent(self, event):
        self.totalTime += event['dt'] # dt = 0.01     
        
        if self.startForces and not self.startTime:
            self.startTime = self.totalTime # set current time as start time of the forces
            self.endTime = self.startTime + self.endTime # set start time + duration as end time of the forces
            
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

        if self.displaceNode:
            #self.indices = self.object.boxROI.findData("indices").value
            self.nodeTranslation = [0.0,0.0,5.5]
            self.nodeRotation = [1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0]
            self.object.AMC.translation.value = self.nodeTranslation
            self.displaceNode = False

    #   def onKeypressedEvent(self, event):
