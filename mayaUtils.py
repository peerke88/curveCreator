from maya import cmds
import os, tempfile
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
    filePath = os.path.join(tempfile.gettempdir(), "img%s"%inString[-1])
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