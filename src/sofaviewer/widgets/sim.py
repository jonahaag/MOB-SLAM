from qtpy.QtCore import QObject, QTimer, Signal
import Sofa.Core as SCore
import Sofa.Simulation as SSim
from SofaRuntime import PluginRepository, importPlugin
import os
from .cameracontroller import controller


class SofaSim(QObject):
    animation_end = Signal()
    animation_start = Signal()

    def __init__(self):
        super(SofaSim, self).__init__()
        # Register all the common component in the factory.
        PluginRepository.addFirstPath(
            "/Users/jona/sofa_20.12/build_20.12/install/plugins"
        )
        importPlugin("SofaOpenglVisual")
        importPlugin("SofaComponentAll")
        importPlugin("SofaGeneralLoader")
        importPlugin("SofaImplicitOdeSolver")
        importPlugin("SofaLoader")
        importPlugin("SofaSimpleFem")
        importPlugin("SofaBoundaryCondition")
        importPlugin("SofaMiscForceField")
        importPlugin("SofaEngine")
        self.root = SCore.Node("Root")
        root = self.root
        root.gravity = [0, 0, 0]
        meshFolderName = "mesh"
        mshFilename = os.path.join(meshFolderName, "blender_ellipsoid.msh")
        stlFilename = os.path.join(meshFolderName, "blender_ellipsoid.stl")
        textureFilename = os.path.join(meshFolderName, "suchbild.dds")
        root.addObject("VisualStyle", displayFlags="showVisual")
        root.addObject("MeshGmshLoader", name="meshGmsh", filename=mshFilename)

        root.addObject("EulerImplicitSolver")
        root.addObject(
            "CGLinearSolver", iterations="200", tolerance="1e-09", threshold="1e-09"
        )

        translation = [0, 0, 0]
        rotation = [0, 0, 0]
        ellipsoid = root.addChild("ellipsoid")

        ellipsoid.addObject(
            "TetrahedronSetTopologyContainer", name="topo", src="@../meshGmsh"
        )
        ellipsoid.addObject(
            "TetrahedronSetGeometryAlgorithms", template="Vec3d", name="GeomAlgo"
        )
        ellipsoid.addObject("Mesh", src="@../meshGmsh", name="container")
        ellipsoid.addObject(
            "MechanicalObject",
            template="Vec3d",
            name="MechanicalModel",
            showObject="0",
            showObjectScale="1",
            translation=translation,
            rotation=rotation,
        )
        #        ellipsoid.addObject("UniformMass", totalMass=0.01)
        ##        ellipsoid.addObject("LinearSolverConstraintCorrection", solverName="directSolver")
        #
        ellipsoid.addObject(
            "TetrahedronFEMForceField",
            name="fem",
            youngModulus="1000",
            poissonRatio="0.4",
            method="large",
        )

        ellipsoid.addObject("MeshMatrixMass", massDensity="1")
        ellipsoid.addObject(
            "BoxROI",
            name="boxROI_fix",
            box="-1.5 -1.5 -0.5 1.5 1.5 0.5",
            drawBoxes=True,
        )
        ellipsoid.addObject(
            "FixedConstraint", name="FixedConstraint", indices="@boxROI_fix.indices"
        )
        # Visual
        visual = ellipsoid.addChild("visual")
        visual.addObject(
            "MeshSTLLoader",
            name="meshLoader_0",
            filename=stlFilename,
            translation=translation,
            rotation=rotation,
        )
        visual.addObject(
            "OglModel",
            name="VisualModel",
            src="@meshLoader_0",
            texturename=textureFilename,
            scale=1,
            rotation=rotation,
        )
        visual.addObject(
            "BarycentricMapping",
            input="@..",
            output="@VisualModel",
            name="visual mapping",
        )
        # Collision
        collision = ellipsoid.addChild("collision")
        collision.addObject("MeshSTLLoader", name="meshLoader_1", filename=stlFilename)
        collision.addObject("Mesh", src="@meshLoader_1", name="topo")
        collision.addObject(
            "MechanicalObject",
            name="collisMech",
            translation=translation,
            rotation=rotation,
        )
        # collision.addObject('Triangle', selfCollision="false")
        # collision.addObject('Line',selfCollision="false")
        # collision.addObject('Point', selfCollision="false")
        collision.addObject(
            "BarycentricMapping",
            input="@..",
            output="@collisMech",
            name="visual mapping",
        )

        # ellipsoid.addObject('BoxROI', name='boxROI', box='-0.1 0.3 0.5 1.0 1.5 1.5', drawBoxes=True)
        ellipsoid.addObject(
            "BoxROI", name="boxROI", box="-1.5 -1.5 0.2 1.5 0 1.5", drawBoxes=True
        )
        # ellipsoid.addObject('BoxROI', name='boxROI', box='-0.5 -0.3 0.7 0.5 0.2 1.5', drawBoxes=True)
        ellipsoid.addObject(
            "ConstantForceField", name="CFF", indices=[1], forces=[0, 0, 0]
        )  # , showArrowSize="0.01"

        ellipsoid.addObject(
            "PairBoxROI",
            name="PairBox",
            inclusiveBox="-1.5 -1.5 0.2 1.5 0 1.5",
            includedBox="-1.3 -1.3 0.4 1.3 -0.2 1.3",
        )
        ellipsoid.addObject(
            "AffineMovementConstraint",
            name="AMC",
            template="Vec3d",
            indices="@PairBox.indices",
            meshIndices="@boxROI.indices",
            translation=[0.0, 0.0, 0.0],
            rotation=[1, 0, 0, 0, 1, 0, 0, 0, 1],
        )

        # cavity = ellipsoid.addChild('cavity')
        # #cavity.createObject('MeshGmshLoader', name='loader', filename='geometry/inner_sphere.msh', scale= '60')
        # cavity.addObject('MeshSTLLoader', name='loader', filename=stlFilename, scale=0.9)
        # cavity.addObject('Mesh', src='@loader', name='topo')
        # cavity.addObject('MechanicalObject', name='cavity')
        # #cavity.createObject('SurfacePressureConstraint', name="surfaceConstraint", triangles='@topo.triangles', valueType="volumeGrowth")
        # # We need to use a BarycentricMapping to map the deformation of the cavity onto our 3d Mesh
        # cavity.addObject('BarycentricMapping', name='mapping',  mapForces='false', mapMasses='false')
        ellipsoid.addObject(
            "SurfacePressureForceField", name="surfaceConstraint", pressure=1
        )

        # place light and a camera
        # self.root.addObject("BackgroundSetting", color=[25/255,35/255,45/255,1.0])
        self.root.addObject("LightManager")
        self.root.addObject("DirectionalLight", direction=[0, 1, 1])
        self.root.addObject("DirectionalLight", direction=[0, -1, -1])
        self.root.addObject(
            "InteractiveCamera",
            name="camera",
            position=[0, 0, 5],
            lookAt=[0, 0, 0],
            distance=5,
            fieldOfView=60,
            zNear=0.160738,
            zFar=20,
        )

        # add controller
        self.root.addObject(controller(name="CameraController", node=root))

        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self.step_sim)
        self.simulation_timer.setInterval(self.root.getDt())
        self.is_animating = False

    def init_sim(self):
        # start the simulator
        SSim.init(self.root)
        self.totalTime = 0.0

    def start_sim(self):
        self.simulation_timer.start()
        self.is_animating = True

    def stop_sim(self):
        self.simulation_timer.stop()
        self.is_animating = False

    def step_sim(self):
        self.animation_start.emit()
        SSim.animate(self.root, self.root.getDt())
        SSim.updateVisual(self.root)  # updates the visual mappings
        #        self.totalTime += self.root.getDt()
        #        self.totalTime = round(self.totalTime, 2)
        #        print(self.simulation_timer)

        self.animation_end.emit()
