#
# Histogram.py -- Histogram plugin for fits viewer
# 
#[ Eric Jeschke (eric@naoj.org) --
#  Last edit: Fri Oct 26 15:44:04 HST 2012
#]
#
# Copyright (c) 2011-2012, Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
import gtk
import pango
import numpy
import pyfits
import os.path

import FitsImageCanvasTypesGtk as CanvasTypes
import Plot
import GingaPlugin
import AstroImage

class Gemini(GingaPlugin.LocalPlugin):

    def __init__(self, fv, fitsimage):
        # superclass defines some variables for us, like logger
        super(Gemini, self).__init__(fv, fitsimage)

        self.layertag = 'gemini-canvas'
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
        # Paned container is just to provide a way to size the graph
        # to a reasonable size
        box = gtk.VPaned()
        container.pack_start(box, expand=True, fill=True)
        
        # Make the waveplot plot
        vbox = gtk.VBox()

        self.msgFont = pango.FontDescription("Sans 14")
        tw = gtk.TextView()
        tw.set_wrap_mode(gtk.WRAP_WORD)
        tw.set_left_margin(4)
        tw.set_right_margin(4)
        tw.set_editable(False)
        tw.set_left_margin(4)
        tw.set_right_margin(4)
        tw.modify_font(self.msgFont)
        self.tw = tw

        fr = gtk.Frame(" Instructions ")
        fr.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        fr.set_label_align(0.1, 0.5)
        fr.add(tw)
        vbox.pack_start(fr, padding=4, fill=True, expand=False)
        
        self.plot = Plot.Plot(self.logger)
        w = self.plot.get_widget()
        vbox.pack_start(w, padding=4, fill=True, expand=True)

        box.pack1(vbox, resize=True, shrink=True)
        drop = gtk.Label("Drop Files Here")
        box.pack2(drop, resize=True, shrink=True)
        #self.plot.set_callback('close', lambda x: self.stop())

        # Set up widget as a drag and drop destination
        self.TARGET_TYPE_TEXT = 80
        toImage = [ ( "text/plain", 0, self.TARGET_TYPE_TEXT ) ]
        drop.connect("drag_data_received", self.drop_event)
        drop.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                           toImage, gtk.gdk.ACTION_COPY)

        btns = gtk.HButtonBox()
        btns.set_layout(gtk.BUTTONBOX_START)
        btns.set_spacing(3)
        btns.set_child_size(15, -1)

        btn = gtk.Button("Close")
        btn.connect('clicked', lambda w: self.close())
        btns.add(btn)
        container.pack_start(btns, padding=4, fill=True, expand=False)

    def close(self):
        chname = self.fv.get_channelName(self.fitsimage)
        self.fv.stop_operation_channel(chname, str(self))
        return True
        
    def instructions(self):
        buf = self.tw.get_buffer()
        buf.set_text(""" """)
        self.tw.modify_font(self.msgFont)
            
    def start(self):
        self.instructions()
        self.plot.set_titles(rtitle="Waveplot")
        self.plot.show()

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
        try:
            self.plot.hide()
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
    
    def drop_event(self, widget, context, x, y, selection, targetType,
                   time):
        if targetType != self.TARGET_TYPE_TEXT:
            return False
        paths = selection.data.split('\n')
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
        return 'gemini'
    
# END
