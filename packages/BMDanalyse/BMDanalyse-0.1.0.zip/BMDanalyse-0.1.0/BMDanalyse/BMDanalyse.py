
import os
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget
import numpy as np
import scipy, sys, pickle
from pyqtgraph.graphicsItems.ROI import * 
import pyqtgraph.functions as fn
import PyQt4
import matplotlib
import matplotlib.pyplot as plt
import pyqtgraph.graphicsItems.ROI
pyqtgraph.graphicsItems.ROI.__all__.append('RectROIcustom1')
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
import pyqtgraph.exporters as exporters
from pyqtgraph.exporters.ImageExporter import ImageExporter 
import matplotlib_fix
import matplotlib.backends.qt4_editor.figureoptions as figureoptions
figureoptions.figure_edit = matplotlib_fix.figure_edit

absDirPath = os.path.dirname(__file__) 

class ImageExporterCustom(ImageExporter):

    """
    Subclass to change preferred image output to bmp. Currently there are some issues 
    with png, as it creates some lines around the image 
    """

    def __init__(self, item):
        ImageExporter.__init__(self,item)
    
    def export(self, fileName=None, toBytes=False, copy=False):
        if fileName is None and not toBytes and not copy:
            filter = ["*."+str(f) for f in QtGui.QImageWriter.supportedImageFormats()]
            preferred = ['*.bmp','*.png', '*.tif', '*.jpg']
            for p in preferred[::-1]:
                if p in filter:
                    filter.remove(p)
                    filter.insert(0, p)
            self.fileSaveDialog(filter=filter)
            return
            
        targetRect = QtCore.QRect(0, 0, self.params['width'], self.params['height'])
        sourceRect = self.getSourceRect()
        
        bg = np.empty((self.params['width'], self.params['height'], 4), dtype=np.ubyte)
        color = self.params['background']
        bg[:,:,0] = color.blue()
        bg[:,:,1] = color.green()
        bg[:,:,2] = color.red()
        bg[:,:,3] = color.alpha()
        self.png = pg.makeQImage(bg, alpha=True)
        
        origTargetRect = self.getTargetRect()
        resolutionScale = targetRect.width() / origTargetRect.width()
        
        painter = QtGui.QPainter(self.png)
        try:
            self.setExportMode(True, {'antialias': self.params['antialias'], 'background': self.params['background'], 'painter': painter, 'resolutionScale': resolutionScale})
            painter.setRenderHint(QtGui.QPainter.Antialiasing, self.params['antialias'])
            self.getScene().render(painter, QtCore.QRectF(targetRect), QtCore.QRectF(sourceRect))
        finally:
            self.setExportMode(False)
        painter.end()
        
        if copy:
            QtGui.QApplication.clipboard().setImage(self.png)
        elif toBytes:
            return self.png
        else:
            self.png.save(fileName)
   
   
class ViewBoxCustom2(pg.ViewBox):

    """
    Custom ViewBox used to over-ride the context menu. I don't want the full context menu, 
    just a view all and an export. Export does not call a dialog, just prompts user for filename.
    """

    def __init__(self,parent=None,border=None,lockAspect=False,enableMouse=True,invertY=False,enableMenu=True,name=None):
        pg.ViewBox.__init__(self,parent,border,lockAspect,enableMouse,invertY,enableMenu,name)
   
        self.menu = None # Override pyqtgraph ViewBoxMenu 
        self.menu = self.getMenu(None)       
        
    def raiseContextMenu(self, ev):
        if not self.menuEnabled(): return
        menu = self.getMenu(ev)
        pos  = ev.screenPos()
        menu.popup(QtCore.QPoint(pos.x(), pos.y()))
        
    def export(self):
        self.exp = ImageExporterCustom(self)
        self.exp.export()

    def getMenu(self,event):
        if self.menu is None:
            self.menu        = QMenuCustom()
            self.viewAll     = QtGui.QAction("View All", self.menu)
            self.exportImage = QtGui.QAction("Export image", self.menu)
            self.viewAll.triggered[()].connect(self.autoRange)
            self.exportImage.triggered[()].connect(self.export)
            self.menu.addAction(self.viewAll)
            self.menu.addAction(self.exportImage)
        return self.menu 

     
class QMenuCustom(QtGui.QMenu):
    """ Custum QMenu that closes on leaveEvent """
    def __init__(self,parent=None):
        QtGui.QMenu.__init__(self,parent)
    def leaveEvent(self,ev):
        self.hide()
      
  
class QActionCustom(QtGui.QAction):
    """ QAction class modified to emit a single argument (an event)"""
    clickEvent = QtCore.Signal(object)
    def __init__(self,name="",parent=None):
        QtGui.QAction.__init__(self,name,parent)
        self.triggered.connect(self.clicked)
        self.event = None
    def updateEvent(self,event):
        self.event = event
    def clicked(self):
        self.clickEvent.emit(self.event)        


class RectROIcustom1(ROI):

    sigRemoveRequested = QtCore.Signal(object)
    sigCopyRequested   = QtCore.Signal(object)
    sigSaveRequested   = QtCore.Signal(object)

    def __init__(self, pos, size, angle=0.0, **args):
        ROI.__init__(self, pos, size, angle, **args)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton or QtCore.Qt.RightButton) # Set to NoButton in parent class
        self.addScaleHandle([0.0, 0.5], [1.0, 0.5])
        self.addScaleHandle([1.0, 0.5], [0.0, 0.5])  
        self.addScaleHandle([0.5, 0.0], [0.5, 1.0])
        self.addScaleHandle([0.5, 1.0], [0.5, 0.0]) 
        self.addRotateHandle([0.0,0.0], [1.0, 1.0])
        self.addRotateHandle([0.0,1.0], [1.0, 0.0]) 
        self.addRotateHandle([1.0,0.0], [0.0, 1.0])
        self.addRotateHandle([1.0,1.0], [0.0, 0.0])  
        self.penActive   = fn.mkPen(  0, 255, 0)
        self.penInactive = fn.mkPen(255,   0, 0) 
        self.penHover    = fn.mkPen(255, 255, 0)   
        self.penActive.setWidth(1)
        self.penInactive.setWidth(1) 
        self.penHover.setWidth(1)   
        self.setName()
        self.isSelected = False
        self.menu = None
        
    def __lt__(self,other):
        selfid  = int(self.name.split('-')[-1])
        otherid = int(other.name.split('-')[-1])
        return selfid < otherid
        
    def setName(self,name=None):
        self.name = name
        
    def setSelected(self, s):
        QtGui.QGraphicsItem.setSelected(self, s)
        if s:
            self.isSelected   = True
            self.translatable = True
            self.setPen(self.penActive)
            for h in self.handles:
                h['item'].currentPen = self.penActive 
                h['item'].pen = h['item'].currentPen             
                h['item'].show()
                h['item'].update()
        else:
            self.isSelected   = False
            self.translatable = False
            self.setPen(self.penInactive)      
            for h in self.handles:
                h['item'].currentPen = self.penInactive 
                h['item'].pen = h['item'].currentPen               
                h['item'].hide()
                h['item'].update()
              
    def mouseDragEvent(self, ev):
        if ev.isStart():  
            # Drag using left button only if selected  
            if ev.button() == QtCore.Qt.LeftButton:
                if self.translatable:
                    self.isMoving = True
                    self.preMoveState = self.getState()
                    self.cursorOffset = self.pos() - self.mapToParent(ev.buttonDownPos())
                    self.sigRegionChangeStarted.emit(self)
                    ev.accept()
                else:
                    ev.ignore()
        elif ev.isFinish():
            if self.translatable:
                if self.isMoving:
                    self.stateChangeFinished()
                self.isMoving = False
            return
        if self.translatable and self.isMoving and ev.buttons() == QtCore.Qt.LeftButton:
            snap = True if (ev.modifiers() & QtCore.Qt.ControlModifier) else None
            newPos = self.mapToParent(ev.pos()) + self.cursorOffset
            self.translate(newPos - self.pos(), snap=snap, finish=False)
      
    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton and self.isMoving:
            ev.accept()
            self.cancelMove()
        elif ev.button() == QtCore.Qt.RightButton and self.contextMenuEnabled():
            self.raiseContextMenu(ev)
            ev.accept()
        elif int(ev.button() & self.acceptedMouseButtons()) > 0:
            ev.accept()
            self.sigClicked.emit(self, ev)
        else:
            ev.ignore()
    
    def contextMenuEnabled(self):
        return self.removable
    
    def raiseContextMenu(self, ev):
        if not self.contextMenuEnabled():
            return
        menu = self.getMenu()
        pos  = ev.screenPos()
        menu.popup(QtCore.QPoint(pos.x(), pos.y()))

    def getMenu(self):
        # Setup menu
        if self.menu is None:
            self.menu         = QMenuCustom()
            self.menuTitle    = QtGui.QAction(self.name,self.menu)
            self.copyAct      = QtGui.QAction("Copy", self.menu)
            self.saveAct      = QtGui.QAction("Save", self.menu)
            self.remAct       = QtGui.QAction("Remove", self.menu)            
            self.menu.actions = [self.menuTitle,self.copyAct,self.saveAct,self.remAct]
            # Connect signals to actions
            self.copyAct.triggered.connect(self.copyClicked)
            self.remAct.triggered.connect(self.removeClicked)
            self.saveAct.triggered.connect(self.saveClicked)
            # Add actions to menu
            self.menu.addAction(self.menuTitle)
            self.menu.addSeparator()
            for action in self.menu.actions[1:]:
                self.menu.addAction(action)
            # Set default properties
            self.menuTitle.setDisabled(True)
            self.menu.setStyleSheet("QMenu::item {color: black; font-weight:normal;}")
            font = QtGui.QFont()
            font.setBold(True)
            self.menuTitle.setFont(font)
        # Enable menus only for selected roi
        if self.isSelected:
            self.copyAct.setVisible(True) 
            self.saveAct.setVisible(True)
            self.remAct.setVisible(True)
        else:               
            self.copyAct.setVisible(False)
            self.saveAct.setVisible(False)
            self.remAct.setVisible(False)  
        return self.menu
       
    def removeClicked(self):
        self.sigRemoveRequested.emit(self) 
        
    def copyClicked(self):
        self.sigCopyRequested.emit(self) 
        
    def saveClicked(self):
        self.sigSaveRequested.emit(self) 

    def hoverEvent(self, ev):
        hover = False
        if not ev.isExit():
            if self.translatable and ev.acceptDrags(QtCore.Qt.LeftButton):
                hover=True
            for btn in [QtCore.Qt.LeftButton, QtCore.Qt.RightButton, QtCore.Qt.MidButton]:
                if int(self.acceptedMouseButtons() & btn) > 0 and ev.acceptClicks(btn):
                    hover=True
            if self.contextMenuEnabled():
                ev.acceptClicks(QtCore.Qt.RightButton)
        if hover:
            self.setMouseHover(True)
            self.sigHoverEvent.emit(self)
            ev.acceptClicks(QtCore.Qt.RightButton)
        else:
            self.setMouseHover(False)
            
    def setMouseHover(self, hover):
        if self.mouseHovering == hover:
            return
        self.mouseHovering = hover
        if hover:
            self.currentPen = self.penHover
        else:
            self.currentPen = self.pen
        self.update()   


class ViewMode():
    def __init__(self,id,cmap):
        self.id   = id
        self.cmap = cmap
        self.getLookupTable()
    def getLookupTable(self):        
        lut = [ [ int(255*val) for val in self.cmap(i)[:3] ] for i in xrange(256) ]
        lut = np.array(lut,dtype=np.ubyte)
        self.lut = lut     


class ViewBoxCustom(pg.ViewBox):

    sigROIchanged = QtCore.Signal(object)

    def __init__(self,parent=None,border=None,lockAspect=False,enableMouse=True,invertY=False,enableMenu=True,name=None):
        pg.ViewBox.__init__(self,parent,border,lockAspect,enableMouse,invertY,enableMenu,name)
        
        self.rois = []
        self.currentROIindex = None
        self.img      = None
        self.menu     = None # Override pyqtgraph ViewBoxMenu 
        self.menu     = self.getMenu(None)       
        self.NORMAL   = ViewMode(0,matplotlib.cm.bone)  
        self.DEXA     = ViewMode(1,matplotlib.cm.jet)
        self.viewMode = self.NORMAL
        
    def raiseContextMenu(self, ev):
        if not self.menuEnabled(): return
        menu = self.getMenu(ev)
        pos  = ev.screenPos()
        menu.popup(QtCore.QPoint(pos.x(), pos.y()))
        
    def export(self):
        self.exp = ImageExporterCustom(self)
        self.exp.export()

    def getMenu(self,event):
        if self.menu is None:
            self.menu        = QMenuCustom()
            self.addROIAct   = QActionCustom("Add ROI",  self.menu)
            self.loadROIAct  = QActionCustom("Load ROI", self.menu)
            self.dexaMode    = QtGui.QAction("DEXA mode", self.menu)
            self.viewAll     = QtGui.QAction("View All", self.menu)
            self.exportImage = QtGui.QAction("Export image", self.menu)
            self.addROIAct.clickEvent.connect(self.addRoiRequest)
            self.loadROIAct.clickEvent.connect(self.loadROI)
            self.dexaMode.toggled.connect(self.toggleViewMode)
            self.viewAll.triggered[()].connect(self.autoRange)
            self.exportImage.triggered[()].connect(self.export)
            self.menu.addAction(self.viewAll)
            self.menu.addAction(self.dexaMode)
            self.menu.addAction(self.exportImage)
            self.menu.addSeparator()
            self.menu.addAction(self.addROIAct)
            self.menu.addAction(self.loadROIAct)
            self.dexaMode.setCheckable(True)      
        # Update action event
        self.addROIAct.updateEvent(event)
        return self.menu  
        
    def setCurrentROIindex(self,roi=None):
        """ Use this function to change currentROIindex value to ensure a signal is emitted"""
        if roi==None: self.currentROIindex = None
        else:         self.currentROIindex = self.rois.index(roi)
        self.sigROIchanged.emit(roi)  

    def roiChanged(self,roi):
        self.sigROIchanged.emit(roi) 

    def getCurrentROIindex(self):
        return self.currentROIindex    
    
    def selectROI(self,roi):
        """ Selection control of ROIs """
        # If no ROI is currently selected (currentROIindex is None), select roi
        if self.currentROIindex==None:
            roi.setSelected(True)
            self.setCurrentROIindex(roi)
        # If an ROI is already selected...
        else:
            roiSelected = self.rois[self.currentROIindex]
            roiSelected.setSelected(False) 
            # If a different roi is already selected, then select roi 
            if self.currentROIindex != self.rois.index(roi):
                self.setCurrentROIindex(roi)
                roi.setSelected(True)
            # If roi is already selected, then unselect
            else: 
                self.setCurrentROIindex(None)   
                
    def addRoiRequest(self,ev):
        """ Function to addROI at an event screen position """
        # Get position
        sp = ev.screenPos() 
        sg = self.screenGeometry()      
        vr = self.viewRect()
        xfract = (sp.x()-sg.left()) / sg.width()
        yfract = (sp.y()-sg.top())  / sg.height()
        xpos   = vr.left()   + xfract * vr.width()
        ypos   = vr.bottom() - yfract * vr.height()
        # Shift down by size
        xr,yr = self.viewRange()
        xsize  = 0.25*(xr[1]-xr[0])
        ysize  = 0.25*(yr[1]-yr[0])
        xysize = min(xsize,ysize)
        if xysize==0: xysize=100       
        ypos -= xysize
        # Create ROI
        xypos = (xpos,ypos)
        self.addROI(pos=xypos)
        
    def addROI(self,pos=None,size=None,angle=0.0):
        """ Add an ROI to the ViewBox """    
        xr,yr = self.viewRange()
        if pos is None:
            posx = xr[0]+0.05*(xr[1]-xr[0])
            posy = yr[0]+0.05*(yr[1]-yr[0])
            pos  = [posx,posy]
        if size is None:
            xsize  = 0.25*(xr[1]-xr[0])
            ysize  = 0.25*(yr[1]-yr[0])
            xysize = min(xsize,ysize)
            if xysize==0: xysize=100
            size = [xysize,xysize]  
        roi = RectROIcustom1(pos,size,angle,removable=True,pen=(255,0,0))
        # Setup signals
        roi.setName('ROI-%i'% self.getROIid()) 
        roi.sigClicked.connect(self.selectROI)
        roi.sigRegionChanged.connect(self.roiChanged)
        roi.sigRemoveRequested.connect(self.removeROI)
        roi.sigCopyRequested.connect(self.copyROI)
        roi.sigSaveRequested.connect(self.saveROI)
        # Keep track of rois
        self.addItem(roi)
        self.rois.append(roi)
        self.selectROI(roi)
        self.sortROIs()  
        self.setCurrentROIindex(roi)

    def sortROIs(self):
        """ Sort self.rois and adjust self.currentROIindex as necessary """
        if len(self.rois)==0: return 
        if self.currentROIindex==None:
            self.rois.sort()  
        else:
            roiCurrent = self.rois[self.currentROIindex]
            self.rois.sort()  
            self.currentROIindex = self.rois.index(roiCurrent)
    
    def getROIid(self):
        """ Get available and unique number for ROI name """
        nums = [ int(roi.name.split('-')[-1]) for roi in self.rois if roi.name!=None ]
        nid  = 1
        if len(nums)>0: 
            while(True):
                if nid not in nums: break
                nid+=1
        return nid
        
    def copyROI(self,offset=0.0):
        """ Copy current ROI. Offset from original for visibility """
        if self.currentROIindex!=None:
            roi = self.rois[self.currentROIindex]
            roiState = roi.getState()
            pos   = roiState['pos']
            size  = roiState['size']
            angle = roiState['angle']
            # Offset position slightly
            offsetFraction = 0.02
            xr,yr  = self.viewRange()
            dx = offsetFraction*(xr[1]-xr[0])
            dy = offsetFraction*(yr[1]-yr[0])
            angleRadians = np.radians(angle) 
            cosa = np.cos(angleRadians)
            sina = np.sin(angleRadians)
            dxt  = dx*cosa - dy*sina
            dyt  = dx*sina + dy*cosa
            pos[0] = pos[0]+dxt
            pos[1] = pos[1]+dyt
            # Add copy
            self.addROI(pos,size,angle)
     
    def saveROI(self):
        """ Save the highlighted ROI to file """
        # NOTE: Not sure is this would be better in MainWindow        
        if self.currentROIindex!=None:
            roi = self.rois[self.currentROIindex]
            fileName = QtGui.QFileDialog.getSaveFileName(None,self.tr("Save ROI"),QtCore.QDir.currentPath(),self.tr("ROI (*.roi)"))
            if not fileName.isEmpty():
                pickle.dump( roi.saveState(), open( fileName, "wb" ) )
        
    def loadROI(self):
        """ Load a previously saved ROI from file """
        # NOTE: Not sure is this would be better in MainWindow
        fileName = QtGui.QFileDialog.getOpenFileName(None,self.tr("Load ROI"),QtCore.QDir.currentPath(),self.tr("ROI (*.roi)"))
        if not fileName.isEmpty():
            roiState = pickle.load( open(fileName, "rb") )
            self.addROI(roiState['pos'],roiState['size'],roiState['angle'])
            
    def removeROI(self):
        """ Delete the highlighted ROI """
        if self.currentROIindex!=None:
            roi = self.rois[self.currentROIindex]
            self.rois.pop(self.currentROIindex)
            self.removeItem(roi)  
            self.setCurrentROIindex(None) 

    def toggleViewMode(self,isChecked):
        """ Toggles between NORMAL (Black/White) and DEXA mode (colour) """
        if isChecked: viewMode = self.DEXA
        else:         viewMode = self.NORMAL
        self.setViewMode(viewMode)             
        
    def setViewMode(self,viewMode):
        self.viewMode = viewMode
        self.updateView()

    def updateView(self):
        self.background.setBrush(fn.mkBrush(self.viewMode.lut[0]))
        self.background.show()  
        if    self.img==None: return
        else: self.img.setLookupTable(self.viewMode.lut)            
       
    def showImage(self,arr):
        if arr==None: 
            self.img = None
            return
        if self.img==None: 
            self.img = pg.ImageItem(arr,autoRange=False,autoLevels=False)
            self.addItem(self.img)      
        self.img.setImage(arr,autoLevels=False)
        self.updateView()                    
        

class SidePanel(QtGui.QWidget):

    def __init__(self, parent=None):
    
        QtGui.QWidget.__init__(self,parent)
        
        self.setMinimumWidth(250)
        self.buttMinimumSize = QtCore.QSize(36,36)
        self.iconSize        = QtCore.QSize(24,24)         
        self.icons           = self.parent().icons
        
        self.setupImageToolbox()
        self.setupRoiToolbox()
        
        sidePanelLayout = QtGui.QVBoxLayout()
        sidePanelLayout.addWidget(self.imageToolbox)
        sidePanelLayout.addWidget(self.roiToolbox)        
        sidePanelLayout.setContentsMargins(0,0,0,0)
        self.setLayout(sidePanelLayout)             

    def setupImageToolbox(self):
    
        # Image filelist
        imageFileListLabel = QtGui.QLabel("Loaded images")
        self.imageFileList = QtGui.QListWidget() 
        
        # Image buttons
        self.buttImageAdd  = QtGui.QPushButton(self.icons['imageAddIcon'],"")
        self.buttImageRem  = QtGui.QPushButton(self.icons['imageRemIcon'],"")
        self.buttImageUp   = QtGui.QPushButton(self.icons['imageUpIcon'],"")
        self.buttImageDown = QtGui.QPushButton(self.icons['imageDownIcon'],"")
        imageButtons       = [self.buttImageAdd,self.buttImageRem,self.buttImageUp,self.buttImageDown]
        imageToolTips      = ['Add image(s)','Remove selected image','Move image down','Move image up']
        for i in xrange(len(imageButtons)): 
            image = imageButtons[i]
            image.setMinimumSize(self.buttMinimumSize)
            image.setIconSize(self.iconSize)
            image.setToolTip(imageToolTips[i])  

        self.imageFileTools  = QtGui.QFrame()
        imageFileToolsLayout = QtGui.QHBoxLayout() 
        self.imageFileTools.setLayout(imageFileToolsLayout) 
        self.imageFileTools.setLineWidth(1)
        self.imageFileTools.setFrameStyle(QtGui.QFrame.StyledPanel)            
        imageFileToolsLayout.addWidget(self.buttImageAdd)
        imageFileToolsLayout.addWidget(self.buttImageRem)        
        imageFileToolsLayout.addWidget(self.buttImageDown)
        imageFileToolsLayout.addWidget(self.buttImageUp)

        # Image Toolbox (containing imageFileList + imageFileList buttons)
        self.imageToolbox = QtGui.QFrame()
        self.imageToolbox.setLineWidth(2)
        self.imageToolbox.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
        imageToolboxLayout = QtGui.QVBoxLayout()
        self.imageToolbox.setLayout(imageToolboxLayout)       
        imageToolboxLayout.addWidget(imageFileListLabel)
        imageToolboxLayout.addWidget(self.imageFileList)         
        imageToolboxLayout.addWidget(self.imageFileTools)

    def setupRoiToolbox(self):   

        # ROI buttons
        self.buttRoiAdd  = QtGui.QPushButton(self.icons['roiAddIcon'],"")
        self.buttRoiRem  = QtGui.QPushButton(self.icons['roiRemIcon'],"")
        self.buttRoiSave = QtGui.QPushButton(self.icons['roiSaveIcon'],"")
        self.buttRoiCopy = QtGui.QPushButton(self.icons['roiCopyIcon'],"")        
        self.buttRoiLoad = QtGui.QPushButton(self.icons['roiLoadIcon'],"")
        roiButtons       = [self.buttRoiAdd, self.buttRoiRem,self.buttRoiSave,self.buttRoiCopy,self.buttRoiLoad]
        roiToolTips      = ['Add ROI','Delete ROI','Save ROI','Copy ROI','Load ROI']
        for i in xrange(len(roiButtons)): 
            button = roiButtons[i]
            button.setMinimumSize(self.buttMinimumSize)
            button.setIconSize(self.iconSize)
            button.setToolTip(roiToolTips[i])

        # ROI Buttons Frame       
        self.roiButtonsFrame = QtGui.QFrame()
        roiButtonsLayout     = QtGui.QHBoxLayout()
        self.roiButtonsFrame.setLayout(roiButtonsLayout)
        self.roiButtonsFrame.setLineWidth(1)
        self.roiButtonsFrame.setFrameStyle(QtGui.QFrame.StyledPanel)
        roiButtonsLayout.addWidget(self.buttRoiAdd)
        roiButtonsLayout.addWidget(self.buttRoiLoad) 
        roiButtonsLayout.addWidget(self.buttRoiCopy)
        roiButtonsLayout.addWidget(self.buttRoiSave)
        roiButtonsLayout.addWidget(self.buttRoiRem)
        
        # ROI Info Box
        self.roiInfoBox  = QtGui.QWidget()
        roiInfoBoxLayout = QtGui.QGridLayout()
        self.roiInfoBox.setLayout(roiInfoBoxLayout)
        self.roiNameLabel  = QtGui.QLabel("ROI name")
        self.roiNameValue  = QtGui.QLineEdit("")
        self.roiPosLabel   = QtGui.QLabel("ROI position")
        self.roiPosValue   = QtGui.QLineEdit("") 
        self.roiSizeLabel  = QtGui.QLabel("ROI size")
        self.roiSizeValue  = QtGui.QLineEdit("")  
        self.roiAngleLabel = QtGui.QLabel("ROI angle")
        self.roiAngleValue = QtGui.QLineEdit("")  
        roiInfoBoxLayout.addWidget(self.roiNameLabel,  0, 0)
        roiInfoBoxLayout.addWidget(self.roiNameValue,  0, 1)
        roiInfoBoxLayout.addWidget(self.roiPosLabel,   1, 0)
        roiInfoBoxLayout.addWidget(self.roiPosValue,   1, 1) 
        roiInfoBoxLayout.addWidget(self.roiSizeLabel,  2, 0)
        roiInfoBoxLayout.addWidget(self.roiSizeValue,  2, 1)    
        roiInfoBoxLayout.addWidget(self.roiAngleLabel, 3, 0)
        roiInfoBoxLayout.addWidget(self.roiAngleValue, 3, 1)           
        
        # ROI Toolbox
        self.roiToolbox  = QtGui.QFrame()
        roiToolboxLayout = QtGui.QVBoxLayout()
        self.roiToolbox.setLayout(roiToolboxLayout)
        self.roiToolbox.setLineWidth(2)
        self.roiToolbox.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)   
        roiToolboxLayout.addWidget(self.roiButtonsFrame)
        roiToolboxLayout.addWidget(self.roiInfoBox) 
      
    def addImageToList(self,filename):
        self.imageFileList.addItem(filename) 

    def moveImageUp(self):
        """ Move current item up the list """
        # Get current row
        currentRow = self.imageFileList.currentRow()
        # If no row is current, set first row as current
        if currentRow==-1: 
            self.imageFileList.setCurrentRow(0)
            currentRow = self.imageFileList.currentRow()
        # Do not move up list if already at the end
        if (currentRow+1) <= self.imageFileList.count()-1: 
            item = self.imageFileList.currentItem()
            self.imageFileList.takeItem(currentRow)
            self.imageFileList.insertItem(currentRow+1,item.text())
            self.imageFileList.setCurrentRow(currentRow+1)
        # Show current item as selected
        self.imageFileList.setItemSelected(self.imageFileList.currentItem(),True)
        
    def moveImageDown(self):
        """ Move current item down the list """ 
        # Get current row
        currentRow = self.imageFileList.currentRow()
        # If no row is current, set first row as current        
        if currentRow==-1: 
            self.imageFileList.setCurrentRow(0)  
            currentRow = self.imageFileList.currentRow()  
        # Do not move down list if already at the beginning    
        if (currentRow-1) >= 0:
            item = self.imageFileList.currentItem()
            self.imageFileList.takeItem(currentRow)
            self.imageFileList.insertItem(currentRow-1,item.text())
            self.imageFileList.setCurrentRow(currentRow-1)
        # Show current item as selected            
        self.imageFileList.setItemSelected(self.imageFileList.currentItem(),True)   

    def getListOfImages(self):
        """ Create a list of all items in the listWidget """
        items = []
        for index in xrange(self.imageFileList.count()):
            items.append(self.imageFileList.item(index))        
        return items
        
    def updateRoiInfoBox(self,name="",pos="",size="",angle=""):
        self.roiNameValue.setText(name)
        self.roiPosValue.setText(pos)
        self.roiSizeValue.setText(size)
        self.roiAngleValue.setText(angle)        
    
class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
    
        QtGui.QMainWindow.__init__(self, parent) 
        self.loadIcons()     
        self.setupUserInterface() 
        self.setupSignals()
        self.__version__='0.1.0'
        
        # Initialise variables
        self.imageFiles = {}
        self.timeData   = None
        self.plotWin    = None
        self.imageWin   = None
        self.BMDchange  = None
        self.roiNames   = None
        
    def loadIcons(self):
        """ Load icons """
        self.icons = dict([
            ('BMDanalyseIcon', QtGui.QIcon(os.path.join(absDirPath,"icons","logo.png"))),
            ('imageAddIcon',   QtGui.QIcon(os.path.join(absDirPath,"icons","file_add.png"))),
            ('imageRemIcon',   QtGui.QIcon(os.path.join(absDirPath,"icons","file_delete2.png"))),
            ('imageDownIcon',  QtGui.QIcon(os.path.join(absDirPath,"icons","arrow-up-2.ico"))),
            ('imageUpIcon',    QtGui.QIcon(os.path.join(absDirPath,"icons","arrow-down-2.ico"))),
            ('imagePrevIcon',  QtGui.QIcon(os.path.join(absDirPath,"icons","arrow-left.ico"))),
            ('imageNextIcon',  QtGui.QIcon(os.path.join(absDirPath,"icons","arrow-right.ico"))),          
            ('roiAddIcon',     QtGui.QIcon(os.path.join(absDirPath,"icons","green-add3.png"))),
            ('roiRemIcon',     QtGui.QIcon(os.path.join(absDirPath,"icons","red_delete.png"))),
            ('roiSaveIcon',    QtGui.QIcon(os.path.join(absDirPath,"icons","filesave.png"))),
            ('roiCopyIcon',    QtGui.QIcon(os.path.join(absDirPath,"icons","file_copy.png"))),
            ('roiLoadIcon',    QtGui.QIcon(os.path.join(absDirPath,"icons","opened-folder.png")))])
        
    def setupUserInterface(self):
        """ Initialise the User Interface """
        
        # Left frame
        leftFrame = QtGui.QFrame()
        leftFrameLayout = QtGui.QHBoxLayout() 
        leftFrame.setLayout(leftFrameLayout)
        leftFrame.setLineWidth(0)
        leftFrame.setFrameStyle(QtGui.QFrame.Panel)
        leftFrameLayout.setContentsMargins(0,0,5,0)

        # Left frame contents     
        self.viewMain = GraphicsLayoutWidget()  # A GraphicsLayout within a GraphicsView 
        leftFrameLayout.addWidget(self.viewMain)
        self.viewMain.setMinimumSize(200,200)
        self.vb = ViewBoxCustom(lockAspect=True,enableMenu=True)
        self.viewMain.addItem(self.vb)
        self.vb.disableAutoRange()
        
        # Right frame
        self.sidePanel = SidePanel(self) 
        
        # UI window (containing left and right frames)
        UIwindow         = QtGui.QWidget(self)
        UIwindowLayout   = QtGui.QHBoxLayout()
        UIwindowSplitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        UIwindowLayout.addWidget(UIwindowSplitter)
        UIwindow.setLayout(UIwindowLayout)
        self.setCentralWidget(UIwindow)
        UIwindowSplitter.addWidget(leftFrame)
        UIwindowSplitter.addWidget(self.sidePanel)  
   
        # Application window
        self.setWindowTitle('BMDanalyse')
        self.setWindowIcon(self.icons['BMDanalyseIcon'])
        self.setMinimumSize(600,500)
        self.resize(self.minimumSize())
        
        # Window menus       
        self.createMenus()
        self.createActions()  

    def createMenus(self):
        
        # Menus 
        menubar          = self.menuBar()
        self.fileMenu    = menubar.addMenu('&File')
        self.roiMenu     = menubar.addMenu('&ROIs')
        self.analyseMenu = menubar.addMenu('&Analyse')
        self.aboutMenu   = menubar.addMenu('A&bout')
        
    def createActions(self):    
       
        # Actions for File menu
        self.loadImageAct   = QtGui.QAction(self.icons['imageAddIcon'], "&Load image(s)",        self, shortcut="Ctrl+L")
        self.removeImageAct = QtGui.QAction(self.icons['imageRemIcon'], "&Remove current image", self, shortcut="Ctrl+X") 
        self.exitAct        = QtGui.QAction("&Quit", self, shortcut="Ctrl+Q",statusTip="Exit the application")
        fileMenuActions  = [self.loadImageAct,self.removeImageAct,self.exitAct]
        fileMenuActFuncs = [self.loadImages,self.removeImage,self.close]
        for i in xrange(len(fileMenuActions)):
            action   = fileMenuActions[i]
            function = fileMenuActFuncs[i]
            action.triggered[()].connect(function)
        self.fileMenu.addAction(self.loadImageAct)
        self.fileMenu.addAction(self.removeImageAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)        
        
        # Actions for ROI menu
        self.addRoiAct  = QtGui.QAction(self.icons['roiAddIcon'],  "&Add ROI",    self, shortcut="Ctrl+A")
        self.loadRoiAct = QtGui.QAction(self.icons['roiLoadIcon'], "L&oad ROI",   self, shortcut="Ctrl+O")                          
        self.copyRoiAct = QtGui.QAction(self.icons['roiCopyIcon'], "&Copy ROI",   self, shortcut="Ctrl+C")     
        self.saveRoiAct = QtGui.QAction(self.icons['roiSaveIcon'], "&Save ROI",   self, shortcut="Ctrl+S") 
        self.remRoiAct  = QtGui.QAction(self.icons['roiRemIcon'] , "&Remove ROI", self, shortcut="Ctrl+D")
        roiMenuActions  = [self.addRoiAct,self.loadRoiAct,self.copyRoiAct,self.saveRoiAct,self.remRoiAct]
        roiMenuActFuncs = [self.vb.addROI,self.vb.loadROI,self.vb.copyROI,self.vb.saveROI,self.vb.removeROI]
        for i in xrange(len(roiMenuActions)):
            action   = roiMenuActions[i]
            function = roiMenuActFuncs[i]
            action.triggered[()].connect(function)
            self.roiMenu.addAction(action)
              
        # Actions for Analyse menu
        self.roiAnalysisAct = QtGui.QAction("&ROI analysis", self.viewMain, shortcut="Ctrl+R",triggered=self.getBMD)
        self.imgAnalysisAct = QtGui.QAction("&Image analysis", self.viewMain, shortcut="Ctrl+I",triggered=self.imageAnalysis)
        self.analyseMenu.addAction(self.roiAnalysisAct) 
        self.analyseMenu.addAction(self.imgAnalysisAct)
        
        # Actions for 
        self.aboutAct = QtGui.QAction("&About", self.viewMain, shortcut='F1', triggered=self.onAbout)
        self.aboutMenu.addAction(self.aboutAct)

    def setupSignals(self):
        """ Setup signals """
        self.sidePanel.imageFileList.itemSelectionChanged.connect(self.getImageToDisplay)
        self.sidePanel.buttImageAdd.clicked.connect(self.loadImages)
        self.sidePanel.buttImageRem.clicked.connect(self.removeImage)
        self.sidePanel.buttImageUp.clicked.connect(self.sidePanel.moveImageUp)
        self.sidePanel.buttImageDown.clicked.connect(self.sidePanel.moveImageDown)
        self.sidePanel.buttRoiAdd.clicked[()].connect(self.vb.addROI)
        self.sidePanel.buttRoiCopy.clicked[()].connect(self.vb.copyROI)
        self.sidePanel.buttRoiRem.clicked.connect(self.vb.removeROI)        
        self.sidePanel.buttRoiLoad.clicked.connect(self.vb.loadROI)
        self.sidePanel.buttRoiSave.clicked.connect(self.vb.saveROI)
        self.vb.sigROIchanged.connect(self.updateROItools)
        
    def onAbout(self):
        """ About BMDanalyse message"""
        author  ='Michael Hogg'
        date    ='September 2012 - 2013'        
        version = self.__version__
        QtGui.QMessageBox.about(self, 'About BMDanalyse', 
            "<b>BMDanalyse</b>" + \
            "<p>A simple program for the analysis of a time " + \
            "series of Bone Mineral Density (BMD) images.</p>" + \
            "<p>Used to evaluate the bone gain / loss in a number of regions of interest (ROIs) " + \
            "over time, typically due to bone remodelling as a result of stress shielding around " + \
            "an orthopaedic implant.</p>" + \
            "<p>Author: " + author + "<br />" + \
            "Version: " + version + "<br />" + \
            "Date: " + date + "</p><br />")    

    def updateROItools(self,roi=None):
        """ Update ROI info box in side panel """ 
        #if self.vb.currentROIindex==None:
        #    self.sidePanel.updateRoiInfoBox()
        if roi==None:
            self.sidePanel.updateRoiInfoBox()
        else:           
            roiState    = roi.getState()
            posx,posy   = roiState['pos']
            sizex,sizey = roiState['size']
            angle       = roiState['angle']
            name  = roi.name
            pos   = '(%.3f, %.3f)' % (posx,posy)
            size  = '(%.3f, %.3f)' % (sizex,sizey)
            angle = '%.3f' % angle
            self.sidePanel.updateRoiInfoBox(name,pos,size,angle)  
    
    def loadImages(self):
        """ Load an image to be analysed """
        newImages = {}
        fileNames = QtGui.QFileDialog.getOpenFileNames(self, self.tr("Load images"),QtCore.QDir.currentPath())
        if len(fileNames)>0:
            for fileName in fileNames:
                if not fileName.isEmpty():
                    imgarr = scipy.misc.imread(str(fileName))
                    imgarr = imgarr.swapaxes(0,1)
                    if   imgarr.ndim==2: imgarr = imgarr[:,::-1]
                    elif imgarr.ndim==3: imgarr = imgarr[:,::-1,:]                   
                    newImages[fileName] = imgarr
            
            # Add filenames to list widget. Only add new filenames. If filename exists aready, then
            # it will not be added, but data will be updated
            for fileName in sorted(newImages.keys()):
                if not self.imageFiles.has_key(fileName):
                    self.sidePanel.addImageToList(fileName)
                self.imageFiles[fileName] = newImages[fileName]
            
            # Show image in Main window
            self.vb.enableAutoRange()
            if self.sidePanel.imageFileList.currentRow()==-1: self.sidePanel.imageFileList.setCurrentRow(0)
            self.showImage(self.sidePanel.imageFileList.currentItem().text())
            self.vb.disableAutoRange()            
            
    def removeImage(self):
        """ Remove image from sidePanel imageFileList """
        
        # Return if there is no image to remove
        if self.vb.img==None: return
        
        # Get current image in sidePanel imageFileList and remove from list
        currentRow = self.sidePanel.imageFileList.currentRow()
        image      = self.sidePanel.imageFileList.takeItem(currentRow)
        
        # Delete key and value from dictionary 
        if image!=None: del self.imageFiles[image.text()]
        
        # Get image item in imageFileList to replace deleted image
        if self.sidePanel.imageFileList.count()==0:
            self.vb.enableAutoRange()
            self.vb.removeItem(self.vb.img)
            self.vb.showImage(None)
            #self.vb.img = None
            self.vb.disableAutoRange()
        else: 
            currentRow = self.sidePanel.imageFileList.currentRow()
            image = self.sidePanel.imageFileList.item(currentRow)
            self.showImage(image.text())   

    def showImage(self,imageFilename):
        """ Shows image in main view """
        self.arr = self.imageFiles[imageFilename]
        self.vb.showImage(self.arr)
    
    def getImageToDisplay(self):
        """ Get current item in file list and display in main view"""
        try:    imageFilename = self.sidePanel.imageFileList.currentItem().text()
        except: pass
        else:   self.showImage(imageFilename)  

    def getBMD(self):
        """ Get change in BMD over time (e.g. for each image) for all ROIs. 
            
            Revised function that converts the list of images into a 3D array
            and then uses the relative position of the ROIs to the current
            image, self.vb.img, to get the average BMD value e.g. it doesn't use
            setImage to change the image in the view. This requires that all
            images are the same size and in the same position.
        """
        
        # Return if there is no image or rois in view
        if self.vb.img==None or len(self.vb.rois)==0: return               
        
        # Collect all images into a 3D array
        imageFilenames = self.sidePanel.getListOfImages()
        images    = [self.imageFiles[name.text()] for name in imageFilenames]
        imageData = np.dstack(images)
        numImages = len(images)           
        
        # Get BMD across image stack for each ROI
        numROIs = len(self.vb.rois)
        BMD     = np.zeros((numImages,numROIs),dtype=float) 
        self.roiNames = []   
        for i in xrange(numROIs):
            roi = self.vb.rois[i]
            self.roiNames.append(roi.name)
            arrRegion   = roi.getArrayRegion(imageData,self.vb.img, axes=(0,1))
            avgROIvalue = arrRegion.mean(axis=0).mean(axis=0)
            BMD[:,i]    = avgROIvalue
        
        # Calculate the BMD change (percentage of original)
        tol = 1.0e-06
        for i in xrange(numROIs):
            if abs(BMD[0,i])<tol: 
                BMD[:,i] = 100.
            else: 
                BMD[:,i] = BMD[:,i] / BMD[0,i] * 100.
        self.BMDchange = BMD
        if self.timeData==None or self.timeData.size!=numImages:
            self.timeData = np.arange(numImages,dtype=float)
        
        # Plot results  
        self.showResults()
        
    def imageAnalysis(self):
        # Generate images of BMD change
        if self.vb.img==None: return
        self.showImageWin()
        
    def sliderValueChanged(self,value):
        self.imageWin.sliderLabel.setText('BMD change: >= %d %s' % (value,'%'))
        self.setLookupTable(value)
        self.imageWin.vb.img2.setLookupTable(self.lut)
        
    def setLookupTable(self,val):
        lut = []
        for i in range(256):
            if   i > 127+val:
                #lut.append(matplotlib.cm.RdBu_r(255))
                lut.append(matplotlib.cm.jet(255))
            elif i < 127-val:    
                lut.append(matplotlib.cm.jet(0))
            else:
                lut.append((0.0,0.0,0.0,0.0)) 
        lut = np.array(lut)*255
        self.lut = np.array(lut,dtype=np.ubyte)
 
    def newFunc(self):
    
        self.buttMinimumSize = QtCore.QSize(110,36)
        self.iconSize = QtCore.QSize(24,24)
        
        if self.imageWin==None:
            
            self.imageWin = QtGui.QDialog(self, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint |  \
                                          QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)
            self.imageWin.setWindowTitle('BMDanalyse')
            self.imageWin.setWindowIcon(self.icons['BMDanalyseIcon'])
            self.imageWin.setMinimumSize(250,500)
            self.imageWin.resize(self.imageWin.minimumSize()) 
            
            # Create viewBox  
            self.imageWin.glw = GraphicsLayoutWidget()  # A GraphicsLayout within a GraphicsView 
            #self.imageWin.vb  = pg.ViewBox(lockAspect=True,enableMenu=True)
            self.imageWin.vb  = ViewBoxCustom2(lockAspect=True,enableMenu=True)
            self.imageWin.vb.disableAutoRange()
            self.imageWin.glw.addItem(self.imageWin.vb) 
            arr = self.imageFiles.values()[0]
            self.imageWin.vb.img1 = pg.ImageItem(arr,autoRange=False,autoLevels=False)
            self.imageWin.vb.addItem(self.imageWin.vb.img1)      
            self.imageWin.vb.img2 = pg.ImageItem(None,autoRange=False,autoLevels=False)
            self.imageWin.vb.addItem(self.imageWin.vb.img2)
            self.imageWin.vb.autoRange()
            lut = [ [ int(255*val) for val in matplotlib.cm.bone(i)[:3] ] for i in xrange(256) ]
            lut = np.array(lut,dtype=np.ubyte)         
            self.imageWin.vb.img1.setLookupTable(lut)
            
            # Create buttons to select images
            self.imageWin.buttCont = QtGui.QWidget()
            self.imageWin.buttPrev = QtGui.QPushButton(self.icons['imagePrevIcon'],"")
            self.imageWin.buttNext = QtGui.QPushButton(self.icons['imageNextIcon'],"")
            self.buttLayout = QtGui.QHBoxLayout()
            self.buttLayout.addStretch(1)
            self.buttLayout.addWidget(self.imageWin.buttPrev)
            self.buttLayout.addWidget(self.imageWin.buttNext)
            self.buttLayout.addStretch(1)
            self.imageWin.buttCont.setLayout(self.buttLayout)
            self.imageWin.buttPrev.setMinimumSize(self.buttMinimumSize)
            self.imageWin.buttNext.setMinimumSize(self.buttMinimumSize)
            self.imageWin.buttPrev.setIconSize(self.iconSize) 
            self.imageWin.buttNext.setIconSize(self.iconSize)
            self.buttLayout.setContentsMargins(0,5,0,5)
            
            self.imageWin.buttPrev.clicked.connect(self.prevImage)
            self.imageWin.buttNext.clicked.connect(self.nextImage)
            
            # Create slider    
            self.imageWin.sliderCon = QtGui.QWidget()
            self.imageWin.slider = QtGui.QSlider(self)
            self.imageWin.slider.setOrientation(QtCore.Qt.Horizontal)
            self.imageWin.slider.setMinimum(1)
            self.imageWin.slider.setMaximum(100)
            self.imageWin.slider.setMinimumWidth(100)
            self.imageWin.slider.valueChanged.connect(self.sliderValueChanged)
            self.imageWin.sliderLabel = QtGui.QLabel('1')
            self.imageWin.sliderLabel.setMinimumWidth(120)
            self.sliderLayout = QtGui.QHBoxLayout()
            self.sliderLayout.addStretch(1)
            self.sliderLayout.addWidget(self.imageWin.sliderLabel)
            self.sliderLayout.addWidget(self.imageWin.slider)
            self.sliderLayout.addStretch(1)
            self.imageWin.sliderCon.setLayout(self.sliderLayout)
            self.sliderLayout.setContentsMargins(0,0,0,5)
            
            # Format image window
            self.imageWinLayout = QtGui.QVBoxLayout()
            self.imageWinLayout.addWidget(self.imageWin.glw)
            self.imageWinLayout.addWidget(self.imageWin.buttCont)
            self.imageWinLayout.addWidget(self.imageWin.sliderCon)
            self.imageWin.setLayout(self.imageWinLayout)
            
            self.imageWin.imagesRGB = None
            self.imageWinIndex = 0
            
        # Show
        self.imageWin.show()
        self.imageWin.slider.setValue(10)
        self.sliderValueChanged(10)
        
    def prevImage(self):
        numImages = len(self.imageFiles)
        minIndex  = 0
        currIndex = self.imageWinIndex 
        prevIndex = currIndex - 1 
        self.imageWinIndex = max(prevIndex,minIndex)    
        self.updateImageWin()
        
    def nextImage(self):
        numImages = len(self.imageFiles)
        maxIndex  = numImages - 1
        currIndex = self.imageWinIndex
        nextIndex = currIndex + 1 
        self.imageWinIndex = min(nextIndex,maxIndex)
        self.updateImageWin()
        
    def updateImageWin(self):
        imageFilenames = self.sidePanel.getListOfImages()
        imageName      = imageFilenames[self.imageWinIndex]
        self.imageWin.vb.img1.setImage(self.imageFiles[imageName.text()],autoLevels=False) 
        self.imageWin.vb.img2.setImage(self.imageWin.imagesRGB[self.imageWinIndex],autoLevels=False) 
        
    def showImageWin(self):
        self.newFunc()
        if self.imageWin.imagesRGB == None: self.imagesBMDpercentChange()
        self.updateImageWin()

    def imagesBMDpercentChange(self):
        
        # Get image arrays and convert to an array of floats
        imageFilenames = self.sidePanel.getListOfImages()
        images         = [ self.imageFiles[name.text()] for name in imageFilenames ]
        imagesConv = []
        for img in images: 
            image = img.copy()
            image[np.where(image==0)] = 1
            image = image.astype(np.float)
            imagesConv.append(image)
               
        # Calculate percentage change and set with limits -100% to +100%
        imagesPercCh = []
        imageInitial = imagesConv[0]
        for image in imagesConv:
            imagePercCh = (image-imageInitial)/imageInitial*100.
            imagePercCh[np.where(imagePercCh> 100.)] =  100.
            imagePercCh[np.where(imagePercCh<-100.)] = -100.
            imagesPercCh.append(imagePercCh)
            
        numImages  = len(imagesPercCh)
        self.imageWin.imagesRGB = []    
        for i in xrange(numImages):
            image = imagesPercCh[i]
            sx,sy = image.shape 
            imageCh  = np.zeros((sx,sy),dtype=np.float)
            imageRGB = image*(255/200.)+(255/2.)
            self.imageWin.imagesRGB.append(imageRGB)
        
    def BMDtoCSVfile(self):
        """ Write BMD change to csv file """
        fileName = QtGui.QFileDialog.getSaveFileName(None,self.tr("Export to CSV"),QtCore.QDir.currentPath(),self.tr("CSV (*.csv)"))
        if not fileName.isEmpty():               
            textFile  = open(fileName,'w')
            numFrames, numROIs = self.BMDchange.shape    
            roiNames = self.roiNames
            header  = "%10s," % 'Time'
            header += ((numROIs-1)*'%10s,'+'%10s\n') % tuple(roiNames)
            textFile.write(header)
            for i in xrange(numFrames):
                textFile.write('%10.1f,' % self.timeData[i])
                for j in xrange(numROIs):
                    if j<numROIs-1: fmt = '%10.3f,'
                    else:           fmt = '%10.3f\n'
                    textFile.write(fmt % self.BMDchange[i,j])
            textFile.close()       

    def showResults(self,):
        """ Plots BMD change using matplotlib """
        # Create plot window       
        if self.plotWin==None:
            self.plotWin = QtGui.QDialog(self, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint |  \
                                         QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)
            self.plotWin.setWindowTitle('BMDanalyse')
            self.plotWin.setWindowIcon(self.icons['BMDanalyseIcon'])
            self.plotWin.setMinimumSize(600,500)
            self.plotWin.resize(self.minimumSize()) 

            # Create Matplotlib widget
            self.mplw = MatplotlibWidget(size=(5,6))
            self.fig  = self.mplw.getFigure()
        
            self.editDataButton  = QtGui.QPushButton('Edit plot')
            self.exportCSVButton = QtGui.QPushButton('Export data')
            self.mplw.toolbar.addWidget(self.editDataButton)
            self.mplw.toolbar.addWidget(self.exportCSVButton)
            self.editDataButton.clicked.connect(self.showEditBox)
            self.exportCSVButton.clicked.connect(self.BMDtoCSVfile)

            # Format plot window
            self.plotWinLayout = QtGui.QVBoxLayout()
            self.plotWinLayout.addWidget(self.mplw)
            self.plotWin.setLayout(self.plotWinLayout)
        
        self.createFigure()
        self.plotWin.show()
        self.mplw.draw()
        
    def createFigure(self):
        """ Creates plot of results """
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.clear()
        self.fig.subplots_adjust(bottom=0.15,top=0.85,left=0.15,right=0.925)
        numFrames, numROIs = self.BMDchange.shape
        t = self.timeData
        # Plot data
        for i in xrange(numROIs):
            roiname = self.roiNames[i]
            self.ax1.plot(t,self.BMDchange[:,i],'-o',label=roiname,linewidth=2.0)
        kwargs = dict(y=1.05)  # Or kwargs = {'y':1.05}
        self.ax1.set_title('Change in Bone Mineral Density over time',fontsize=14,fontweight='roman',**kwargs)
        self.ax1.set_xlabel('Time',fontsize=10)
        self.ax1.set_ylabel('Change in BMD (%)',fontsize=10)
        self.ax1.legend(loc=0)
        plt.setp(self.ax1.get_xmajorticklabels(),  fontsize=10)
        plt.setp(self.ax1.get_ymajorticklabels(),  fontsize=10)
        plt.setp(self.ax1.get_legend().get_texts(),fontsize=10)  
        self.ax1.grid()  

    def fillEditBox(self):
        rows,cols = self.BMDchange.shape
        for i in xrange(rows):
            itmValue = '%.2f' % self.timeData[i]
            itm      = QtGui.QTableWidgetItem(itmValue)
            self.tableResults.setItem(i,0,itm)
            for j in xrange(cols):
                itmValue = '%.2f' % self.BMDchange[i,j]
                itm = QtGui.QTableWidgetItem(itmValue)
                self.tableResults.setItem(i,j+1,itm)

    def showEditBox(self):
        self.plotWin.editBox = QtGui.QDialog(self.plotWin, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.plotWin.editBox.setWindowIcon(self.icons['BMDanalyseIcon']) 
        self.plotWin.editBox.setWindowTitle('BMDanalyse') 
        self.plotWin.editBox.setModal(True)
        # Add table
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(10,10,10,10)
        layout.setSpacing(20)
        rows,cols = self.BMDchange.shape
        self.tableResults = MyTableWidget(rows,cols+1,self.plotWin.editBox)
        self.tableResults.verticalHeader().setVisible(True)
        # Set headers
        self.tableResults.setHorizontalHeaderItem(0,QtGui.QTableWidgetItem('Time'))
        for i in xrange(cols):
            header = QtGui.QTableWidgetItem(self.roiNames[i])
            self.tableResults.setHorizontalHeaderItem(i+1,header)
        # Add values to table
        self.fillEditBox()
        # Set layout
        layout.addWidget(self.tableResults)
        self.buttonsFrame  = QtGui.QFrame()
        self.buttonsLayout = QtGui.QHBoxLayout()
        self.buttonReset   = QtGui.QPushButton('Reset')
        self.buttonSave    = QtGui.QPushButton('Save')
        self.buttonClose   = QtGui.QPushButton('Cancel')
        self.buttonReset.setFixedWidth(50)
        self.buttonSave.setFixedWidth(50)
        self.buttonClose.setFixedWidth(50)
        self.buttonClose.clicked.connect(self.plotWin.editBox.close)
        self.buttonSave.clicked.connect(self.updateTableValues)
        self.buttonReset.clicked.connect(self.fillEditBox)
        self.buttonsLayout.addStretch(1)
        self.buttonsLayout.addWidget(self.buttonReset)
        self.buttonsLayout.addWidget(self.buttonSave)
        self.buttonsLayout.addWidget(self.buttonClose) 
        self.buttonsLayout.setContentsMargins(0,0,0,0) 
        self.buttonsFrame.setLayout(self.buttonsLayout)
        layout.addWidget(self.buttonsFrame)
        self.plotWin.editBox.setLayout(layout)
        self.plotWin.editBox.setMaximumSize(layout.sizeHint())
        self.plotWin.editBox.show()
        
    def updateTableValues(self):        
        # Create temporary arrays
        timeData  = self.timeData.copy()
        BMDchange = self.BMDchange.copy() 
        # Put the values from the tables into the temporary arrays
        rows = self.tableResults.rowCount()
        cols = self.tableResults.columnCount()
        for r in xrange(rows):
            for c in xrange(cols):
                item      = self.tableResults.item(r,c)
                itemValue = float(item.text())
                if c==0:
                    timeData[r] = itemValue 
                else: 
                    BMDchange[r,c-1] = itemValue
        # Check that time values are in increasing order. If so, then update arrays
        if any(np.diff(timeData)<=0):
            self.errorMessage = QtGui.QMessageBox()
            self.errorMessage.setWindowIcon(self.icons['BMDanalyseIcon'])
            self.errorMessage.setWindowTitle('BMDanalyse')
            self.errorMessage.setText('Input error: Time values should be in order of increasing value')
            self.errorMessage.setIcon(QtGui.QMessageBox.Warning)           
            self.errorMessage.open()         
        else:         
            self.timeData  = timeData
            self.BMDchange = BMDchange
            self.createFigure()
            self.mplw.draw()
            self.plotWin.editBox.close()


class MyTableWidget(QtGui.QTableWidget):  
    def __init__(self, x, y, parent = None):
        super(MyTableWidget, self).__init__(x, y, parent)

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.itemChanged.connect(self.tableItemChanged)
        self.currentItemChanged.connect(self.tableUpdateItemText)
        self.currentItemText = None
        
        self.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        hh = self.horizontalHeader()
        hh.setDefaultSectionSize(125)
        vh = self.verticalHeader()
        vh.setDefaultSectionSize(25) 
        
    def tableUpdateItemText(self,itemCurr,itemPrev):
        self.currentItemText = itemCurr.text()
        
    def tableItemChanged(self,item):
        self.errorMessage = QtGui.QMessageBox()
        try: 
            itemValue = float(item.text())
        except: 
            if self.currentItemText!=None: item.setText(self.currentItemText)
            icon = self.parent().windowIcon()
            self.errorMessage.setWindowIcon(icon)
            self.errorMessage.setWindowTitle('BMDanalyse')
            self.errorMessage.setText('Input error: Value must be a number')
            self.errorMessage.setIcon(QtGui.QMessageBox.Warning)           
            self.errorMessage.open()            
        else:
            item.setText('%.2f' % itemValue)
            self.currentItemText = item.text()
       
    def sizeHint(self):
        margins = self.contentsMargins()
        hh      = self.horizontalHeader()
        vh      = self.verticalHeader()
        hsb     = self.horizontalScrollBar()
        vsb     = self.verticalScrollBar()
        vsb.setMaximumWidth(17)
        hsb.setMaximumHeight(17)
        numCols, numRows = (2,15)
        width  = numCols * hh.defaultSectionSize() + margins.left() + margins.right()  + vh.width()  + vsb.width()
        height = numRows * vh.defaultSectionSize() + margins.top()  + margins.bottom() + hh.height() + hsb.height()
        return QtCore.QSize(width, height)
        
def run():
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
