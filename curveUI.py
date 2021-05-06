from py23 import *
from qt_util import *
import os, re, stat, functools,shutil, platform, logging, 

import mayaWidget
import captureWindow

__VERSION__ = "3.0.20210506"
__MAYAVERSION = int(str(cmds.about(apiVersion=True))[:-2])
__FILE = os.path.dirname(__file__) 

class ControlUI(mayaWidget.DockWidget):

	toolName = 'Curve Tool: %s' % __VERSION__

	def __init__(self, newPlacement=False, parent=None):
		super(SkinningToolsUI, self).__init__(parent)

		self.setWindowIcon(QIcon(":/commandButton.png"))
        self.setupUi(self)


    def __ColorRgbCommand(self):
        self.removeableObjects = []
        if QT_VERSION == "pyqt4":
            parentlayout = OpenMayaUI.MQtUtil.fullName( long(sip.unwrapinstance(self.formColorLayout)) )
        else:
            parentlayout = OpenMayaUI.MQtUtil.fullName( long(shiboken.getCppPointer(self.formColorLayout)[0]) )
        self.colorSlider = cmds.colorSliderGrp( label='Color: ', rgb=(0, 0, 1), p=parentlayout )
        button = cmds.button( l='Set Color', parent=parentlayout, c=('import maya.cmds as cmds\nselection = cmds.ls(sl=True)\ncolorSet = cmds.colorSliderGrp("%s", q=True, rgb=True)\nfor select in selection:\n\tshapes = cmds.listRelatives(select,ad=True,s=True,f=True )\n\tfor node in shapes:\n\t\tcmds.setAttr(node + ".overrideRGBColors", 1)\n\t\tcmds.setAttr((node+".overrideEnabled"), 1)\n\t\tcmds.setAttr((node+".overrideColorRGB"), colorSet[0], colorSet[1], colorSet[2])'%self.colorSlider))

        self.removeableObjects.append(self.colorSlider)
        self.removeableObjects.append(button)

    def __ColorCurveCommand(self):
        self.colorList = [[0,[0.38, 0.38, 0.38], 'None'],    [1,[0.0, 0.0, 0.0]],         [2,[0.75, 0.75, 0.75]],
                          [3,[0.5, 0.5, 0.5]],               [4,[0.8, 0.0, 0.2]],         [5,[0.0, 0.0, 0.4]],
                          [6,[0.0, 0.0, 1.0]],               [7,[0.0, 0.3, 0.0]],         [8,[0.2, 0.0, 0.2]], 
                          [9,[0.8, 0.0, 0.8]],               [10,[0.6, 0.3, 0.2]],        [11,[0.25, 0.13, 0.13]],
                          [12,[0.7,0.2,0.0]],                [13,[1.0,0.0,0.0]],          [14,[0.0,1.0,0.0]], 
                          [15,[0.0,0.3,0.6]],                [16,[1.0,1.0,1.0]],          [17,[1.0,1.0,0.0]],
                          [18,[0.0,1.0,1.0]],                [19,[0.0,1.0,0.8]],          [20,[1.0,0.7,0.7]],
                          [21,[0.9,0.7,0.7]],                [22,[1.0,1.0,0.4]],          [23,[0.0,0.7,0.4]],
                          [24,[0.6,0.4,0.2]],                [25,[0.63,0.63,0.17]],       [26,[0.4,0.6,0.2]],
                          [27,[0.2,0.63,0.35]],              [28,[0.18,0.63,0.63]],       [29,[0.18,0.4,0.63]],
                          [30,[0.43,0.18,0.63]],             [31,[0.63,0.18,0.4]]]
                          
        self.removeableObjects = []    
        if QT_VERSION == "pyqt4":
            parentlayout = OpenMayaUI.MQtUtil.fullName( long(sip.unwrapinstance(self.formColorLayout)) )
        else:
            parentlayout = OpenMayaUI.MQtUtil.fullName( long(shiboken.getCppPointer(self.formColorLayout)[0]) )
        layout = cmds.gridLayout(numberOfColumns=8,cellWidthHeight=[45,25],parent=parentlayout)
        self.removeableObjects.append(layout)
        for i in self.colorList:
            if len(i) == 3:
                if self.mayaVersion < 2015:
                    button = cmds.button( l='None', bgc=tuple(i[1]),parent=layout, c=('import maya.cmds as cmds\nselection = cmds.ls(sl=True)\nfor select in selection:\n\tshapes = cmds.listRelatives(select,ad=True,s=True,f=True)\n\tfor node in shapes:\n\t\tcmds.setAttr((node+".overrideEnabled"), 0)'))
                else:    
                    button = cmds.button( l='None', bgc=tuple(i[1]),parent=layout, c=('import maya.cmds as cmds\nselection = cmds.ls(sl=True)\nfor select in selection:\n\tshapes = cmds.listRelatives(select,ad=True,s=True,f=True)\n\tfor node in shapes:\n\t\tcmds.setAttr(node + ".overrideRGBColors", 0)\n\t\tcmds.setAttr((node+".overrideEnabled"), 0)'))
            else:
                if self.mayaVersion < 2015:
                    button = cmds.button( l='', bgc=tuple(i[1]),parent=layout, c=('import maya.cmds as cmds\nselection = cmds.ls(sl=True)\nfor select in selection:\n\tshapes = cmds.listRelatives(select,ad=True,s=True,f=True )\n\tfor node in shapes:\n\t\tcmds.setAttr((node+".overrideEnabled"), 1)\n\t\tcmds.setAttr((node+".overrideColor"),' + str(i[0]) + ')'))
                else:  
                    button = cmds.button( l='', bgc=tuple(i[1]),parent=layout, c=('import maya.cmds as cmds\nselection = cmds.ls(sl=True)\nfor select in selection:\n\tshapes = cmds.listRelatives(select,ad=True,s=True,f=True )\n\tfor node in shapes:\n\t\tcmds.setAttr(node + ".overrideRGBColors", 0)\n\t\tcmds.setAttr((node+".overrideEnabled"), 1)\n\t\tcmds.setAttr((node+".overrideColor"),' + str(i[0]) + ')'))
            self.removeableObjects.append(button)