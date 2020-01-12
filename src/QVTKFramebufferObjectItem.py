from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, QEvent, QPoint, QPointF, Qt, Signal
from PySide2.QtGui import QColor, QMouseEvent, QWheelEvent
from PySide2.QtQuick import QQuickFramebufferObject

from QVTKFramebufferObjectRenderer import FboRenderer
import logging

class FboItem(QQuickFramebufferObject):
    rendererInitialized = Signal()

    def __init__(self):
        logging.debug('FboItem::__init__')
        super().__init__()
        self.__m_vtkFboRenderer = None

        self.__m_lastMouseLeftButton:QMouseEvent = QMouseEvent(QEvent.Type.None_, QPointF(0,0), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        self.__m_lastMouseButton:QMouseEvent = QMouseEvent(QEvent.Type.None_, QPointF(0,0), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        self.__m_lastMouseMove:QMouseEvent = QMouseEvent(QEvent.Type.None_, QPointF(0,0), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        self.__m_lastMouseWheel:QWheelEvent = None        

        self.setMirrorVertically(True) # QtQuick and OpenGL have opposite Y-Axis directions
        self.setAcceptedMouseButtons(Qt.RightButton | Qt.LeftButton)

    def createRenderer(self):
        logging.debug('FboItem::createRenderer')
        self.setVtkFboRenderer(FboRenderer())
        return self.__m_vtkFboRenderer

    def setVtkFboRenderer(self, renderer):
        logging.debug('FboItem::setVtkFboRenderer')

        self.__m_vtkFboRenderer = renderer
        self.__m_vtkFboRenderer.renderer.setVtkFboItem(self)

        self.rendererInitialized.emit()

    def isInitialized(self) -> bool:
        return (self.__m_vtkFboRenderer != None)

    # #* Camera related functions

    def wheelEvent(self, e:QWheelEvent):
        print("myMouseWheel in Item...")
        self.__m_lastMouseWheel = self.__cloneMouseWheelEvent(e)
        self.__m_lastMouseWheel.ignore()
        e.accept()
        self.update()

    def mousePressEvent(self, e:QMouseEvent):
        if e.buttons() & (Qt.RightButton | Qt.LeftButton):
            print("mousePressEvent in Item...")
            self.__m_lastMouseButton = self.__cloneMouseEvent(e)
            self.__m_lastMouseButton.ignore()
            e.accept()
            self.update()

    def mouseReleaseEvent(self, e:QMouseEvent):
        print("mouseReleaseEvent in Item...")
        self.__m_lastMouseButton = self.__cloneMouseEvent(e)
        self.__m_lastMouseButton.ignore()
        e.accept()
        self.update()

    def mouseMoveEvent(self, e:QMouseEvent):
        if e.buttons() & (Qt.RightButton | Qt.LeftButton):
            print("mouseMoveEvent in Item...")
            self.__m_lastMouseMove = self.__cloneMouseEvent(e)
            self.__m_lastMouseMove.ignore()
            e.accept()
            self.update()


    def getLastMouseButton(self) -> QMouseEvent:
        return self.__m_lastMouseButton

    def getLastMoveEvent(self) -> QMouseEvent:
        return self.__m_lastMouseMove

    def getLastWheelEvent(self) -> QWheelEvent:
        return self.__m_lastMouseWheel


    def resetCamera(self):
        self.__m_vtkFboRenderer.renderer.resetCamera()
        self.update()

    def __cloneMouseEvent(self, e:QMouseEvent):
        event_type = e.type()
        local_pos = e.localPos()
        button = e.button()
        buttons = e.buttons()
        modifiers = e.modifiers()
        clone = QMouseEvent(event_type, local_pos, button, buttons, modifiers)
        clone.ignore()
        return clone

    def __cloneMouseWheelEvent(self, e:QWheelEvent):
        pos = e.pos()
        globalPos = e.globalPos() 
        pixelDelta = e.pixelDelta() 
        angleDelta = e.angleDelta()
        buttons = e.buttons()
        modifiers = e.modifiers()
        phase = e.phase()
        inverted = e.inverted()
        clone = QWheelEvent(pos, globalPos, pixelDelta, angleDelta, buttons, modifiers, phase, inverted)
        clone.ignore()
        clone.accepted = False
        return clone

    def addModel(self, fileName):
        self.__m_vtkFboRenderer.addModel(fileName)
        self.update()
