import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Dialogs 1.2
import QtQuick.Window 2.12
import QtQuick.Controls.Material 2.12
import QtCharts 2.3
import QtVTK 1.0

ApplicationWindow {
    id: root
    minimumWidth: 1024
    minimumHeight: 700
    visible: true
    title: "QtVTK-Py"

    Material.primary: Material.Indigo
    Material.accent: Material.LightBlue

    Rectangle {
        id: screenCanvasUI
        anchors.fill: parent

        VtkFboItem {
            id: vtkFboItem
            objectName: "vtkFboItem"
            anchors.fill: parent

            MouseArea {
                acceptedButtons: Qt.AllButtons
                anchors.fill: parent
                scrollGestureEnabled: false

                onPositionChanged: (mouse) => {
                    canvasHandler.mouseMoveEvent(pressedButtons, mouseX, mouseY);
                   mouse.accepted = false;
                }
                onPressed: (mouse) => {
                    canvasHandler.mousePressEvent(pressedButtons, mouseX, mouseY);
                    mouse.accepted = false;
                    // if u want to propagate the pressed event
                    // so the VtkFboItem instance can receive it
                    // then uncomment the belowed line
                    // mouse.ignore() // or mouse.accepted = false
                }
                onReleased: (mouse) => {
                    canvasHandler.mouseReleaseEvent(pressedButtons, mouseX, mouseY);
                    print(mouse);
                    mouse.accepted = false;
                }
                onWheel: (wheel) => {
                    wheel.accepted = false;
                }
            }
        }

        Button {
            id: openFileButton
            text: "Open file"
            highlighted: true
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: 50
            onClicked: {
                openModelsFileDialog.visible = true
            }

            ToolTip.visible: hovered
            ToolTip.delay: 1000
            ToolTip.text: "Open a 3D model into the canvas"
        }

        Button {
            id: showChart
            text: "Show Chart"
            highlighted: true
            anchors.right: openFileButton.left
            anchors.bottom: parent.bottom
            anchors.margins: 50
            onClicked: {                
                lineChart.visible = !lineChart.visible
            }

            ToolTip.visible: hovered
            ToolTip.delay: 1000
            ToolTip.text: "Show 2D Chart in right corner"
        }

        ChartView {
            id: lineChart
            title: "Line"
            visible: false
            anchors.top: parent.top
            anchors.right: parent.right
            width: 300
            height: 300
            antialiasing: true

            LineSeries {
                id: lineSeries
                name: "LineSeries"
                /*
                XYPoint { x: 0; y: 0 }
                XYPoint { x: 1.1; y: 2.1 }
                XYPoint { x: 1.9; y: 3.3 }
                XYPoint { x: 2.1; y: 2.1 }
                XYPoint { x: 2.9; y: 4.9 }
                XYPoint { x: 3.4; y: 3.0 }
                XYPoint { x: 4.1; y: 3.3 }
                */
            }

            Component.onCompleted: {
                print("Nothing")
                print(chartDataProvider)
                chartDataProvider.fillData(lineSeries)
            }
        }
    }

    FileDialog {
        id: openModelsFileDialog
        visible: false
        title: "Import model"
        folder: shortcuts.documents
        nameFilters: ["Model files" + "(*.stl *.STL)", "All files" + "(*)"]

        onAccepted: {
            canvasHandler.showFileDialog = false;
            canvasHandler.openModel(fileUrl);
        }
        onRejected: {
            canvasHandler.showFileDialog = false;
        }
    }
}
