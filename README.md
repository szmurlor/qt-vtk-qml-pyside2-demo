# A python-based project on VTK-QML-PySide2 combination

The source code is based on [Nicanor Romero Venier's project](https://github.com/nicanor-romero/QtVtk) and its [Tung
dao-duc-tung port to Python](https://github.com/dao-duc-tung/QtVTK-Py).

This is a strongly simplified version of the application which focuses mainly on fixing problems with binding between Qt, QML, PySide2 and VTK. The code is refactored to focus on the integration of VTK and QML. This is more a tutorial version of the application than a final product. In addition it shows how to overlay a very simple QML Qt Charts plot and feed it with data from Python.

## Description

The code was tested using Python 3.7.6, Qt 5.12.5, PySide2 5.13.1 and VTK 8.2 (installed with Conda environment in Windows 10 and Ubuntu - https://docs.conda.io/en/latest/miniconda.html).

Thanks Nicanor and Tung very much!

## Installation

Assuming you are having a conda environment (on January 2020 the pip has not yet released the 8.2 version of VTK which supports PySide2 for the interactor binding.)

```sh
conda create --name vtkqml python=3.7
conda activate vtkqml
conda install -c conda-forge qt vtk pyside2 numpy pandas pyopengl
```

The `-c conda-forge` is required because the `PySide2` is not available in the main conda repository.

After doing this you can start the application:

```sh
python src/main.py
```

## Tweaks and quirks 

Some tweaks and 'hacks' were required to make all running smoothly. The first was the problem of the depth buffer compatibility between the Qt's OpenGL rendering configuraion and VTK (https://public.kitware.com/pipermail/vtkusers/2016-September/096465.html). This required to initialize the QSurfaceFormat before the QApplication ws initialized. The key is the moment when you do this and it must be done before creating the QApplication, as this the moment when the OpenGL context is initialized.

The pieco of reposnsible for this:

```python
def defaultFormat(stereo_capable):
  """ Ported from: https://github.com/Kitware/VTK/blob/master/GUISupport/Qt/QVTKRenderWindowAdapter.cxx
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

...

QtGui.QSurfaceFormat.setDefaultFormat(defaultFormat(False)) # from vtk 8.2.0
app = QApplication(sys_argv)
```

## Example

![Show layout, Import and view STL file, overaly Qt Charts](resources/qt-vtk-qml-pyside2-demo.gif "Import and view STL files")

