from pyqtgraph.Qt import QtGui, QtCore
from scipy.fftpack import fft
import numpy as np
import scipy.stats
from .GraphicsObject import GraphicsObject
import pyqtgraph.functions as fn
from pyqtgraph import debug
from pyqtgraph.Point import Point
import pyqtgraph as pg
import struct, sys

__all__ = ['PlotCurveItem']
class PlotCurveItem(GraphicsObject):
    
    
    """
    Class representing a single plot curve. Instances of this class are created
    automatically as part of PlotDataItem; these rarely need to be instantiated
    directly.
    
    Features:
    
    - Fast data update
    - FFT display mode (accessed via PlotItem context menu)
    - Fill under curve
    - Mouse interaction
    
    ====================  ===============================================
    **Signals:**
    sigPlotChanged(self)  Emitted when the data being plotted has changed
    sigClicked(self)      Emitted when the curve is clicked
    ====================  ===============================================
    """
    
    sigPlotChanged = QtCore.Signal(object)
    sigClicked = QtCore.Signal(object)
    
    def __init__(self, *args, **kargs):
        """
        Forwards all arguments to :func:`setData <pyqtgraph.PlotCurveItem.setData>`.
        
        Some extra arguments are accepted as well:
        
        ==============  =======================================================
        **Arguments:**
        parent          The parent GraphicsObject (optional)
        clickable       If True, the item will emit sigClicked when it is 
                        clicked on. Defaults to False.
        ==============  =======================================================
        """
        GraphicsObject.__init__(self, kargs.get('parent', None))
        self.clear()
        self.path = None
        self.fillPath = None
        
            
        ## this is disastrous for performance.
        #self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)
        
        self.metaData = {}
        self.opts = {
            'pen': fn.mkPen('w'),
            'shadowPen': None,
            'fillLevel': None,
            'brush': None,
            'stepMode': False,
            'name': None,
            'antialias': pg.getConfigOption('antialias'),
        }
        self.setClickable(kargs.get('clickable', False))
        self.setData(*args, **kargs)
        
    def implements(self, interface=None):
        ints = ['plotData']
        if interface is None:
            return ints
        return interface in ints
    
    def setClickable(self, s):
        """Sets whether the item responds to mouse clicks."""
        self.clickable = s
        
        
    def getData(self):
        return self.xData, self.yData
        
    def dataBounds(self, ax, frac=1.0, orthoRange=None):
        (x, y) = self.getData()
        if x is None or len(x) == 0:
            return (0, 0)
            
        if ax == 0:
            d = x
            d2 = y
        elif ax == 1:
            d = y
            d2 = x

        if orthoRange is not None:
            mask = (d2 >= orthoRange[0]) * (d2 <= orthoRange[1])
            d = d[mask]
            d2 = d2[mask]

            
        if frac >= 1.0:
            return (d.min(), d.max())
        elif frac <= 0.0:
            raise Exception("Value for parameter 'frac' must be > 0. (got %s)" % str(frac))
        else:
            return (scipy.stats.scoreatpercentile(d, 50 - (frac * 50)), scipy.stats.scoreatpercentile(d, 50 + (frac * 50)))
            
    def setPen(self, *args, **kargs):
        """Set the pen used to draw the curve."""
        self.opts['pen'] = fn.mkPen(*args, **kargs)
        self.update()
        
    def setShadowPen(self, *args, **kargs):
        """Set the shadow pen used to draw behind tyhe primary pen.
        This pen must have a larger width than the primary 
        pen to be visible.
        """
        self.opts['shadowPen'] = fn.mkPen(*args, **kargs)
        self.update()

    def setBrush(self, *args, **kargs):
        """Set the brush used when filling the area under the curve"""
        self.opts['brush'] = fn.mkBrush(*args, **kargs)
        self.update()
        
    def setFillLevel(self, level):
        """Set the level filled to when filling under the curve"""
        self.opts['fillLevel'] = level
        self.fillPath = None
        self.update()

    #def setColor(self, color):
        #self.pen.setColor(color)
        #self.update()
        
    #def setAlpha(self, alpha, auto):
        #self.opts['alphaHint'] = alpha
        #self.opts['alphaMode'] = auto
        #self.update()
        
    #def setSpectrumMode(self, mode):
        #self.opts['spectrumMode'] = mode
        #self.xDisp = self.yDisp = None
        #self.path = None
        #self.update()
    
    #def setLogMode(self, mode):
        #self.opts['logMode'] = mode
        #self.xDisp = self.yDisp = None
        #self.path = None
        #self.update()
    
    #def setPointMode(self, mode):
        #self.opts['pointMode'] = mode
        #self.update()
        

    #def setDownsampling(self, ds):
        #if self.opts['downsample'] != ds:
            #self.opts['downsample'] = ds
            #self.xDisp = self.yDisp = None
            #self.path = None
            #self.update()

    def setData(self, *args, **kargs):
        """
        ==============  ========================================================
        **Arguments:**
        x, y            (numpy arrays) Data to show 
        pen             Pen to use when drawing. Any single argument accepted by
                        :func:`mkPen <pyqtgraph.mkPen>` is allowed.
        shadowPen       Pen for drawing behind the primary pen. Usually this
                        is used to emphasize the curve by providing a 
                        high-contrast border. Any single argument accepted by
                        :func:`mkPen <pyqtgraph.mkPen>` is allowed.
        fillLevel       (float or None) Fill the area 'under' the curve to
                        *fillLevel*
        brush           QBrush to use when filling. Any single argument accepted
                        by :func:`mkBrush <pyqtgraph.mkBrush>` is allowed.
        antialias       (bool) Whether to use antialiasing when drawing. This
                        is disabled by default because it decreases performance.
        ==============  ========================================================
        
        If non-keyword arguments are used, they will be interpreted as
        setData(y) for a single argument and setData(x, y) for two
        arguments.
        
        
        """
        self.updateData(*args, **kargs)
        
    def updateData(self, *args, **kargs):
        prof = debug.Profiler('PlotCurveItem.updateData', disabled=True)

        if len(args) == 1:
            kargs['y'] = args[0]
        elif len(args) == 2:
            kargs['x'] = args[0]
            kargs['y'] = args[1]
        
        if 'y' not in kargs or kargs['y'] is None:
            kargs['y'] = np.array([])
        if 'x' not in kargs or kargs['x'] is None:
            kargs['x'] = np.arange(len(kargs['y']))
            
        for k in ['x', 'y']:
            data = kargs[k]
            if isinstance(data, list):
                data = np.array(data)
                kargs[k] = data
            if not isinstance(data, np.ndarray) or data.ndim > 1:
                raise Exception("Plot data must be 1D ndarray.")
            if 'complex' in str(data.dtype):
                raise Exception("Can not plot complex data types.")
            
        prof.mark("data checks")
        
        #self.setCacheMode(QtGui.QGraphicsItem.NoCache)  ## Disabling and re-enabling the cache works around a bug in Qt 4.6 causing the cached results to display incorrectly
                                                        ##    Test this bug with test_PlotWidget and zoom in on the animated plot
        self.prepareGeometryChange()
        self.yData = kargs['y'].view(np.ndarray)
        self.xData = kargs['x'].view(np.ndarray)
        
        prof.mark('copy')
        
        if 'stepMode' in kargs:
            self.opts['stepMode'] = kargs['stepMode']
        
        if self.opts['stepMode'] is True:
            if len(self.xData) != len(self.yData)+1:  ## allow difference of 1 for step mode plots
                raise Exception("len(X) must be len(Y)+1 since stepMode=True (got %s and %s)" % (str(x.shape), str(y.shape)))
        else:
            if self.xData.shape != self.yData.shape:  ## allow difference of 1 for step mode plots
                raise Exception("X and Y arrays must be the same shape--got %s and %s." % (str(x.shape), str(y.shape)))
        
        self.path = None
        self.fillPath = None
        #self.xDisp = self.yDisp = None
        
        if 'name' in kargs:
            self.opts['name'] = kargs['name']
        
        if 'pen' in kargs:
            self.setPen(kargs['pen'])
        if 'shadowPen' in kargs:
            self.setShadowPen(kargs['shadowPen'])
        if 'fillLevel' in kargs:
            self.setFillLevel(kargs['fillLevel'])
        if 'brush' in kargs:
            self.setBrush(kargs['brush'])
        if 'antialias' in kargs:
            self.opts['antialias'] = kargs['antialias']
        
        
        prof.mark('set')
        self.update()
        prof.mark('update')
        self.sigPlotChanged.emit(self)
        prof.mark('emit')
        prof.finish()
        
    def generatePath(self, x, y):
        prof = debug.Profiler('PlotCurveItem.generatePath', disabled=True)
        path = QtGui.QPainterPath()
        
        ## Create all vertices in path. The method used below creates a binary format so that all 
        ## vertices can be read in at once. This binary format may change in future versions of Qt, 
        ## so the original (slower) method is left here for emergencies:
        #path.moveTo(x[0], y[0])
        #for i in range(1, y.shape[0]):
        #    path.lineTo(x[i], y[i])
            
        ## Speed this up using >> operator
        ## Format is:
        ##    numVerts(i4)   0(i4)
        ##    x(f8)   y(f8)   0(i4)    <-- 0 means this vertex does not connect
        ##    x(f8)   y(f8)   1(i4)    <-- 1 means this vertex connects to the previous vertex
        ##    ...
        ##    0(i4)
        ##
        ## All values are big endian--pack using struct.pack('>d') or struct.pack('>i')
        
        if self.opts['stepMode']:
            ## each value in the x/y arrays generates 2 points.
            x2 = np.empty((len(x),2), dtype=x.dtype)
            x2[:] = x[:,np.newaxis]
            if self.opts['fillLevel'] is None:
                x = x2.reshape(x2.size)[1:-1]
                y2 = np.empty((len(y),2), dtype=y.dtype)
                y2[:] = y[:,np.newaxis]
                y = y2.reshape(y2.size)
            else:
                ## If we have a fill level, add two extra points at either end
                x = x2.reshape(x2.size)
                y2 = np.empty((len(y)+2,2), dtype=y.dtype)
                y2[1:-1] = y[:,np.newaxis]
                y = y2.reshape(y2.size)[1:-1]
                y[0] = self.opts['fillLevel']
                y[-1] = self.opts['fillLevel']
                
                
            
        
        
        if sys.version_info[0] == 2:   ## So this is disabled for python 3... why??
            n = x.shape[0]
            # create empty array, pad with extra space on either end
            arr = np.empty(n+2, dtype=[('x', '>f8'), ('y', '>f8'), ('c', '>i4')])
            # write first two integers
            prof.mark('allocate empty')
            arr.data[12:20] = struct.pack('>ii', n, 0)
            prof.mark('pack header')
            # Fill array with vertex values
            arr[1:-1]['x'] = x
            arr[1:-1]['y'] = y
            arr[1:-1]['c'] = 1
            prof.mark('fill array')
            # write last 0
            lastInd = 20*(n+1)
            arr.data[lastInd:lastInd+4] = struct.pack('>i', 0)
            prof.mark('footer')
            # create datastream object and stream into path
            buf = QtCore.QByteArray(arr.data[12:lastInd+4])  # I think one unnecessary copy happens here
            prof.mark('create buffer')
            ds = QtCore.QDataStream(buf)
            prof.mark('create datastream')
            ds >> path
            prof.mark('load')
            
            prof.finish()
        else:
            path.moveTo(x[0], y[0])
            for i in range(1, y.shape[0]):
                path.lineTo(x[i], y[i])
        
        return path


    def shape(self):
        if self.path is None:
            try:
                self.path = self.generatePath(*self.getData())
            except:
                return QtGui.QPainterPath()
        return self.path

    def boundingRect(self):
        (x, y) = self.getData()
        if x is None or y is None or len(x) == 0 or len(y) == 0:
            return QtCore.QRectF()
            
            
        if self.opts['shadowPen'] is not None:
            lineWidth = (max(self.opts['pen'].width(), self.opts['shadowPen'].width()) + 1)
        else:
            lineWidth = (self.opts['pen'].width()+1)
            
        
        pixels = self.pixelVectors()
        if pixels == (None, None):
            pixels = [Point(0,0), Point(0,0)]
            
        xmin = x.min()
        xmax = x.max()
        ymin = y.min()
        ymax = y.max()
        
        if self.opts['fillLevel'] is not None:
            ymin = min(ymin, self.opts['fillLevel'])
            ymax = max(ymax, self.opts['fillLevel'])
            
        xmin -= pixels[0].x() * lineWidth
        xmax += pixels[0].x() * lineWidth
        ymin -= abs(pixels[1].y()) * lineWidth
        ymax += abs(pixels[1].y()) * lineWidth
        
        return QtCore.QRectF(xmin, ymin, xmax-xmin, ymax-ymin)

    def paint(self, p, opt, widget):
        prof = debug.Profiler('PlotCurveItem.paint '+str(id(self)), disabled=True)
        if self.xData is None:
            return
        #if self.opts['spectrumMode']:
            #if self.specPath is None:
                
                #self.specPath = self.generatePath(*self.getData())
            #path = self.specPath
        #else:
        x = None
        y = None
        if self.path is None:
            x,y = self.getData()
            if x is None or len(x) == 0 or y is None or len(y) == 0:
                return
            self.path = self.generatePath(x,y)
            self.fillPath = None
            
            
        path = self.path
        prof.mark('generate path')
        
        if self._exportOpts is not False:
            aa = self._exportOpts.get('antialias', True)
        else:
            aa = self.opts['antialias']
        
        p.setRenderHint(p.Antialiasing, aa)
        
            
        if self.opts['brush'] is not None and self.opts['fillLevel'] is not None:
            if self.fillPath is None:
                if x is None:
                    x,y = self.getData()
                p2 = QtGui.QPainterPath(self.path)
                p2.lineTo(x[-1], self.opts['fillLevel'])
                p2.lineTo(x[0], self.opts['fillLevel'])
                p2.lineTo(x[0], y[0])
                p2.closeSubpath()
                self.fillPath = p2
                
            prof.mark('generate fill path')
            p.fillPath(self.fillPath, self.opts['brush'])
            prof.mark('draw fill path')
            

        ## Copy pens and apply alpha adjustment
        sp = QtGui.QPen(self.opts['shadowPen'])
        cp = QtGui.QPen(self.opts['pen'])
        #for pen in [sp, cp]:
            #if pen is None:
                #continue
            #c = pen.color()
            #c.setAlpha(c.alpha() * self.opts['alphaHint'])
            #pen.setColor(c)
            ##pen.setCosmetic(True)
            
            
            
        if sp is not None and sp.style() != QtCore.Qt.NoPen:
            p.setPen(sp)
            p.drawPath(path)
        p.setPen(cp)
        p.drawPath(path)
        prof.mark('drawPath')
        
        #print "Render hints:", int(p.renderHints())
        prof.finish()
        #p.setPen(QtGui.QPen(QtGui.QColor(255,0,0)))
        #p.drawRect(self.boundingRect())
        
        
    def clear(self):
        self.xData = None  ## raw values
        self.yData = None
        self.xDisp = None  ## display values (after log / fft)
        self.yDisp = None
        self.path = None
        #del self.xData, self.yData, self.xDisp, self.yDisp, self.path
        
    #def mousePressEvent(self, ev):
        ##GraphicsObject.mousePressEvent(self, ev)
        #if not self.clickable:
            #ev.ignore()
        #if ev.button() != QtCore.Qt.LeftButton:
            #ev.ignore()
        #self.mousePressPos = ev.pos()
        #self.mouseMoved = False
        
    #def mouseMoveEvent(self, ev):
        ##GraphicsObject.mouseMoveEvent(self, ev)
        #self.mouseMoved = True
        ##print "move"
        
    #def mouseReleaseEvent(self, ev):
        ##GraphicsObject.mouseReleaseEvent(self, ev)
        #if not self.mouseMoved:
            #self.sigClicked.emit(self)

    def mouseClickEvent(self, ev):
        if not self.clickable or ev.button() != QtCore.Qt.LeftButton:
            return
        ev.accept()
        self.sigClicked.emit(self)


class ROIPlotItem(PlotCurveItem):
    """Plot curve that monitors an ROI and image for changes to automatically replot."""
    def __init__(self, roi, data, img, axes=(0,1), xVals=None, color=None):
        self.roi = roi
        self.roiData = data
        self.roiImg = img
        self.axes = axes
        self.xVals = xVals
        PlotCurveItem.__init__(self, self.getRoiData(), x=self.xVals, color=color)
        #roi.connect(roi, QtCore.SIGNAL('regionChanged'), self.roiChangedEvent)
        roi.sigRegionChanged.connect(self.roiChangedEvent)
        #self.roiChangedEvent()
        
    def getRoiData(self):
        d = self.roi.getArrayRegion(self.roiData, self.roiImg, axes=self.axes)
        if d is None:
            return
        while d.ndim > 1:
            d = d.mean(axis=1)
        return d
        
    def roiChangedEvent(self):
        d = self.getRoiData()
        self.updateData(d, self.xVals)

