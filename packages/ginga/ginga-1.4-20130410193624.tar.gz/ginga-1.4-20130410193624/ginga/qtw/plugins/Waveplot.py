#
# Waveplot.py -- Example Waveplot plugin for Ginga fits viewer
# 
# Eric Jeschke (eric@naoj.org)
#
import numpy
import pyfits
import os.path

from QtHelp import QtGui, QtCore
import QtHelp

import FitsImageCanvasTypesQt as CanvasTypes
import Plot
import GingaPlugin
import AstroImage

class Waveplot(GingaPlugin.LocalPlugin):

    def __init__(self, fv, fitsimage):
        # superclass defines some variables for us, like logger
        super(Waveplot, self).__init__(fv, fitsimage)

        self.layertag = 'waveplot-canvas'
        self.wavetag = None
        self.wavecolor = 'aquamarine'

        canvas = CanvasTypes.DrawingCanvas()
        canvas.enable_draw(True)
        canvas.set_drawtype('rectangle', color='cyan', linestyle='dash',
                            drawdims=True)
        canvas.set_callback('draw-event', self.waveplot)
        canvas.set_callback('button-press', self.drag)
        canvas.set_callback('motion', self.drag)
        canvas.set_callback('button-release', self.update)
        canvas.setSurface(self.fitsimage)
        self.canvas = canvas

        # Number of columns to wrap linear 1D data
        self.wraplen = 40

    def build_gui(self, container):
        # Splitter is just to provide a way to size the graph
        # to a reasonable size
        vpaned = QtGui.QSplitter()
        vpaned.setOrientation(QtCore.Qt.Vertical)
        
        # Make the cuts plot
        twidget = QtHelp.VBox()
        vbox1 = twidget.layout()
        vbox1.setContentsMargins(4, 4, 4, 4)
        vbox1.setSpacing(2)

        msgFont = QtGui.QFont("Sans", 14)
        tw = QtGui.QLabel()
        tw.setFont(msgFont)
        tw.setWordWrap(True)
        self.tw = tw

        fr = QtHelp.Frame("Instructions")
        fr.layout().addWidget(tw, stretch=1, alignment=QtCore.Qt.AlignTop)
        vbox1.addWidget(fr, stretch=0, alignment=QtCore.Qt.AlignTop)
        
        self.plot = Plot.Plot(self.logger)
        w = self.plot.get_widget()
        vbox1.addWidget(w, stretch=2, alignment=QtCore.Qt.AlignTop)

        w = DropLabel("Drop files here")
        w.plugin = self
        w.logger = self.logger
        w.setAcceptDrops(True)
        vbox1.addWidget(w, stretch=1, alignment=QtCore.Qt.AlignCenter)

        btns = QtHelp.HBox()
        layout= btns.layout()
        layout.setSpacing(3)
        #btns.set_child_size(15, -1)

        btn = QtGui.QPushButton("Close")
        btn.clicked.connect(lambda w: self.close())

        layout.addWidget(btn, stretch=0, alignment=QtCore.Qt.AlignLeft)
        vbox1.addWidget(btns, stretch=0, alignment=QtCore.Qt.AlignLeft)

        vpaned.addWidget(twidget)
        vpaned.addWidget(QtGui.QLabel(''))

        container.addWidget(vpaned, stretch=1)

    def close(self):
        chname = self.fv.get_channelName(self.fitsimage)
        self.fv.stop_operation_channel(chname, str(self))
        return True
        
    def instructions(self):
        self.tw.setText("""Drop 1D files on to the widget below.""")
            
    def start(self):
        self.instructions()
        self.plot.set_titles(rtitle="Waveplot")

        # insert canvas, if not already
        try:
            obj = self.fitsimage.getObjectByTag(self.layertag)

        except KeyError:
            # Add ruler layer
            self.fitsimage.add(self.canvas, tag=self.layertag)

        #self.canvas.deleteAllObjects()
        self.resume()

    def pause(self):
        self.canvas.ui_setActive(False)
        
    def resume(self):
        self.canvas.ui_setActive(True)
        self.fv.showStatus("Draw a rectangle with the right mouse button")
        if self.wavetag:
            self.redo()
        
    def stop(self):
        # remove the rect from the canvas
        ## try:
        ##     self.canvas.deleteObjectByTag(self.wavetag, redraw=False)
        ## except:
        ##     pass
        ##self.wavetag = None
        # remove the canvas from the image
        try:
            self.fitsimage.deleteObjectByTag(self.layertag)
        except:
            pass
        self.fv.showStatus("")
        
    def get_limits(self, image, bbox):
        length = image.get('length')
        cols, rows = image.get_data_size()
        lower_wl = 4500.0
        upper_wl = 7000.0
        return (lower_wl, upper_wl)
        
    def redo(self):
        obj = self.canvas.getObjectByTag(self.wavetag)
        if obj.kind != 'compound':
            return True
        bbox = obj.objects[0]
        
        image = self.fitsimage.get_image()
        data = image.cutout_data(bbox.x1, bbox.y1, bbox.x2, bbox.y2)
        ht, wd = data.shape[:2]
        # See if image was stored with a length attribute
        length = image.get('length', ht*wd)
        # chop off blank data we added to make 2D
        Y = data.flat
        if len(Y) > length:
            Y = Y[:length]
        lower_wl, upper_wl = self.get_limits(image, bbox)
        inc = (upper_wl - lower_wl) / float(len(Y))
        xaxis = [ lower_wl + inc*x for x in xrange(len(Y)) ]
        X = numpy.array(xaxis)
        self.plot.clear()
        self.plot.plot(X, Y, xtitle="Wavelength (angstroms)", ytitle="",
                           title="Your Title Here")
        return True
    
    def drop_event(self, paths):
        self.logger.debug("dropped filename(s): %s" % (str(paths)))

        path = paths[0].strip()
        self.open_file(path)

    def open_file(self, path):
        in_f = pyfits.open(path, 'readonly')
        data = in_f[2].data
        assert len(data.shape) == 1
        length = data.shape[0]
        in_f.close()

        dirname, filename = os.path.split(path)

        cols = self.wraplen
        rows = int(length // cols)
        rem = length % cols
        
        if rem > 0:
            rest = cols - rem
            rows += 1
            newdata = numpy.zeros(rows * cols)
            newdata[0:length] = data
            data = newdata
        data = data.reshape((rows, cols))

        # Create an image with the reshaped data and fits keywords
        image = AstroImage.AstroImage(data)
        image.update_keywords(in_f[0].header)
        keylist = [ kwd for kwd, val in in_f[0].header.items() ]
        image.set(name=filename, keyorder=keylist, length=length)

        # Load the image for visualization
        self.fv.add_image(filename, image)

        y2, x2 = data.shape
        # Create the boundary of the area to graph
        tag = self.canvas.add(CanvasTypes.Rectangle(0, 0, x2, y2,
                                                    color='cyan',
                                                    linestyle='dash'))

        # and plot
        self.waveplot(self.canvas, tag)

    def update(self, canvas, button, data_x, data_y):
        if not (button == 0x1):
            return
        
        obj = self.canvas.getObjectByTag(self.wavetag)
        if obj.kind == 'compound':
            bbox = obj.objects[0]
        elif obj.kind == 'rectangle':
            bbox = obj
        else:
            return True

        # calculate center of bbox
        wd = bbox.x2 - bbox.x1
        dw = wd // 2
        ht = bbox.y2 - bbox.y1
        dh = ht // 2
        x, y = bbox.x1 + dw, bbox.y1 + dh

        # calculate offsets of move
        dx = (data_x - x)
        dy = (data_y - y)

        # calculate new coords
        x1, y1, x2, y2 = bbox.x1+dx, bbox.y1+dy, bbox.x2+dx, bbox.y2+dy
        
        try:
            canvas.deleteObjectByTag(self.wavetag, redraw=False)
        except:
            pass

        tag = canvas.add(CanvasTypes.Rectangle(x1, y1, x2, y2,
                                               color='cyan',
                                               linestyle='dash'))

        self.waveplot(canvas, tag)

    def drag(self, canvas, button, data_x, data_y):
        if not (button == 0x1):
            return
        
        obj = self.canvas.getObjectByTag(self.wavetag)
        if obj.kind == 'compound':
            bbox = obj.objects[0]
        elif obj.kind == 'rectangle':
            bbox = obj
        else:
            return True

        # calculate center of bbox
        wd = bbox.x2 - bbox.x1
        dw = wd // 2
        ht = bbox.y2 - bbox.y1
        dh = ht // 2
        x, y = bbox.x1 + dw, bbox.y1 + dh

        # calculate offsets of move
        dx = (data_x - x)
        dy = (data_y - y)

        # calculate new coords
        x1, y1, x2, y2 = bbox.x1+dx, bbox.y1+dy, bbox.x2+dx, bbox.y2+dy

        if obj.kind == 'compound':
            try:
                canvas.deleteObjectByTag(self.wavetag, redraw=False)
            except:
                pass

            self.wavetag = canvas.add(CanvasTypes.Rectangle(x1, y1, x2, y2,
                                                            color='cyan',
                                                            linestyle='dash'))
        else:
            bbox.x1, bbox.y1, bbox.x2, bbox.y2 = x1, y1, x2, y2
            canvas.redraw(whence=3)

    
    def waveplot(self, canvas, tag):
        obj = canvas.getObjectByTag(tag)
        if obj.kind != 'rectangle':
            return True
        canvas.deleteObjectByTag(tag, redraw=False)

        if self.wavetag:
            try:
                canvas.deleteObjectByTag(self.wavetag, redraw=False)
            except:
                pass

        tag = canvas.add(CanvasTypes.CompoundObject(
            CanvasTypes.Rectangle(obj.x1, obj.y1, obj.x2, obj.y2,
                                  color=self.wavecolor),
            CanvasTypes.Text(obj.x1, obj.y2+4, "Waveplot",
                             color=self.wavecolor)))
        self.wavetag = tag

        return self.redo()
    
    def __str__(self):
        return 'waveplot'


class DropLabel(QtGui.QLabel):
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            print "ACCEPT!"
            event.accept()
        else:
            print "IGNORE!"
            event.ignore() 

    def dropEvent(self, event):
        dropdata = event.mimeData()
        formats = map(str, list(dropdata.formats()))
        self.logger.debug("available formats of dropped data are %s" % (
            formats))
        if dropdata.hasUrls():
            urls = list(dropdata.urls())
            paths = [ str(url.toString()) for url in urls ]
            event.acceptProposedAction()
            print "paths are %s" % str(paths)
            self.plugin.drop_event(paths)
            
# END
