from maya import cmds, mel
import os, tempfile, stat
from functools import wraps

MAYAVERSION = int(str(cmds.about(apiVersion=True))[:-2])
_DEBUG = True
INDEXCOLORS = [[0.38, 0.38, 0.38], [0.0, 0.0, 0.0],   [0.75, 0.75, 0.75],
              [0.5, 0.5, 0.5],    [0.8, 0.0, 0.2],   [0.0, 0.0, 0.4],
              [0.0, 0.0, 1.0],    [0.0, 0.3, 0.0],   [0.2, 0.0, 0.2], 
              [0.8, 0.0, 0.8],    [0.6, 0.3, 0.2],   [0.25, 0.13, 0.13],
              [0.7,0.2,0.0],      [1.0,0.0,0.0],     [0.0,1.0,0.0], 
              [0.0,0.3,0.6],      [1.0,1.0,1.0],     [1.0,1.0,0.0],
              [0.0,1.0,1.0],      [0.0,1.0,0.8],     [1.0,0.7,0.7],
              [0.9,0.7,0.7],      [1.0,1.0,0.4],     [0.0,0.7,0.4],
              [0.6,0.4,0.2],      [0.63,0.63,0.1],   [0.4,0.6,0.2],
              [0.2,0.63,0.35],    [0.18,0.63,0.6],   [0.18,0.4,0.63],
              [0.43,0.18,0.63],   [0.63,0.18,0.4]]

def getSelection():
    return cmds.ls(sl=1, fl=1)

def hideUnselected(inBool):
    if inBool:
        mel.eval("HideUnselectedObjects;")
        return
    mel.eval("ShowLastHidden;");

def dec_undo(func):
    @wraps(func)
    def _undo_func(*args, **kwargs):
        try:
            cmds.undoInfo(ock=True)
            return func(*args, **kwargs)
        except Exception as e:
            if _DEBUG:
                print(e)
                print(e.__class__)
                print(sys.exc_info())
                cmds.warning(traceback.format_exc())
        finally:
            cmds.undoInfo(cck=True)
            
    return _undo_func

def setToolTips(inBool):
    cmds.help(popupMode=inBool)

def convertImageToString(inPath):
    with open(inPath, "rb") as imageFile:
        _str = base64.b64encode(imageFile.read())
    return [_str, os.path.splitext(inPath)[-1]]

def convertStringToImage(inString):
    filePath = os.path.join(tempfile.gettempdir(), "img{}".format(inString[-1]))
    with open(filePath, "wb") as fh:
        fh.write(inString[0].decode('base64'))
    return filePath

@dec_undo
def createTextController(inText, inFont):
    createdText = cmds.textCurves( f=inFont, t=inText )
    allDescendants = cmds.listRelatives( createdText[0], ad=True)
    shapeList = []
    for desc in allDescendants:
        if 'curve' in desc and 'Shape' not in desc:
            shapeList.append(desc)
    for index, shape in enumerate(shapeList):
        cmds.parent(shape,w=True)
        cmds.makeIdentity(shape, apply=True, t=1, r=1, s=1, n=0)
        if index == 0:
            parentGuide = shapeList[0]
            continue
    
        foundShape = cmds.listRelatives(shape, s=True) 
        cmds.move(0,0,0,(shape+'.scalePivot'),(shape+'.rotatePivot'))
        cmds.parent(foundShape,parentGuide,add=True,s=True)
        cmds.delete(shape)
    cmds.delete(createdText[0])
    cmds.xform(shapeList[0], cp=True)    
    worldPosition = cmds.xform(shapeList[0], q=True, piv=True, ws=True)
    cmds.xform(shapeList[0], t=(-worldPosition[0],-worldPosition[1],-worldPosition[2]))
    cmds.makeIdentity(shapeList[0], apply=True, t=1, r=1, s=1, n=0)
    cmds.select(shapeList[0])

@dec_undo
def CombineCurveShapes():
    selection  = cmds.ls(selection=True)
    for obj in selection:
        cmds.xform(obj, ws=True, piv = (0,0,0))

    cmds.makeIdentity(selection, apply=True, t=1, r=1, s=1, n=0)
    for index, obj in selection:
        if index == 0:
            continue
        shapeNode = cmds.listRelatives(obj, shapes=True)
        cmds.parent(shapeNode, selection[0], add=True, s=True)
        cmds.delete(obj)      
    cmds.select(base)  

@dec_undo
def setDisplayType(Type):
    selection         = cmds.ls(sl=True)
    if len(selection) == 0:
        cmds.warning("nothing selected")
    else:
        for Selected in selection:
            cmds.delete(Selected, ch=True)
            shapeNode = cmds.listRelatives(Selected,ad=True, s=True)
            for shapes in shapeNode:
                cmds.setAttr((shapes + ".overrideEnabled"), 1)
                cmds.setAttr((shapes + ".overrideDisplayType"), Type)
                if Type == 0:
                    cmds.setAttr((shapes + ".overrideEnabled"), 0)

@dec_undo
def setRgbColor(r, g, b, f):
    selection = cmds.ls(sl=True)
    if len(selection) == 0:
        cmds.warning("nothing selected")
    for select in selection:
        shapes = cmds.listRelatives(select,ad=True,s=True,f=True )
        for node in shapes:
            if f == 0:
                cmds.setAttr("{0}.overrideEnabled".format(node), 0)
                continue
            cmds.setAttr("{0}.overrideRGBColors".format(node), 1)
            cmds.setAttr("{0}.overrideEnabled".format(node), 1)
            cmds.setAttr("{0}.overrideColorRGB".format(node), r, g, b)

@dec_undo
def setIndexColor(index):
    selection = cmds.ls(sl=True)
    for select in selection:
        shapes = cmds.listRelatives(select, ad=True,s=True,f=True )
        for node in shapes:
            cmds.setAttr("{0}.overrideRGBColors".format(node), 0)
            if index == 0:
                cmds.setAttr("{0}.overrideEnabled".format(node), 0)
                continue
            cmds.setAttr("{0}.overrideEnabled".format(node), 1)
            cmds.setAttr("{0}.overrideColor".format(node), index)

def __fileWriteOrAdd(inFileName, inText, inWriteOption):                                                                                                                     
    if os.path.exists(inFileName):
        read_only_or_write_able = os.stat(inFileName)[0]
        if read_only_or_write_able != stat.S_IWRITE:
            os.chmod(inFileName, stat.S_IWRITE)

    file = open(inFileName, inWriteOption)
    file.write(inText)
    file.close()

def GetControler(inputCurve, curveDirectory, isChecked):
    cmds.delete(inputCurve, ch=True)


    directory = os.path.dirname(str(curveDirectory))
    if not os.path.exists(directory):
        os.makedirs(directory)

    baseText = 'import maya.cmds as cmds\n'
    __fileWriteOrAdd((curveDirectory), baseText, 'w')
    multipleShapes = False
    
    def completeList(input):
        childrenBase = cmds.listRelatives(input, ad=True, type="transform")
        childrenBase.append(input)
        childrenBase.reverse()
        return childrenBase

    childrenBase = cmds.listRelatives( inputCurve, ad=True, type="transform")
    if childrenBase:
        selection = completeList(inputCurve)
    else:
        selection = [inputCurve] 

    for inputCurve in selection:
        shapeNode = cmds.listRelatives(inputCurve, s=True, f=True)
        listdef = '%s = []\n'%inputCurve
        __fileWriteOrAdd((curveDirectory), listdef, 'a')

        for shapes in shapeNode:
            controlVerts      = cmds.getAttr(shapes+'.cv[*]')
            curveDegree       = cmds.getAttr(shapes+'.degree')
            period            = cmds.getAttr(shapes+'.f')
            localPosition     = cmds.getAttr(inputCurve+'.translate')
            worldPosition     = cmds.xform(inputCurve, q=True, piv=True, ws=True)
            
            infoNode = cmds.createNode('curveInfo')
            cmds.connectAttr((shapes + '.worldSpace'), (infoNode+'.inputCurve'))
            
            if len(shapeNode) > 1:
                multipleShapes = True
            
            list1 = []
            list2 = []
            list3 = []
            
            knots = cmds.getAttr(infoNode+'.knots')
            for i in knots[0]:
                list3.append(int(i))
            
            if isChecked:
                for i in range(len(controlVerts)):    
                    for j in range(3):
                        originCalculation     =  (float(controlVerts[i][j])-float(worldPosition[j]))
                        localSpaceAddition    =  originCalculation + float(localPosition[0][j])
                        list1.append(localSpaceAddition)
                    list2.append(list1)
                    list1=[]
            else:
                list2 = controlVerts
            
            if period == 0 :
                periodNode = ',per = False'
            else:
                periodNode = ',per = True'
                for i in range(curveDegree):
                    list2.append(list2[i])
            
            _points = str(list2).replace('[','(').replace(']',')').replace('((','[(').replace('))',')]')
            _knots = str(list3)
            CurveCreation = 'cmds.curve( p ={0}{1}, d={2}, k={3})'.format(_points, periodNode, curveDegree, _knots)
            CurveCreation = '{0}.append({1})'.format(inputCurve, CurveCreation)
            __fileWriteOrAdd((curveDirectory), str(CurveCreation+'\n'), 'a')
            
            cmds.delete(infoNode)
            
        if multipleShapes == True:
            End = 'for x in range(len({0})-1):\n\tcmds.makeIdentity({0}[x+1], apply=True, t=1, r=1, s=1, n=0)\n\tshapeNode = cmds.listRelatives({0}[x+1], shapes=True)\n\tcmds.parent(shapeNode, {0}[0], add=True, s=True)\n\tcmds.delete({0}[x+1])\n'.format(inputCurve)
            __fileWriteOrAdd((curveDirectory), End, 'a')
        
        parentObject = cmds.listRelatives(inputCurve, parent=True)
        if parentObject:
            listdef = 'cmds.parent({0}[0], {1}[0])\n'.format(inputCurve, parentObject[0])
            __fileWriteOrAdd((curveDirectory), listdef, 'a')
    
    close = 'fp = cmds.listRelatives({0}[0], f=True)[0]\npath = fp.split("|")[1]\ncmds.select(path)'.format(inputCurve)
    __fileWriteOrAdd((curveDirectory), close, 'a')