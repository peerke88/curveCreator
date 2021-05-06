from qt_util import *
import tempfile, os
from maya import cmds, OpenMaya, OpenMayaUI, mel

class CaptureWindow(QDialog):
    def __init__(self, parent=None, name='test'):
        super(CaptureWindow, self).__init__(parent)

        self.setLayout(QVBoxLayout())

        self.SaveAndCloseButton = QPushButton("SaveAndCloseButton")
        self.verticalLayoutWidget_2 = QWidget(self)
        self.verticalLayoutWidget_2.setGeometry(QRect(10, 10, 191, 201))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.layout().addWidget(self.verticalLayoutWidget_2)
        self.layout().addWidget(self.SaveAndCloseButton)

        self.viewportLayout = QVBoxLayout(self.verticalLayoutWidget_2)
        self.viewportLayout.setContentsMargins(0, 0, 0, 0)

        self.__itemCreated = False
        self.name = name
        self.cameraName = ''

        self.__addViewport()
        self.SaveAndCloseButton.clicked.connect(self.__saveAndClose)
        self.SaveAndCloseButton.setText("saveAndClose")

    def __addViewport(self):
        self.cameraName = cmds.camera()[0]
        cmds.hide(self.cameraName)

        self.modelPanelName = cmds.modelEditor(camera=self.cameraName, displayAppearance='smoothShaded', dtx=1, hud=0, alo=0, pm=1, grid=0)

        ptr = OpenMayaUI.MQtUtil.findControl(self.modelPanelName)
        self.modelEditor = wrapinstance(long(ptr))
        self.viewportLayout.addWidget(self.modelEditor)

        cmds.viewFit(self.cameraName, all=True)

    def createSnapshot(self):
        filePath  = os.path.join(tempfile.tempdir,'screenshot.jpg')
        QPixmap.grabWindow(self.modelEditor.winId()).save(filePath, 'jpg')
        self.__itemCreated =  filePath
        return filePath

    def __saveAndClose(self, *args):
        self.createSnapshot()
        self.close()
        self.deleteLater()

    def returnCreatedItem(self):
        return self.__itemCreated

    def hideEvent(self, event):
        QDialog.hideEvent(self, event)
        cmds.delete(self.cameraName)

def testUI():
    window_name = 'captureWindowTest'
    mainWindow = get_maya_window()

    if mainWindow:
        for child in mainWindow.children():
            if child.objectName() == window_name:
                child.close()
                child.deleteLater()
    window = CaptureWindow(mainWindow)
    window.setObjectName(window_name)
    window.setWindowTitle(window_name)
    window.setFixedSize(QSize(300, 400))
    window.exec_()

    return window

