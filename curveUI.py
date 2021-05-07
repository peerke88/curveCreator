from curveCreator.py23 import *
from curveCreator.qt_util import *

import os, re, stat, shutil, platform, logging, tempfile, glob, warnings
from functools import partial
from maya import cmds

from curveCreator import mayaWidget
from curveCreator import captureWindow
from curveCreator import mayaUtils

__VERSION__ = "3.0.20210507"
_DIR = os.path.dirname(__file__) 
_CURVES = os.path.join(_DIR, 'Curves')

class ControlUI(mayaWidget.DockWidget):

    toolName = 'Curve Tool: %s' % __VERSION__

    def __init__(self, newPlacement=False, parent=None):
        super(ControlUI, self).__init__(parent)

        self.setWindowIcon(QIcon(":/commandButton.png"))
        self.setWindowTitle(self.__class__.toolName)

        self.__defaults()
        self.__uiElements()

        mainLayout = nullLayout(QVBoxLayout, None, 3)
        self.setLayout(mainLayout)

        self.__menuSetup()
        
        self.__header()
        self.__displayTypes()
        self.__saveAndText()
        self.__loadControllers()

        self.loadUIState()

    def __defaults(self):
        """ some default local variables for the current UI    
        """
        self.textInfo = {}
        mayaUtils.setToolTips(True)
        self.colorList = mayaUtils.INDEXCOLORS

    def __uiElements(self):
        """ several general UI elements that should be visible most of the times
        also loads the settings necessary for storing and retrieving information
        """
        _ini = os.path.join(_DIR,'settings.ini')
        self.settings = QSettings(_ini, QSettings.IniFormat)

    def __menuSetup(self):
        """ the menubar
        this will hold information on language, simple copy/paste(hold fetch) functionality and all the documentation/settings
        documentation will open specifically for the current open tab, next to that we also have a markingmenu button as this is available all the time
        """
        self.menuBar = QMenuBar(self)
        self.menuBar.setLayoutDirection(Qt.RightToLeft)
        helpAction = QAction('', self)
        helpAction.setIcon(QIcon(":/QR_help.png"))

        self.textInfo["docAction"] = QAction("UI documentation", self)
        

        self.changeLN = QMenu("en", self)
        languageFiles = os.listdir(os.path.join(_DIR, "languages"))
        for language in languageFiles:
            ac = QAction(language, self)
            self.changeLN.addAction(ac)
            ac.triggered.connect(self._changeLanguage)

        helpAction.triggered.connect(self._openDocHelp)
        
        self.menuBar.addAction(helpAction)
        self.menuBar.addMenu(self.changeLN)
        self.layout().setMenuBar(self.menuBar)

    def __header(self):
        headerLayout = nullLayout(QHBoxLayout, None, 0)
        headerLayout.addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
        headerButton = toolButton("{0}/icons/TextCurve.png".format(_DIR),0, QSize(87, 40))
        headerLayout.addWidget(headerButton)
        headerLayout.addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.layout().addLayout(headerLayout)
    
    def __displayTypes(self):
        self.textInfo["displayGB"] = QGroupBox("Display")
        groupBLayout = nullLayout(QVBoxLayout, None, 0)
        self.textInfo["displayGB"].setLayout(groupBLayout)

        hlay = nullLayout(QHBoxLayout, None, 0)
        self.textInfo["normalBtn"] = buttonsToAttach("Default", partial(mayaUtils.setDisplayType, 0))
        self.textInfo["templateBtn"] = buttonsToAttach("Template", partial(mayaUtils.setDisplayType, 1))
        self.textInfo["referenceBtn"] = buttonsToAttach("Reference", partial(mayaUtils.setDisplayType, 2))
        for btn in [self.textInfo["normalBtn"], self.textInfo["templateBtn"], self.textInfo["referenceBtn"]]:
            hlay.addWidget(btn)
        groupBLayout.addLayout(hlay)

        self.colorTab = QTabWidget()
        indexTab = QWidget()
        tab1 = self.colorTab.addTab(indexTab, "index")
        rgbTab = QWidget()
        tab2 = self.colorTab.addTab(rgbTab, "rgb")

        grid = nullLayout(QGridLayout, None, 0)
        indexTab.setLayout(grid)
        for index, color in enumerate(self.colorList):
            row = int(index/8.0)
            _btn = QPushButton()
            _btn.clicked.connect(partial(mayaUtils.setIndexColor, index))
            _btn.setStyleSheet("background-color:rgb({0},{1},{2})".format(color[0]*255, color[1]*255, color[2]*255));
            grid.addWidget(_btn, row, index - (8*row))
        grid.addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding), 4, 0)
        box = nullLayout(QVBoxLayout, None, 0)
        rgbTab.setLayout(box)
        colorPicker = ColorPicker()
        colorPicker.setOptions(QColorDialog.NoButtons | QColorDialog.DontUseNativeDialog)
        box.addWidget(colorPicker)
        box.addWidget(buttonsToAttach("Assign Color", partial(self.setRgbColor, colorPicker)))

        groupBLayout.addWidget(self.colorTab)

        self.layout().addWidget(self.textInfo["displayGB"])

    def __saveAndText(self):
        layout = nullLayout(QHBoxLayout, None, 0)
        self.layout().addLayout(layout)
        saveGB = QGroupBox("Save")
        textGB = QGroupBox("Text")

        for gb in [saveGB, textGB]:
            layout.addWidget(gb)

        saveLay = nullLayout(QVBoxLayout, None, 0)
        checkLay = nullLayout(QHBoxLayout, None, 0)
        self.useControlCheck = QCheckBox("Use curve name")
        self.centerCheck = QCheckBox("re-center the curve")
        for ck in [self.useControlCheck,self.centerCheck]:
            checkLay.addWidget(ck)
        saveLay.addLayout(checkLay)
        self.controlName = LineEdit() 
        self.controlName.setPlaceholderText("Give name to control...")
        def setEnabled(state): self.controlName.setEnabled(not state)
        self.useControlCheck.stateChanged.connect(setEnabled)
        self.useControlCheck.setChecked(True)
        self.centerCheck.setChecked(True)
        saveBtn = buttonsToAttach("Save Controller", self.__imageCreationWindow)
        self.controlName.allowText.connect(saveBtn.setEnabled)
        self.controlName.allowText.connect(self.useControlCheck.setEnabled)
        for btn in [self.controlName, saveBtn]:
            saveLay.addWidget(btn)
        saveGB.setLayout(saveLay)

        textLay = nullLayout(QVBoxLayout, None, 0)
        textInput = LineEdit(folderSpecific = False)
        textInput.setPlaceholderText("Create text Controller...")
        combo = QFontComboBox()
        combo.setCurrentFont(QFont("Arial"))
        textBtn = buttonsToAttach("Create Text", partial(self.__createText, textInput, combo))
        for btn in [textInput, combo, textBtn]:
            textLay.addWidget(btn)
        textGB.setLayout(textLay)

    def __loadControllers(self):
        loadGB = QGroupBox("Load")
        self.layout().addWidget(loadGB)

        box = nullLayout(QHBoxLayout, None, 0)
        self.controlTree = QTreeWidget()
        self.controlTree.setHeaderHidden(True)
        self.controlTree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.controlTree.setIconSize(QSize(30,30))
        self.controlTree.setIndentation(2)
        self.controlTree.itemSelectionChanged.connect(self.__handleChanged)
        self.controlTree.itemDoubleClicked.connect(self.__doubleClicked)
        box.addWidget(self.controlTree)
        vbox = nullLayout(QVBoxLayout, None, 0)
        self.iconButton = QLabel()
        self.iconButton.setMinimumSize(QSize(80, 80))
        self.iconButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        combineBtn = buttonsToAttach("combine curves", mayaUtils.CombineCurveShapes)
        deleteBtn = buttonsToAttach("delete", self._deletecontroller)
        for btn in [self.iconButton, combineBtn, deleteBtn]:
            vbox.addWidget(btn)
        
        box.addLayout(vbox)
        loadGB.setLayout(box)

        self.__readOutFiles()
            
    def setRgbColor(self, picker):
        r, g, b, f = picker.currentColor().getRgbF()
        mayaUtils.setRgbColor(r, g, b, f)
        
    def _openDocHelp(self):
        pass
    def _tooltipsCheck(self):
        pass
    def _changeLanguage(self, language):
        pass
    def _displayToolTip(self):
        pass

    def __imageCreationWindow(self, *args):
        selection = mayaUtils.getSelection()
        if len(selection) == 0:
            warnings.warn("no selection made!")
        else:
            for obj in selection:
                checked = self.useControlCheck.isChecked()
                if checked:
                    curvename = obj
                else:
                    InputText = self.controlName.displayText()
                    curvename = InputText

                # make sure none of the manipulators is shown
                _cap = captureWindow.CaptureWindow(self, os.path.join(_CURVES, "{}.png".format(curvename)))
                _cap.setFixedSize(QSize(300, 300))
                _cap.exec_()

                if _cap.returnCreatedItem() != False:
                    _path = os.path.join(_CURVES, "{}.py".format(curvename.split("|")[-1]))
                    mayaUtils.GetControler(obj, _path, self.centerCheck.isChecked())

                self.__readOutFiles()

    def __readOutFiles(self,*args):
        self.controlTree.clear()

        files = glob.glob(os.path.join(_CURVES, "*.py"))
        listing = []
        for file in files:
            listing.append(os.path.basename(file))
                
        for infile in listing:
            if not '.py' in infile:
                continue
            file = infile.split('.')

            f = open(os.path.join(_CURVES, infile), "r")
            text = f.read()

            item    = QTreeWidgetItem()
            item.setText(0, str(file[0]))
            try:
                icon = QIcon(os.path.join(_CURVES, "{0}.png".format(file[0]) ) )
                item.setIcon(0, icon)
            except Exception as e:
                pass
            self.controlTree.addTopLevelItem(item)  

    def __handleChanged(self):
        getItem = self.controlTree.selectedItems()
        if getItem == []:
            return
        inObject = getItem[0].text(0)
        try:
            icon = QPixmap(os.path.join(_CURVES, "{0}.png".format(inObject) ) )
            self.iconButton.setPixmap(icon)
        except Exception as e:
            pass

    def __doubleClicked(self):
        getItem = self.controlTree.selectedItems()
        if getItem == []:
            return
        
        inObject = getItem[0].text(0)
        f = open(os.path.join(_CURVES, "{0}.py".format(inObject) ), "r")
        text = f.read()
        exec (text)

    def _deletecontroller(self, *args):
        getItem = self.controlTree.selectedItems()
        
        if not getItem == []:
            inObject = getItem[0].text(0)
            for ext in ["png", "py"]:
                try:
                    os.remove(os.path.join(_CURVES, '{0}.{1}'.format(inObject, ext)))
                except Exception as e:
                    pass
            
        self.__readOutFiles()

    def __createText(self, textEdit, fontBox):
        InputText = textEdit.text()
        FontType  = fontBox.currentText()
        if str(InputText) == "":
            raise InputError("no text given!")
        else:
            mayaUtils.createTextController(str(InputText),str(FontType))


    def saveUIState(self):
        """ save the current state of the ui in a seperate ini file, this should also hold information later from a seperate settings window

        :todo: instead of only geometry also store torn of tabs for each posssible object
        :todo: save the geometries of torn of tabs as well
        """
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("tabs", self.colorTab.currentIndex())
        self.settings.setValue("language", self.changeLN.title())
        
    def loadUIState(self):
        """ load the previous set information from the ini file where possible, if the ini file is not there it will start with default settings
        """
        getGeo = self.settings.value("geometry", None)
        if not getGeo in [None, "None"]:
            self.restoreGeometry(getGeo)
        _tab = self.settings.value("tabs", 1)
        if _tab in ["0", 0]:
            _tab = 0
        else:
            _tab = 1
        self.colorTab.setCurrentIndex(_tab)

        self._changeLanguage(self.settings.value("language","en"))
        
    def hideEvent(self, event):
        """ the hide event is something that is triggered at the same time as close,
        sometimes the close event is not handled correctly by maya so we add the save state in here to make sure its always triggered
        :note: its only storing info so it doesnt break anything
        """
        self.saveUIState()
        
        super(ControlUI, self).hideEvent(event)

    def closeEvent(self, event):
        """ the close event, 
        we save the state of the ui but we also force delete a lot of the skinningtool elements,
        normally python would do garbage collection for you, but to be sure that nothing is stored in memory that does not get deleted we 
        force the deletion here as well. somehow this avoids crashes in maya!
        """
        self.saveUIState()
        self.deleteLater()
        return True

def showUI(newPlacement=False):
    """ convenience function to show the current user interface in maya,

    :param newPlacement: if `True` will force the tool to not read the ini file, if `False` will open the tool as intended
    :type newPlacement: bool
    """
    dock = ControlUI(newPlacement, parent = None)
    dock.run()
    return dock