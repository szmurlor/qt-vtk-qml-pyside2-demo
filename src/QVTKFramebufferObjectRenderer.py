from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, QFileInfo, QEvent, Qt, QSize, Signal
from PySide2.QtGui import QSurfaceFormat, QColor, QMouseEvent, QWheelEvent, QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat, QOpenGLFunctions
from PySide2.QtQuick import QQuickFramebufferObject

import logging
import vtk
from OpenGL import GL

from SceneHelpers import SceneHelper


class FboRenderer(QQuickFramebufferObject.Renderer):
    def __init__(self):
        super().__init__()
        self.renderer = RendererHelper()
        self.__fbo = None

    def render( self ):
        self.renderer.render()

    def synchronize(self, item:QQuickFramebufferObject):
        self.renderer.synchronize(item)

    def createFramebufferObject( self, size ):
        self.__fbo = self.renderer.createFramebufferObject( size )
        return self.__fbo

    def addModel(self, fileName):
        self.renderer.addModel(fileName)

class RendererHelper(QObject):
    def __init__(self):
        qDebug('RendererHelper::__init__()')
        super().__init__()
        self.__m_vtkFboItem = None
        self.gl = QOpenGLFunctions()

        self.__m_mouseLeftButton:QMouseEvent = None
        self.__m_mouseEvent:QMouseEvent = None
        self.__m_moveEvent:QMouseEvent = None
        self.__m_wheelEvent:QWheelEvent = None

        self.__m_firstRender:bool = True

        self.renderWindow:vtk.vtkGenericOpenGLRenderWindow = vtk.vtkGenericOpenGLRenderWindow()
        self.renderer:vtk.vtkRenderer = vtk.vtkRenderer()
        self.renderWindow.AddRenderer(self.renderer)

        #* Interactor
        self.interactor:vtk.vtkGenericRenderWindowInteractor = vtk.vtkGenericRenderWindowInteractor()
        self.interactor.EnableRenderOff()
        self.renderWindow.SetInteractor(self.interactor)

        #* Initialize the OpenGL context for the renderer
        self.renderWindow.OpenGLInitContext()

        #* Interactor Style
        style = vtk.vtkInteractorStyleTrackballCamera()
        style.SetDefaultRenderer(self.renderer)
        style.SetMotionFactor(10.0)
        self.interactor.SetInteractorStyle(style)


    def setVtkFboItem(self, vtkFboItem):
        self.__m_vtkFboItem = vtkFboItem


    def synchronize(self, item:QQuickFramebufferObject):
        rendererSize = self.renderWindow.GetSize()
        if self.__m_vtkFboItem.width() != rendererSize[0] or self.__m_vtkFboItem.height() != rendererSize[1]:
            self.renderWindow.SetSize(int(self.__m_vtkFboItem.width()), int(self.__m_vtkFboItem.height()))

        #* Copy mouse events
        print(self.__m_vtkFboItem.getLastMouseButton().isAccepted())
        if not self.__m_vtkFboItem.getLastMouseButton().isAccepted():
            self.__m_mouseEvent = self.__m_vtkFboItem.getLastMouseButton()

        if not self.__m_vtkFboItem.getLastMoveEvent().isAccepted():
            self.__m_moveEvent = self.__m_vtkFboItem.getLastMoveEvent()

        if self.__m_vtkFboItem.getLastWheelEvent() and not self.__m_vtkFboItem.getLastWheelEvent().isAccepted():
            self.__m_wheelEvent = self.__m_vtkFboItem.getLastWheelEvent()


    def render(self):
        self.renderWindow.PushState()
        self.openGLInitState()
        self.renderWindow.Start()

        if self.__m_firstRender:
            self.renderWindow.SetOffScreenRendering(True)
            sceneHelper = SceneHelper(self.renderer)
            sceneHelper.initScene()
            self.resetCamera()
            self.__m_firstRender = False

        #* Process camera related commands
        if self.__m_mouseEvent and not self.__m_mouseEvent.isAccepted():
            self.interactor.SetEventInformationFlipY(
                self.__m_mouseEvent.x(), self.__m_mouseEvent.y(),
                1 if (self.__m_mouseEvent.modifiers() & Qt.ControlModifier) > 0 else 0,
                1 if (self.__m_mouseEvent.modifiers() & Qt.ShiftModifier) > 0 else 0,
                '0',
                1 if self.__m_mouseEvent.type() == QEvent.MouseButtonDblClick else 0
            )

            if self.__m_mouseEvent.type() == QEvent.MouseButtonPress:
                self.interactor.InvokeEvent(vtk.vtkCommand.LeftButtonPressEvent)
            elif self.__m_mouseEvent.type() == QEvent.MouseButtonRelease:
                self.interactor.InvokeEvent(vtk.vtkCommand.LeftButtonReleaseEvent)

            self.__m_mouseEvent.accept()

        #* Process move event
        if self.__m_moveEvent and not self.__m_moveEvent.isAccepted():
            if self.__m_moveEvent.type() == QEvent.MouseMove and self.__m_moveEvent.buttons() & (Qt.RightButton | Qt.LeftButton) :
                self.interactor.SetEventInformationFlipY(
                    self.__m_moveEvent.x(),
                    self.__m_moveEvent.y(),
                    1 if (self.__m_moveEvent.modifiers() & Qt.ControlModifier) > 0 else 0,
                    1 if (self.__m_moveEvent.modifiers() & Qt.ShiftModifier) > 0 else 0,
                    '0',
                    1 if self.__m_moveEvent.type() == QEvent.MouseButtonDblClick else 0
                )

                self.interactor.InvokeEvent(vtk.vtkCommand.MouseMoveEvent)

            self.__m_moveEvent.accept()

        #* Process wheel event
        if self.__m_wheelEvent and not self.__m_wheelEvent.isAccepted():
            self.interactor.SetEventInformationFlipY(
                self.__m_wheelEvent.x(), self.__m_wheelEvent.y(),
                1 if (self.__m_wheelEvent.modifiers() & Qt.ControlModifier) > 0 else 0,
                1 if (self.__m_wheelEvent.modifiers() & Qt.ShiftModifier) > 0 else 0,
                '0',
                1 if self.__m_wheelEvent.type() == QEvent.MouseButtonDblClick else 0
            )

            if self.__m_wheelEvent.delta() > 0:
                self.interactor.InvokeEvent(vtk.vtkCommand.MouseWheelForwardEvent)
            elif self.__m_wheelEvent.delta() < 0:
                self.interactor.InvokeEvent(vtk.vtkCommand.MouseWheelBackwardEvent)

            self.__m_wheelEvent.accept()

        # Render
        self.renderWindow.Render()
        self.renderWindow.PopState()
        self.__m_vtkFboItem.window().resetOpenGLState()


    def openGLInitState(self):
        self.renderWindow.OpenGLInitState()
        self.renderWindow.MakeCurrent()
        self.gl.initializeOpenGLFunctions()


    def createFramebufferObject(self, size:QSize) -> QOpenGLFramebufferObject:
        format = QOpenGLFramebufferObjectFormat()
        format.setAttachment(QOpenGLFramebufferObject.Depth)
        framebufferObject = QOpenGLFramebufferObject(size, format)
        framebufferObject.release()
        return framebufferObject


    def addModel(self, fileName):
        reader = vtk.vtkSTLReader()
        url = QUrl(fileName)
        reader.SetFileName(url.path())
        reader.Update()

        transform = vtk.vtkTransform()
        transform.Scale( (.5,.5,.5) )

        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetInputConnection(reader.GetOutputPort())
        transformFilter.SetTransform(transform)
        transformFilter.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(transformFilter.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.renderer.AddActor(actor)

        print(f"Added...{url.path()}")


    def resetCamera(self):
        #* Seting the clipping range here messes with the opacity of the actors prior to moving the camera
        m_camPositionX = -237.885
        m_camPositionY = -392.348
        m_camPositionZ = 369.477
        self.renderer.GetActiveCamera().SetPosition(m_camPositionX, m_camPositionY, m_camPositionZ)
        self.renderer.GetActiveCamera().SetFocalPoint(0.0, 0.0, 0.0)
        self.renderer.GetActiveCamera().SetViewUp(0.0, 0.0, 1.0)
        self.renderer.ResetCameraClippingRange()
