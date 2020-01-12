from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, Signal, Property, Slot, Qt
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType, QQmlEngine
from PySide2.QtWidgets import QApplication
import PySide2.QtGui as QtGui
import PySide2.QtCharts

from QVTKFramebufferObjectItem import FboItem

def defaultFormat(stereo_capable):
  """ Po prostu skopiowałem to z https://github.com/Kitware/VTK/blob/master/GUISupport/Qt/QVTKRenderWindowAdapter.cxx
     i działa poprawnie bufor głębokości
  """
  fmt = QtGui.QSurfaceFormat()
  fmt.setRenderableType(QtGui.QSurfaceFormat.OpenGL)
  fmt.setVersion(3, 2)
  fmt.setProfile(QtGui.QSurfaceFormat.CoreProfile)
  fmt.setSwapBehavior(QtGui.QSurfaceFormat.DoubleBuffer)
  fmt.setRedBufferSize(8)
  fmt.setGreenBufferSize(8)
  fmt.setBlueBufferSize(8)
  fmt.setDepthBufferSize(8)
  fmt.setAlphaBufferSize(8)
  fmt.setStencilBufferSize(0)
  fmt.setStereo(stereo_capable)
  fmt.setSamples(0)

  return fmt

class ChartDataProvider(QObject):
    def __init__(self, parent=None):
        super(ChartDataProvider, self).__init__(parent)

    @Slot(PySide2.QtCore.QObject)
    def fillData(self, series):
        print(series)
        series.append(0.1,0.23)
        series.append(0.4,0.3)
        series.append(0.7,0.75)
        series.append(0.85,0.65)
        series.setName("Czy to ładny przebieg?")
   
class CanvasHandler(QObject):
    def __init__(self, sys_argv):
        super().__init__()
        self.__m_vtkFboItem = None
        #* Set style: https://stackoverflow.com/questions/43093797/PySide2-quickcontrols-material-style
        sys_argv += ['--style', 'material'] #! MUST HAVE


        QApplication.setAttribute( Qt.AA_UseDesktopOpenGL )
        QtGui.QSurfaceFormat.setDefaultFormat(defaultFormat(False)) # from vtk 8.2.0
        app = QApplication(sys_argv)

        engine = QQmlApplicationEngine()
        app.setApplicationName('QtVTK-Py')

        # Register QML Types
        qmlRegisterType(FboItem, 'QtVTK', 1, 0, 'VtkFboItem')

        # Expose/Bind Python classes (QObject) to QML
        ctxt = engine.rootContext() # returns QQmlContext
        ctxt.setContextProperty('canvasHandler', self)
        self.dataProvider = ChartDataProvider()
        ctxt.setContextProperty('chartDataProvider', self.dataProvider)

        # Load main QML file
        engine.load(QUrl.fromLocalFile('resources/main.qml'))

        # Get reference to the QVTKFramebufferObjectItem in QML
        rootObject = engine.rootObjects()[0] # returns QObject
        self.__m_vtkFboItem = rootObject.findChild(FboItem, 'vtkFboItem')

        # Give the vtkFboItem reference to the CanvasHandler
        if (self.__m_vtkFboItem):
            qDebug('CanvasHandler::CanvasHandler: setting vtkFboItem to CanvasHandler')
            self.__m_vtkFboItem.rendererInitialized.connect(self.startApplication)
        else:
            qCritical('CanvasHandler::CanvasHandler: Unable to get vtkFboItem instance')
            return

        rc = app.exec_()
        qDebug(f'CanvasHandler::CanvasHandler: Execution finished with return code: {rc}')

    @Slot(str) 
    def openModel(self, fileName):
        print(f'Otwieram: {fileName}')
        self.__m_vtkFboItem.addModel(fileName)

    @Slot(int,int,int)
    def mousePressEvent(self, button:int, screenX:int, screenY:int):
        qDebug('CanvasHandler::mousePressEvent()')
        #self.__m_vtkFboItem.selectModel(screenX, screenY)

    @Slot(int,int,int)
    def mouseMoveEvent(self, button:int, screenX:int, screenY:int):
        qDebug('CanvasHandler::mouseMoveEvent()')


    @Slot(int,int,int)
    def mouseReleaseEvent(self, button:int, screenX:int, screenY:int):
        qDebug('CanvasHandler::mouseReleaseEvent()')


    def startApplication(self):
        qDebug('CanvasHandler::startApplication()')
        self.__m_vtkFboItem.rendererInitialized.disconnect(self.startApplication)

