from PySide2.QtCore import qDebug, qCritical
import numpy as np
import vtk

class SceneHelper:
    def __init__(self, renderer=None):
        self.renderer = renderer

        self.__m_platformModel:vtk.vtkCubeSource = None
        self.__m_platformGrid:vtk.vtkPolyData = None
        self.__m_platformModelActor:vtk.vtkActor = None
        self.__m_platformGridActor:vtk.vtkActor = None

        self.__m_platformWidth:float = 200.0
        self.__m_platformDepth:float = 200.0
        self.__m_platformThickness:float = 2.0
        self.__m_gridBottomHeight:float = 0.15
        self.__m_gridSize:np.uint16 = 10
        self.__m_clickPositionZ:float = 0.0


    def initScene(self):
        qDebug('RendererHelper::initScene()')

        #* Top background color
        r2 = 245.0 / 255.0
        g2 = 245.0 / 255.0
        b2 = 245.0 / 255.0

        #* Bottom background color
        r1 = 170.0 / 255.0
        g1 = 170.0 / 255.0
        b1 = 170.0 / 255.0

        self.renderer.SetBackground(r2, g2, b2)
        self.renderer.SetBackground2(r1, g1, b1)
        self.renderer.GradientBackgroundOn()

        # #* Axes
        axes = vtk.vtkAxesActor()
        axes_length = 50.0
        axes_label_font_size = np.int16(20)
        axes.SetTotalLength(axes_length, axes_length, axes_length)
        axes.SetCylinderRadius(0.01)
        axes.SetShaftTypeToCylinder()
        axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(axes_label_font_size)
        axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(axes_label_font_size)
        axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(axes_label_font_size)
        self.renderer.AddActor(axes)

        # Platform
        self.__generatePlatform()
    

    def __generatePlatform(self):
        qDebug('RendererHelper::__generatePlatform()')

        #* Platform Model
        platformModelMapper = vtk.vtkPolyDataMapper()

        self.__m_platformModel = vtk.vtkCubeSource()
        platformModelMapper.SetInputConnection(self.__m_platformModel.GetOutputPort())

        self.__m_platformModelActor = vtk.vtkActor()
        self.__m_platformModelActor.SetMapper(platformModelMapper)
        self.__m_platformModelActor.GetProperty().SetColor(1, 1, 1)
        self.__m_platformModelActor.GetProperty().LightingOn()
        self.__m_platformModelActor.GetProperty().SetOpacity(1)
        self.__m_platformModelActor.GetProperty().SetAmbient(0.45)
        self.__m_platformModelActor.GetProperty().SetDiffuse(0.4)

        self.__m_platformModelActor.PickableOff()
        self.renderer.AddActor(self.__m_platformModelActor)

        #* Platform Grid
        self.__m_platformGrid = vtk.vtkPolyData()

        platformGridMapper = vtk.vtkPolyDataMapper()
        platformGridMapper.SetInputData(self.__m_platformGrid)

        self.__m_platformGridActor = vtk.vtkActor()
        self.__m_platformGridActor.SetMapper(platformGridMapper)
        self.__m_platformGridActor.GetProperty().LightingOff()
        self.__m_platformGridActor.GetProperty().SetColor(0.45, 0.45, 0.45)
        self.__m_platformGridActor.GetProperty().SetOpacity(1)
        self.__m_platformGridActor.PickableOff()
        self.renderer.AddActor(self.__m_platformGridActor)

        self.__updatePlatform()

    def __updatePlatform(self):
        qDebug('RendererHelper::__updatePlatform()')

        #* Platform Model

        if self.__m_platformModel:
            self.__m_platformModel.SetXLength(self.__m_platformWidth)
            self.__m_platformModel.SetYLength(self.__m_platformDepth)
            self.__m_platformModel.SetZLength(self.__m_platformThickness)
            self.__m_platformModel.SetCenter(0.0, 0.0, -self.__m_platformThickness / 2)

        #* Platform Grid
        gridPoints = vtk.vtkPoints()
        gridCells = vtk.vtkCellArray()

        i = -self.__m_platformWidth / 2
        while i <= self.__m_platformWidth / 2:
            self.__createLine(i, -self.__m_platformDepth / 2, self.__m_gridBottomHeight, i, self.__m_platformDepth / 2, self.__m_gridBottomHeight, gridPoints, gridCells)
            i += self.__m_gridSize

        i = -self.__m_platformDepth / 2
        while i <= self.__m_platformDepth / 2:
            self.__createLine(-self.__m_platformWidth / 2, i, self.__m_gridBottomHeight, self.__m_platformWidth / 2, i, self.__m_gridBottomHeight, gridPoints, gridCells)
            i += self.__m_gridSize

        self.__m_platformGrid.SetPoints(gridPoints)
        self.__m_platformGrid.SetLines(gridCells)

    def __createLine(self, x1:float, y1:float, z1:float, x2:float, y2:float, z2:float, points:vtk.vtkPoints, cells:vtk.vtkCellArray):
        line = vtk.vtkPolyLine()
        line.GetPointIds().SetNumberOfIds(2)

        id_1 = points.InsertNextPoint(x1, y1, z1) # vtkIdType
        id_2 = points.InsertNextPoint(x2, y2, z2) # vtkIdType

        line.GetPointIds().SetId(0, id_1)
        line.GetPointIds().SetId(1, id_2)

        cells.InsertNextCell(line)


    def screenToWorld(self, screenX:np.int16, screenY:np.int16, worldPos:list) -> bool: # list of float
        #* Create  planes for projection plan:
        boundingPlanes = list(vtk.vtkPlane() for i in range(0, 4))

        boundingPlanes[0].SetOrigin(0.0, 1000.0, 0.0)
        boundingPlanes[0].SetNormal(0.0, -1.0, 0.0)

        boundingPlanes[1].SetOrigin(0.0, -1000.0, 0.0)
        boundingPlanes[1].SetNormal(0.0, 1.0, 0.0)

        boundingPlanes[2].SetOrigin(1000.0, 0.0, 0.0)
        boundingPlanes[2].SetNormal(-1.0, 0.0, 0.0)

        boundingPlanes[3].SetOrigin(-1000.0, 0.0, 0.0)
        boundingPlanes[3].SetNormal(1.0, 0.0, 0.0)

        #* Create projection plane parallel platform and Z coordinate from clicked position in model
        plane = vtk.vtkPlane()
        plane.SetOrigin(0.0, 0.0, self.__m_clickPositionZ)
        plane.SetNormal(0.0, 0.0, 1.0)

        #* Set projection and bounding planes to placer
        placer = vtk.vtkBoundedPlanePointPlacer()
        placer.SetObliquePlane(plane)
        placer.SetProjectionNormalToOblique()

        placer.AddBoundingPlane(boundingPlanes[0])
        placer.AddBoundingPlane(boundingPlanes[1])
        placer.AddBoundingPlane(boundingPlanes[2])
        placer.AddBoundingPlane(boundingPlanes[3])

        screenPos = list(0.0 for i in range(0, 2)) # 2 items
        worldOrient = list(0.0 for i in range(0, 9)) # 9 items

        screenPos[0] = screenX
        #*  the y-axis flip for the pickin:
        screenPos[1] = self.renderer.GetSize()[1] - screenY
        withinBounds = placer.ComputeWorldPosition(self.renderer, screenPos, worldPos, worldOrient) # int16_t

        return withinBounds