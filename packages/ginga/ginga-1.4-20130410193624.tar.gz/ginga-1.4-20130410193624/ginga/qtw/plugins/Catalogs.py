#
# Catalogs.py -- Catalogs plugin for fits viewer
# 
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c)  Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
from ginga.qtw.QtHelp import QtGui, QtCore
from ginga.qtw import QtHelp

from ginga.qtw import FitsImageCanvasTypesQt as CanvasTypes
from ginga import GingaPlugin
from ginga.qtw import ColorBar
from ginga import cmap, imap
from ginga import wcs

from ginga.misc import Bunch, Future

class Catalogs(GingaPlugin.LocalPlugin):

    def __init__(self, fv, fitsimage):
        super(Catalogs, self).__init__(fv, fitsimage)

        self.mycolor = 'skyblue'
        self.color_cursor = 'red'

        self.limit_stars_to_area = False
        self.use_dss_channel = False
        self.plot_max = 500
        self.plot_limit = 100
        self.plot_start = 0

        canvas = CanvasTypes.DrawingCanvas()
        canvas.enable_draw(True)
        canvas.set_drawtype('rectangle', color='cyan', linestyle='dash',
                            drawdims=True)
        canvas.set_callback('button-release', self.btnup)
        canvas.set_callback('draw-event', self.getarea)
        canvas.setSurface(self.fitsimage)
        self.canvas = canvas
        self.layertag = 'catalog-canvas'
        self.areatag = None
        self.curstar = None

        self.image_server_options = []
        self.image_server_params = None

        self.catalog_server_options = []
        self.catalog_server_params = None


    def build_gui(self, container, future=None):
        vbox1 = QtHelp.VBox()

        msgFont = QtGui.QFont("Sans", 14)
        tw = QtGui.QLabel()
        tw.setFont(msgFont)
        tw.setWordWrap(True)
        self.tw = tw

        fr = QtHelp.Frame("Instructions")
        fr.addWidget(tw, stretch=1, alignment=QtCore.Qt.AlignTop)
        vbox1.addWidget(fr, stretch=0, alignment=QtCore.Qt.AlignTop)
        
        nb = QtHelp.TabWidget()
        nb.setTabPosition(QtGui.QTabWidget.South)
        nb.setUsesScrollButtons(True)
        self.w.nb = nb
        #vbox1.addWidget(nb, stretch=1, alignment=QtCore.Qt.AlignTop)
        vbox1.addWidget(nb, stretch=1)

        vbox0 = QtHelp.VBox()

        hbox = QtHelp.HBox()
        hbox.setSpacing(4)
        vbox0.addWidget(hbox, stretch=1, alignment=QtCore.Qt.AlignTop)

        vbox = QtHelp.VBox()
        fr = QtHelp.Frame(" Image Server ")
        fr.addWidget(vbox, stretch=1, alignment=QtCore.Qt.AlignTop)
        hbox.addWidget(fr, stretch=0, alignment=QtCore.Qt.AlignLeft)

        captions = (('Server', 'xlabel'),
                    ('@Server', 'combobox'),
                    ('Use DSS channel', 'checkbutton'),
                    ('Get Image', 'button'))
        w, b = QtHelp.build_info(captions)
        self.w.update(b)
        self.w.get_image.clicked.connect(self.getimage_cb)
        self.w.use_dss_channel.setChecked(self.use_dss_channel)
        self.w.use_dss_channel.stateChanged.connect(self.use_dss_channel_cb)

        vbox.addWidget(w, stretch=0, alignment=QtCore.Qt.AlignTop)

        self.w.img_params = QtHelp.StackedWidget()
        vbox.addWidget(self.w.img_params, stretch=1,
                       alignment=QtCore.Qt.AlignTop)
        
        combobox = self.w.server
        index = 0
        self.image_server_options = self.fv.imgsrv.getServerNames(kind='image')
        for name in self.image_server_options:
            combobox.addItem(name)
            index += 1
        index = 0
        combobox.setCurrentIndex(index)
        combobox.activated.connect(self.setup_params_image)
        if len(self.image_server_options) > 0:
            self.setup_params_image(index, redo=False)

        vbox = QtHelp.VBox()
        fr = QtHelp.Frame(" Catalog Server ")
        fr.addWidget(vbox, stretch=1, alignment=QtCore.Qt.AlignTop)
        hbox.addWidget(fr, stretch=0, alignment=QtCore.Qt.AlignLeft)

        captions = (('Server', 'xlabel'),
                    ('@Server', 'combobox'),
                    ('Limit stars to area', 'checkbutton'),
                    ('Search', 'button'))
        w, self.w2 = QtHelp.build_info(captions)
        self.w2.search.clicked.connect(self.getcatalog_cb)
        self.w2.limit_stars_to_area.setChecked(self.limit_stars_to_area)
        self.w2.limit_stars_to_area.stateChanged.connect(self.limit_area_cb)

        vbox.addWidget(w, stretch=0, alignment=QtCore.Qt.AlignTop)

        self.w2.cat_params = QtHelp.StackedWidget()
        vbox.addWidget(self.w2.cat_params, stretch=1,
                       alignment=QtCore.Qt.AlignTop)
        
        combobox = self.w2.server
        index = 0
        self.catalog_server_options = self.fv.imgsrv.getServerNames(kind='catalog')
        for name in self.catalog_server_options:
            combobox.addItem(name)
            index += 1
        index = 0
        combobox.setCurrentIndex(index)
        combobox.activated.connect(self.setup_params_catalog)
        if len(self.catalog_server_options) > 0:
            self.setup_params_catalog(index, redo=False)

        btns = QtHelp.HBox()
        btns.setSpacing(5)
        
        btn = QtGui.QPushButton("Set parameters from entire image")
        btn.clicked.connect(self.setfromimage)
        btns.addWidget(btn, stretch=0, alignment=QtCore.Qt.AlignCenter)
        vbox0.addWidget(btns, stretch=0, alignment=QtCore.Qt.AlignTop)

        self.w.params = vbox0
        nb.addTab(vbox0, u"Params")

        vbox = QtHelp.VBox()
        self.table = CatalogListing(self.logger, vbox)

        hbox = QtHelp.HBox()
        adj = QtGui.QScrollBar(QtCore.Qt.Horizontal)
        adj.setRange(0, 1000)
        adj.setSingleStep(1)
        adj.setPageStep(10)
        #adj.setMaximum(1000)
        adj.setValue(0)
        #adj.resize(200, -1)
        adj.setTracking(True)
        adj.setToolTip("Choose subset of stars plotted")
        self.w.plotgrp = adj
        adj.valueChanged.connect(self.plot_pct_cb)
        hbox.addWidget(adj, stretch=1)

        sb = QtGui.QSpinBox()
        sb.setRange(10, self.plot_max)
        sb.setValue(self.plot_limit)
        sb.setSingleStep(10)
        adj.setPageStep(100)
        sb.setWrapping(False)
        self.w.plotnum = sb
        sb.setToolTip("Adjust size of subset of stars plotted")
        sb.valueChanged.connect(self.plot_limit_cb)
        hbox.addWidget(sb, stretch=0)

        vbox.addWidget(hbox, stretch=0)
        self.w.listing = vbox
        nb.addTab(vbox, u"Listing")

        btns = QtHelp.HBox()
        btns.setSpacing(3)
        #btns.set_child_size(15, -1)
        self.w.buttons = btns

        btn = QtGui.QPushButton("Close")
        btn.clicked.connect(self.close)
        btns.addWidget(btn, stretch=0, alignment=QtCore.Qt.AlignLeft)

        if future:
            btn = QtGui.QPushButton('Ok')
            btn.clicked.connect(lambda w: self.ok())
            btns.addWidget(btn, stretch=0, alignment=QtCore.Qt.AlignLeft)
            btn = QtGui.QPushButton('Cancel')
            btn.clicked.connect(lambda w: self.cancel())
            btns.addWidget(btn, stretch=0, alignment=QtCore.Qt.AlignLeft)

        container.addWidget(vbox1, stretch=1)
        

    def limit_area_cb(self, tf):
        self.limit_stars_to_area = (tf != 0)
        return True

    def use_dss_channel_cb(self, tf):
        self.use_dss_channel = (tf != 0)
        return True

    def plot_pct_cb(self):
        val = self.w.plotgrp.value()
        self.plot_start = int(val)
        self.replot_stars()
        return True

    def _update_plotscroll(self):
        num_stars = len(self.starlist)
        if num_stars > 0:
            adj = self.w.plotgrp
            page_size = self.plot_limit
            self.plot_start = min(self.plot_start, num_stars-1)
            adj.setRange(0, num_stars)
            adj.setSingleStep(1)
            adj.setPageStep(page_size)

        self.replot_stars()

    def plot_limit_cb(self):
        val = self.w.plotnum.value()
        self.plot_limit = int(val)
        self._update_plotscroll()
        return True

    def set_message(self, msg):
        self.tw.setText(msg)
        
    def ok(self):
        return self.close()

    def cancel(self):
        return self.close()

    def update_gui(self):
        self.fv.update_pending()

    def close(self):
        chname = self.fv.get_channelName(self.fitsimage)
        self.fv.stop_operation_channel(chname, str(self))
        return True
        
    def _setup_params(self, obj, container):
        params = obj.getParams()
        captions = []
        for key, bnch in params.items():
            text = key
            if bnch.has_key('label'):
                text = bnch.label
            captions.append((text, 'entry'))

        # TODO: put RA/DEC first, and other stuff not in random orders
        w, b = QtHelp.build_info(captions)

        # remove old widgets
        old_w = container.currentWidget()
        if old_w != None:
            container.removeWidget(old_w)

        # add new widgets
        container.insertWidget(0, w)
        return b

    def setup_params_image(self, index, redo=True):
        key = self.image_server_options[index]

        # Get the parameter list and adjust the widget
        obj = self.fv.imgsrv.getImageServer(key)
        b = self._setup_params(obj, self.w.img_params)
        self.image_server_params = b

        if redo:
            self.redo()

    def setup_params_catalog(self, index, redo=True):
        key = self.catalog_server_options[index]

        # Get the parameter list and adjust the widget
        obj = self.fv.imgsrv.getCatalogServer(key)
        b = self._setup_params(obj, self.w2.cat_params)
        self.catalog_server_params = b

        if redo:
            self.redo()

            
    def instructions(self):
        self.set_message("""TBD.""")
            
    def start(self, future=None):
        self.instructions()
        # start catalog operation
        try:
            obj = self.fitsimage.getObjectByTag(self.layertag)

        except KeyError:
            # Add canvas layer
            self.fitsimage.add(self.canvas, tag=self.layertag)
            
        # Raise the params tab
        self.w.nb.setCurrentWidget(self.w.params)

        self.setfromimage()
        self.resume()

    def pause(self):
        self.canvas.ui_setActive(False)
        
    def resume(self):
        self.canvas.ui_setActive(True)
        #self.fv.showStatus("Draw a rectangle with the right mouse button")
        
    def stop(self):
        # stop catalog operation
        self.clearAll()
        # remove the canvas from the image
        self.canvas.ui_setActive(False)
        try:
            self.fitsimage.deleteObjectByTag(self.layertag)
        except:
            pass
        try:
            self.table.close()
        except:
            pass
        self.fv.showStatus("")
        
    def redo(self):
        obj = self.canvas.getObjectByTag(self.areatag)
        if obj.kind != 'rectangle':
            self.stop()
            return True
        
        try:
            image = self.fitsimage.get_image()

            # calculate center of bbox
            wd = obj.x2 - obj.x1
            dw = wd // 2
            ht = obj.y2 - obj.y1
            dh = ht // 2
            ctr_x, ctr_y = obj.x1 + dw, obj.y1 + dh
            ra_ctr, dec_ctr = image.pixtoradec(ctr_x, ctr_y, format='str')

            # Calculate RA and DEC for the three points
            # origination point
            ra_org, dec_org = image.pixtoradec(obj.x1, obj.y1)

            # destination point
            ra_dst, dec_dst = image.pixtoradec(obj.x2, obj.y2)

            # "heel" point making a right triangle
            ra_heel, dec_heel = image.pixtoradec(obj.x1, obj.y2)

            ht_deg = image.deltaStarsRaDecDeg(ra_org, dec_org, ra_heel, dec_heel)
            wd_deg = image.deltaStarsRaDecDeg(ra_heel, dec_heel, ra_dst, dec_dst)
            radius_deg = image.deltaStarsRaDecDeg(ra_heel, dec_heel, ra_dst, dec_dst)
            # width and height are specified in arcmin
            sgn, deg, mn, sec = wcs.degToDms(wd_deg)
            wd = deg*60.0 + float(mn) + sec/60.0
            sgn, deg, mn, sec = wcs.degToDms(ht_deg)
            ht = deg*60.0 + float(mn) + sec/60.0
            sgn, deg, mn, sec = wcs.degToDms(radius_deg)
            radius = deg*60.0 + float(mn) + sec/60.0
            
        except Exception, e:
            self.fv.showStatus('BAD WCS: %s' % str(e))
            return True

        # Copy the image parameters out to the widget
        d = { 'ra': ra_ctr, 'dec': dec_ctr, 'width': str(wd),
              'height': ht, 'r': radius, 'r2': radius,
              'r1': 0.0,
              }
        for bnch in (self.image_server_params,
                     self.catalog_server_params):
            if bnch != None:
                for key in bnch.keys():
                    if d.has_key(key):
                        bnch[key].setText(str(d[key]))

        return True
    
    def btnup(self, canvas, button, data_x, data_y):
        if not (button == 0x1):
            return
        
        objs = self.canvas.getItemsAt(data_x, data_y)
        for obj in objs:
            if (obj.tag != None) and obj.tag.startswith('star'):
                info = obj.get_data()
                self.table.show_selection(info.star)
                return True
    
    def highlight_object(self, obj, tag, color, redraw=True):
        x = obj.objects[0].x
        y = obj.objects[0].y
        delta = 10
        
        radius = obj.objects[0].radius + delta

        hilite = CanvasTypes.Circle(x, y, radius,
                                    linewidth=4, color=color)
        obj.add(hilite, tag=tag, redraw=redraw)
        
    def highlight_objects(self, objs, tag, color, redraw=True):
        for obj in objs:
            self.highlight_object(obj, tag, color, redraw=False)
        if redraw:
            self.canvas.redraw()
        
    def unhighlight_object(self, obj, tag):
        # delete the highlight ring of the former cursor object
        try:
            #hilite = obj.objects[2]
            obj.deleteObjectByTag(tag)
        except:
            pass
        
    def highlight_cursor(self, obj):
        if self.curstar:
            bnch = self.curstar
            if bnch.obj == obj:
                # <-- we are already highlighting this object
                return True

            # delete the highlight ring of the former cursor object
            self.unhighlight_object(bnch.obj, 'cursor')

        self.highlight_object(obj, 'cursor', self.color_cursor)
        self.curstar = Bunch.Bunch(obj=obj)
        self.canvas.redraw()
        

    def setfromimage(self):
        x1, y1 = 0, 0
        x2, y2 = self.fitsimage.get_data_size()
        tag = self.canvas.add(CanvasTypes.Rectangle(x1, y1, x2, y2,
                                                    color=self.mycolor))

        self.getarea(self.canvas, tag)
        
        
    def getarea(self, canvas, tag):
        obj = canvas.getObjectByTag(tag)
        if obj.kind != 'rectangle':
            return True

        if self.areatag:
            try:
                canvas.deleteObjectByTag(self.areatag)
            except:
                pass

        obj.color = self.mycolor
        obj.linestyle = 'solid'
        canvas.redraw(whence=3)

        self.areatag = tag
        # Raise the params tab
        self.w.nb.setCurrentWidget(self.w.params)
        return self.redo()

    def get_params(self, bnch):
        params = {}
        for key in bnch.keys():
            params[key] = str(bnch[key].text())
        return params

        
    def getimage_cb(self):
        params = self.get_params(self.image_server_params)

        index = self.w.server.currentIndex()
        server = self.image_server_options[index]

        self.clearAll()

        if self.use_dss_channel:
            chname = 'DSS'
            if not self.fv.has_channel(chname):
                self.fv.add_channel(chname)
        else:
            chname = self.fv.get_channelName(self.fitsimage)

        self.fitsimage.onscreen_message("Querying image db...",
                                        delay=1.0)

        # Offload this network task to a non-gui thread
        self.fv.nongui_do(self.getimage, server, params, chname)

    def getimage(self, server, params, chname):
        fitspath = self.fv.get_sky_image(server, params)

        self.fv.load_file(fitspath, chname=chname)

        # Update the GUI
        def getimage_update(self):
            self.setfromimage()
            self.redo()

        self.fv.gui_do(getimage_update)

    def getcatalog_cb(self):
        params = self.get_params(self.catalog_server_params)

        index = self.w2.server.currentIndex()
        server = self.catalog_server_options[index]

        obj = None
        if self.limit_stars_to_area:
            # Look for the defining object to filter stars
            # If none, then use the visible image area
            try:
                obj = self.canvas.getObjectByTag(self.areatag)
            
            except KeyError:
                pass
            
        self.reset()
        self.fitsimage.onscreen_message("Querying catalog db...",
                                        delay=1.0)
        # Offload this network task to a non-gui thread
        self.fv.nongui_do(self.getcatalog, server, params, obj)

    def getcatalog(self, server, params, obj):
        starlist, info = self.fv.get_catalog(server, params)
        self.logger.debug("starlist=%s" % str(starlist))

        starlist = self.filter_results(starlist, obj)

        # Update the GUI
        self.fv.gui_do(self.update_catalog, starlist, info)
        
    def update_catalog(self, starlist, info):
        self.starlist = starlist
        self.table.show_table(self, info, starlist)
        # Raise the listing tab
        self.w.nb.setCurrentWidget(self.w.listing)

        self._update_plotscroll()


    def filter_results(self, starlist, filter_obj):
        image = self.fitsimage.get_image()

        # Filter starts by a containing object, if provided
        if filter_obj:
            stars = []
            for star in starlist:
                x, y = image.radectopix(star['ra_deg'], star['dec_deg'])
                if filter_obj.contains(x, y):
                    stars.append(star)
            starlist = stars

        return starlist

    def clear(self):
        # TODO: remove only star objects?
        objects = self.canvas.getObjectsByTagpfx('star')
        self.canvas.deleteObjects(objects)
       
    def clearAll(self):
        self.canvas.deleteAllObjects()
       
    def reset(self):
        #self.clear()
        self.clearAll()
        self.table.clear()
       
    def plot_star(self, obj, image=None):
        if not image:
            image = self.fitsimage.get_image()
        x, y = image.radectopix(obj['ra_deg'], obj['dec_deg'])
        #print "STAR at %d,%d" % (x, y)
        # TODO: auto-pick a decent radius
        radius = 10
        color = self.table.get_color(obj)
        #print "color is %s" % str(color)
        circle = CanvasTypes.Circle(x, y, radius, color=color)
        point = CanvasTypes.Point(x, y, radius, color=color)
        if obj.has_key('pick') and (not obj['pick']):
            star = CanvasTypes.Canvas(circle, point)
        else:
            star = CanvasTypes.Canvas(circle)
        star.set_data(star=obj)
        obj.canvobj = star

        self.canvas.add(star, tagpfx='star', redraw=False)

    def replot_stars(self, selected=[]):
        self.clear()

        image = self.fitsimage.get_image()
        canvas = self.canvas
        
        length = len(self.starlist)
        if length <= self.plot_limit:
            i = 0
        else:
            i = self.plot_start
            i = min(i, length - self.plot_limit)
            length = self.plot_limit
        
        # remove references to old objects before this range
        for j in xrange(i):
            obj = self.starlist[j]
            obj.canvobj = None

        # plot stars in range
        for j in xrange(length):
            obj = self.starlist[i]
            i += 1
            self.plot_star(obj, image=image)

        # remove references to old objects after this range
        for j in xrange(i, length):
            obj = self.starlist[j]
            obj.canvobj = None

        # plot stars in selected list even if they are not in the range
        #for obj in selected:
        selected = self.table.get_selected()
        for obj in selected:
            if (not obj.has_key('canvobj')) or (obj.canvobj == None):
                self.plot_star(obj, image=image)
            self.highlight_object(obj.canvobj, 'selected', 'skyblue')

        canvas.redraw(whence=3)

        
    def __str__(self):
        return 'catalogs'
    

class CatalogListing(object):
    
    def __init__(self, logger, container):
        self.logger = logger
        self.tag = None
        self.mycolor = 'skyblue'
        self.magmap = 'stairs8'

        self.mag_max = 25.0
        self.mag_min = 0.0

        # keys: are name, ra, dec, mag, flag, b_r, preference, priority, dst
        # TODO: automate this generation
        self.columns = [('Name', 'name'),
                        ('RA', 'ra'),
                        ('DEC', 'dec'),
                        ('Mag', 'mag'),
                        ('Preference', 'preference'),
                        ('Priority', 'priority'),
                        ('Flag', 'flag'),
                        ('b-r', 'b_r'),
                        ('Dst', 'dst'),
                        ('Description', 'description'),
                        ]

        self.catalog = None
        self.cursor = 0
        self.color_cursor = 'red'
        self.color_selected = 'skyblue'
        self.selection_mode = 'single'
        self.selected = []
        self.moving_cursor = False

        self.btn = Bunch.Bunch()

        self.mframe = container
            
        vbox = QtHelp.VBox()

        # create the table
        table = QtGui.QTableWidget()
        table.setColumnCount(len(self.columns))
        table.cellClicked.connect(self.select_star)
        self.table = table
        
        col = 0
        for hdr, kwd in self.columns:
            item = QtGui.QTableWidgetItem(hdr)
            table.setHorizontalHeaderItem(col, item)
            col += 1

        vbox.addWidget(table, stretch=1)

        self.cbar = ColorBar.ColorBar(self.logger)
        self.cmap = cmap.get_cmap(self.magmap)
        self.imap = imap.get_imap('ramp')
        self.cbar.set_cmap(self.cmap)
        self.cbar.set_imap(self.imap)
        #self.cbar.set_size_request(-1, 20)

        vbox.addWidget(self.cbar, stretch=0)

        btns = QtHelp.HBox()
        btns.setSpacing(5)

        for name in ('Plot', 'Clear', #'Close'
                     ):
            btn = QtGui.QPushButton(name)
            btns.addWidget(btn, stretch=0, alignment=QtCore.Qt.AlignCenter)
            self.btn[name.lower()] = btn

        self.btn.plot.clicked.connect(self.replot_stars)
        self.btn.clear.clicked.connect(self.clear)
        #self.btn.close.clicked.connect(self.close)

        vbox.addWidget(btns, stretch=0, alignment=QtCore.Qt.AlignTop)
        
        self.mframe.addWidget(vbox, stretch=1)

    def show_table(self, catalog, info, starlist):
        self.starlist = starlist
        self.catalog = catalog
        # info is ignored, for now
        #self.info = info
        self.selected = []

        table = self.table
        table.clearContents()
        table.setSortingEnabled(False)
        # Update the starlist info
        row = 0
        table.setRowCount(len(starlist))
        
        for star in starlist:
            col = 0
            for hdr, kwd in self.columns:
                val = str(star.starInfo.get(kwd, ''))
                item = QtGui.QTableWidgetItem(val)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                table.setItem(row, col, item)
                col += 1
            row += 1
        table.setSortingEnabled(True)

        # TODO: fix.  This is raising a segfault!
        #self.cbar.set_range(self.mag_min, self.mag_max)

    def get_color(self, obj):
        try:
            mag = obj['mag']
        except:
            return self.mycolor

        # clip magnitude to the range we have defined
        mag = max(self.mag_min, mag)
        mag = min(self.mag_max, mag)

        # calculate percentage in range
        point = float(mag) / float(self.mag_max - self.mag_min)
        # invert
        point = 1.0 - point
        # map to a 8-bit color range
        point = int(point * 255.0)

        # Apply colormap.  
        rgbmap = self.cbar.get_rgbmap()
        (r, g, b) = rgbmap.get_rgbval(point)
        r = float(r) / 255.0
        g = float(g) / 255.0
        b = float(b) / 255.0
        return (r, g, b)

    def mark_selection(self, star, fromtable=False):
        """Mark or unmark a star as selected.  (fromtable)==True if the
        selection action came from the table (instead of the star plot).
        """
        self.logger.debug("star selected name=%s ra=%s dec=%s" % (
            star['name'], star['ra'], star['dec']))

        if star in self.selected:
            # Item is already selected--so unselect it
            self.selected.remove(star)
            try:
                self._unselect_tv(star)
                self.catalog.unhighlight_object(star.canvobj, 'selected')
            except Exception, e:
                self.logger.warn("Error unhilighting star: %s" % (str(e)))
            return False
        else:
            if self.selection_mode == 'single':
                # if selection mode is 'single' unselect any existing selections
                for star2 in self.selected:
                    self.selected.remove(star2)
                    try:
                        self._unselect_tv(star2)
                        self.catalog.unhighlight_object(star2.canvobj, 'selected')
                    except Exception, e:
                        self.logger.warn("Error unhilighting star: %s" % (str(e)))
                        self.selected.append(star)
            try:
                # If this star is not plotted, then plot it
                if (not star.has_key('canvobj')) or (star.canvobj == None):
                    self.catalog.plot_star(star)
                    
                self._select_tv(star, fromtable=fromtable)
                self.catalog.highlight_object(star.canvobj, 'selected', 'skyblue')
            except Exception, e:
                self.logger.warn("Error hilighting star: %s" % (str(e)))
            return True


    def show_selection(self, star):
        """This is called by the canvas handling code when a star is clicked.
        """
        # Decide selection or deselection of star
        self.mark_selection(star)

    def _update_selections(self):

        # Go through all selections in the table and ensure that the
        # ones in self.selected are highlighted and the others are not.
        checked = set()
        for modelidx in self.table.selectedIndexes():
            idx = modelidx.row()
            star2 = self.starlist[idx]
            checked.add(star2)
            isSelected = star2 in self.selected
            _range = QtGui.QTableWidgetSelectionRange(idx, 0, idx, maxcol)
            self.table.setRangeSelected(_range, isSelected)

        # Mark any other selected stars that are not highlighted
        for star2 in set(self.selected) - checked:
            idx = self.starlist.index(star2)
            _range = QtGui.QTableWidgetSelectionRange(idx, 0, idx, maxcol)
            self.table.setRangeSelected(_range, True)

    def _select_tv(self, star, fromtable=False):
        self._update_selections()
        
        star_idx = self.starlist.index(star)
        maxcol = len(self.columns)-1
        item = self.table.item(star_idx, 0)

        if not fromtable:
            self.table.scrollToItem(item)

    def _unselect_tv(self, star):
        self._update_selections()

    def clear(self):
        if self.catalog != None:
            self.catalog.clear()

    def get_selected(self):
        return self.selected
    
    def replot_stars(self):
        self.catalog.replot_stars()
        canvobjs = map(lambda star: star.canvobj, self.selected)
        self.catalog.highlight_objects(canvobjs, 'selected', 'skyblue')
            
    def select_star(self, row, col):
        """This method is called when the user selects a star from the table.
        """
        star = self.starlist[row]
        self.mark_selection(star, fromtable=True)
        return True
    

    def motion_notify_event(self, widget, event):
        if event.is_hint:
            x, y, state = event.window.get_pointer()
        else:
            x, y, state = event.x, event.y, event.state

        buf_x1, buf_y1 = self.tw.window_to_buffer_coords(gtk.TEXT_WINDOW_TEXT,
                                                         x, y)
        txtiter = self.tw.get_iter_at_location(buf_x1, buf_y1)

        line = txtiter.get_line()
        star = self.line_to_object(line)
        
        if star == self.cursor:
            return True
        
        self._mark_cursor(star)
        try:
            self.catalog.highlight_cursor(star.canvobj)
        except:
            pass
        return True
        

# END
