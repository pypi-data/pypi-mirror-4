#
# Pick.py -- Pick plugin for fits viewer
# 
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c) Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
import threading
from ginga.qtw.QtHelp import QtGui, QtCore
from ginga.qtw import QtHelp

from ginga import GingaPlugin
from ginga import iqcalc
from ginga.misc import Bunch

import numpy
try:
    import matplotlib
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    have_mpl = True
except ImportError:
    have_mpl = False

from ginga.qtw import FitsImageCanvasQt
from ginga.qtw import FitsImageCanvasTypesQt as CanvasTypes


region_default_width = 30
region_default_height = 30


class Pick(GingaPlugin.LocalPlugin):

    def __init__(self, fv, fitsimage):
        # superclass defines some variables for us, like logger
        super(Pick, self).__init__(fv, fitsimage)

        self.layertag = 'pick-canvas'
        self.pickimage = None
        self.pickcenter = None
        self.pick_qs = None
        self.picktag = None
        self.pickcolor = 'lightgreen'
        self.candidate_color = 'purple'

        self.pick_x1 = 0
        self.pick_y1 = 0
        self.pick_data = None
        self.dx = region_default_width
        self.dy = region_default_height
        # For offloading intensive calculation from graphics thread
        self.serialnum = 0
        self.lock = threading.RLock()
        self.lock2 = threading.RLock()
        self.ev_intr = threading.Event()

        # Peak finding parameters and selection criteria
        # this is the maximum size a side can be
        self.max_side = 1024
        self.radius = 10
        self.threshold = None
        self.min_fwhm = 2.0
        self.max_fwhm = 50.0
        self.min_ellipse = 0.5
        self.edgew = 0.01
        self.show_candidates = False

        self.plot_panx = 0.5
        self.plot_pany = 0.5
        self.plot_zoomlevel = 1.0
        self.num_contours = 8
        self.contour_size_limit = 70
        self.contour_data = None
        self.delta_sky = 0.0
        self.delta_bright = 0.0
        self.iqcalc = iqcalc.IQCalc(self.logger)

        canvas = CanvasTypes.DrawingCanvas()
        canvas.enable_draw(True)
        canvas.set_callback('button-press', self.btndown)
        canvas.set_callback('motion', self.drag)
        canvas.set_callback('button-release', self.update)
        canvas.set_drawtype('rectangle', color='cyan', linestyle='dash',
                            drawdims=True)
        canvas.set_callback('draw-event', self.setpickregion)
        canvas.setSurface(self.fitsimage)
        self.canvas = canvas


    def build_gui(self, container):
        self.pickcenter = None

        # Splitter is just to provide a way to size the graph
        # to a reasonable size
        vpaned = QtGui.QSplitter()
        vpaned.setOrientation(QtCore.Qt.Vertical)
        
        nb = QtHelp.TabWidget()
        nb.setTabPosition(QtGui.QTabWidget.East)
        nb.setUsesScrollButtons(True)
        self.w.nb1 = nb
        vpaned.addWidget(nb)
        
        cm, im = self.fv.cm, self.fv.im

        di = FitsImageCanvasQt.FitsImageCanvas(logger=self.logger)
        di.enable_autozoom('off')
        di.enable_autocuts('off')
        di.enable_zoom(True)
        di.enable_cuts(True)
        di.zoom_to(3, redraw=False)
        di.set_callback('zoom-set', self.zoomset)
        di.set_cmap(cm, redraw=False)
        di.set_imap(im, redraw=False)
        di.set_callback('motion', self.detailxy)
        di.set_bg(0.4, 0.4, 0.4)
        self.pickimage = di

        iw = di.get_widget()
        sp = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                               QtGui.QSizePolicy.MinimumExpanding)
        iw.setSizePolicy(sp)
        width, height = 200, 200
        iw.resize(width, height)
        nb.addTab(iw, 'Image')

        if have_mpl:
            self.w.fig = matplotlib.figure.Figure()
            self.w.ax = self.w.fig.add_subplot(111, axisbg='black')
            self.w.ax.set_aspect('equal', adjustable='box')
            self.w.ax.set_title('Contours')
            #self.w.ax.grid(True)
            canvas = MyFigureCanvas(self.w.fig)
            canvas.setDelegate(self)
            #canvas.resize(width, height)
            self.w.canvas = canvas
            nb.addTab(canvas, u"Contour")

            self.w.fig2 = matplotlib.figure.Figure()
            self.w.ax2 = self.w.fig2.add_subplot(111, axisbg='white')
            #self.w.ax2.set_aspect('equal', adjustable='box')
            self.w.ax2.set_ylabel('brightness')
            self.w.ax2.set_xlabel('pixels')
            self.w.ax2.set_title('FWHM')
            self.w.ax.grid(True)
            canvas = FigureCanvas(self.w.fig2)
            self.w.canvas2 = canvas
            nb.addTab(canvas, u"FWHM")

        sw = QtGui.QScrollArea()

        twidget = QtHelp.VBox()
        sp = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                               QtGui.QSizePolicy.Fixed)
        twidget.setSizePolicy(sp)
        vbox = twidget.layout()
        vbox.setContentsMargins(4, 4, 4, 4)
        vbox.setSpacing(2)
        sw.setWidgetResizable(True)
        sw.setWidget(twidget)

        msgFont = QtGui.QFont("Sans", 14)
        tw = QtGui.QLabel()
        tw.setFont(msgFont)
        tw.setWordWrap(True)
        self.tw = tw

        fr = QtHelp.Frame("Instructions")
        fr.layout().addWidget(tw, stretch=1, alignment=QtCore.Qt.AlignTop)
        vbox.addWidget(fr, stretch=0, alignment=QtCore.Qt.AlignTop)
        
        fr = QtHelp.Frame("Pick")

        nb = QtHelp.TabWidget()
        nb.setTabPosition(QtGui.QTabWidget.South)
        nb.setUsesScrollButtons(True)
        self.w.nb2 = nb

        fr.layout().addWidget(nb, stretch=1, alignment=QtCore.Qt.AlignLeft)
        vbox.addWidget(fr, stretch=0, alignment=QtCore.Qt.AlignTop)

        vbox2 = QtHelp.VBox()
        captions = (('Zoom', 'label', 'Contour Zoom', 'label'),
                    ('Object_X', 'label', 'Object_Y', 'label'),
                    ('RA', 'label', 'DEC', 'label'),
                    ('Equinox', 'label', 'Background', 'label'),
                    ('Sky Level', 'label', 'Brightness', 'label'), 
                    ('FWHM X', 'label', 'FWHM Y', 'label'),
                    ('FWHM', 'label', 'Star Size', 'label'),
                    ('Sample Area', 'label', 'Default Region', 'button'),
                    )

        w, b = QtHelp.build_info(captions)
        self.w.update(b)
        b.zoom.setText(self.fv.scale2text(di.get_scale()))
        self.wdetail = b
        b.default_region.clicked.connect(self.reset_region)
        b.default_region.setToolTip("Reset region size to default")

        vbox2.addWidget(w, stretch=1)
        
        # Pick field evaluation status
        label = QtGui.QLabel()
        self.w.eval_status = label
        ## w.layout().addWidget(label, stretch=0, alignment=QtCore.Qt.AlignLeft)
        vbox2.addWidget(label, stretch=0)

        # Pick field evaluation progress bar and stop button
        hbox = QtHelp.HBox()
        pgs = QtGui.QProgressBar()
        pgs.setRange(0, 100)
        pgs.setTextVisible(True)
        self.w.eval_pgs = pgs
        hbox.addWidget(pgs, stretch=0)
        btn = QtGui.QPushButton("Stop")
        btn.clicked.connect(lambda w: self.eval_intr())
        btn.setEnabled(False)
        self.w.btn_intr_eval = btn
        hbox.addWidget(btn, stretch=0)
        vbox2.addWidget(hbox, stretch=0)

        nb.addTab(vbox2, "Report")

        # Build settings panel
        captions = (('Show Candidates', 'checkbutton'),
                    ('Radius', 'xlabel', '@Radius', 'spinfloat'),
                    ('Threshold', 'xlabel', '@Threshold', 'entry'),
                    ('Min FWHM', 'xlabel', '@Min FWHM', 'spinfloat'),
                    ('Max FWHM', 'xlabel', '@Max FWHM', 'spinfloat'),
                    ('Ellipticity', 'xlabel', '@Ellipticity', 'entry'),
                    ('Edge', 'xlabel', '@Edge', 'entry'),
                    ('Max side', 'xlabel', '@Max side', 'spinbutton'),
                    ('Redo Pick', 'button'),
            )

        w, b = QtHelp.build_info(captions)
        self.w.update(b)
        b.radius.setToolTip("Radius for peak detection")
        b.threshold.setToolTip("Threshold for peak detection (blank=default)")
        b.min_fwhm.setToolTip("Minimum FWHM for selection")
        b.max_fwhm.setToolTip("Maximum FWHM for selection")
        b.ellipticity.setToolTip("Minimum ellipticity for selection")
        b.edge.setToolTip("Minimum edge distance for selection")
        b.show_candidates.setToolTip("Show all peak candidates")
        b.show_candidates.setChecked(self.show_candidates)
        b.show_candidates.stateChanged.connect(self.show_candidates_cb)

        # radius control
        adj = b.radius
        adj.setRange(5.0, 200.0)
        adj.setSingleStep(1.0)
        adj.setValue(self.radius)
        def chg_radius(val):
            self.radius = val
            self.w.lbl_radius.setText(str(self.radius))
            return True
        b.lbl_radius.setText(str(self.radius))
        b.radius.valueChanged.connect(chg_radius)

        # threshold control
        def chg_threshold():
            threshold = None
            ths = str(self.w.threshold.text()).strip()
            if len(ths) > 0:
                threshold = float(ths)
            self.threshold = threshold
            self.w.lbl_threshold.setText(str(self.threshold))
            return True
        b.lbl_threshold.setText(str(self.threshold))
        b.threshold.returnPressed.connect(chg_threshold)

        # min fwhm
        adj = b.min_fwhm
        adj.setRange(0.1, 200.0)
        adj.setSingleStep(1.0)
        adj.setValue(self.min_fwhm)
        def chg_min(val):
            self.min_fwhm = val
            self.w.lbl_min_fwhm.setText(str(self.min_fwhm))
            return True
        b.lbl_min_fwhm.setText(str(self.min_fwhm))
        b.min_fwhm.valueChanged.connect(chg_min)

        # max fwhm
        adj = b.max_fwhm
        adj.setRange(0.1, 200.0)
        adj.setSingleStep(1.0)
        adj.setValue(self.max_fwhm)
        def chg_max(val):
            self.max_fwhm = val
            self.w.lbl_max_fwhm.setText(str(self.max_fwhm))
            return True
        b.lbl_max_fwhm.setText(str(self.max_fwhm))
        b.max_fwhm.valueChanged.connect(chg_max)

        # Ellipticity control
        def chg_ellipticity():
            minellipse = None
            val = str(self.w.ellipticity.text()).strip()
            if len(val) > 0:
                minellipse = float(val)
            self.min_ellipse = minellipse
            self.w.lbl_ellipticity.setText(str(self.min_ellipse))
            return True
        b.lbl_ellipticity.setText(str(self.min_ellipse))
        b.ellipticity.returnPressed.connect(chg_ellipticity)

        # Edge control
        def chg_edgew():
            edgew = None
            val = str(self.w.edge.text()).strip()
            if len(val) > 0:
                edgew = float(val)
            self.edgew = edgew
            self.w.lbl_edge.setText(str(self.edgew))
            return True
        b.lbl_edge.setText(str(self.edgew))
        b.edge.returnPressed.connect(chg_edgew)

        adj = b.max_side
        adj.setRange(5, 10000)
        adj.setSingleStep(10)
        adj.setValue(self.max_side)
        def chg_max_side(val):
            self.max_side = val
            self.w.lbl_max_side.setText(str(self.max_side))
            return True
        b.lbl_max_side.setText(str(self.max_side))
        b.max_side.valueChanged.connect(chg_max_side)

        b.redo_pick.clicked.connect(self.redo)

        nb.addTab(w, "Settings")

        captions = (
            ('Sky cut', 'button', 'Delta sky', 'entry'),
            ('Bright cut', 'button', 'Delta bright', 'entry'),
            )

        w, b = QtHelp.build_info(captions)
        self.w.update(b)

        b.sky_cut.setToolTip("Set image low cut to Sky Level")
        b.delta_sky.setToolTip("Delta to apply to low cut")
        b.bright_cut.setToolTip("Set image high cut to Sky Level+Brightness")
        b.delta_bright.setToolTip("Delta to apply to high cut")

        b.sky_cut.setEnabled(False)
        self.w.btn_sky_cut = b.sky_cut
        self.w.btn_sky_cut.clicked.connect(self.sky_cut)
        self.w.sky_cut_delta = b.delta_sky
        b.delta_sky.setText(str(self.delta_sky))
        b.bright_cut.setEnabled(False)
        self.w.btn_bright_cut = b.bright_cut
        self.w.btn_bright_cut.clicked.connect(self.bright_cut)
        self.w.bright_cut_delta = b.delta_bright
        b.delta_bright.setText(str(self.delta_bright))

        nb.addTab(w, "Controls")

        btns = QtHelp.HBox()
        layout = btns.layout()
        layout.setSpacing(3)
        #btns.set_child_size(15, -1)

        btn = QtGui.QPushButton("Close")
        btn.clicked.connect(self.close)
        layout.addWidget(btn, stretch=0, alignment=QtCore.Qt.AlignLeft)
        vbox.addWidget(btns, stretch=0, alignment=QtCore.Qt.AlignLeft)

        vpaned.addWidget(sw)
        
        container.addWidget(vpaned, stretch=1)
        #vpaned.moveSplitter(260, 1)

    def bump_serial(self):
        with self.lock:
            self.serialnum += 1
            return self.serialnum
        
    def get_serial(self):
        with self.lock:
            return self.serialnum
        
    def plot_panzoom(self):
        ht, wd = self.contour_data.shape
        x = int(self.plot_panx * wd)
        y = int(self.plot_pany * ht)

        if self.plot_zoomlevel >= 1.0:
            scalefactor = 1.0 / self.plot_zoomlevel
        elif self.plot_zoomlevel < -1.0:
            scalefactor = - self.plot_zoomlevel
        else:
            # wierd condition?--reset to 1:1
            scalefactor = 1.0
            self.plot_zoomlevel = 1.0

        # Show contour zoom level
        text = self.fv.scale2text(1.0/scalefactor)
        self.wdetail.contour_zoom.setText(text)

        xdelta = int(scalefactor * (wd/2.0))
        ydelta = int(scalefactor * (ht/2.0))
        xlo, xhi = x-xdelta, x+xdelta
        # distribute remaining x space from plot
        if xlo < 0:
            xsh = abs(xlo)
            xlo, xhi = 0, min(wd-1, xhi+xsh)
        elif xhi >= wd:
            xsh = xhi - wd
            xlo, xhi = max(0, xlo-xsh), wd-1
        self.w.ax.set_xlim(xlo, xhi)

        ylo, yhi = y-ydelta, y+ydelta
        # distribute remaining y space from plot
        if ylo < 0:
            ysh = abs(ylo)
            ylo, yhi = 0, min(ht-1, yhi+ysh)
        elif yhi >= ht:
            ysh = yhi - ht
            ylo, yhi = max(0, ylo-ysh), ht-1
        self.w.ax.set_ylim(ylo, yhi)

        self.w.fig.canvas.draw()

    def plot_contours(self):
        # Make a contour plot

        ht, wd = self.pick_data.shape

        # If size of pick region is too large, carve out a subset around
        # the picked object coordinates for plotting contours
        maxsize = max(ht, wd)
        if maxsize > self.contour_size_limit:
            image = self.fitsimage.get_image()
            radius = int(self.contour_size_limit // 2)
            x, y = self.pick_qs.x, self.pick_qs.y
            data, x1, y1, x2, y2 = image.cutout_radius(x, y, radius)
            x, y = x - x1, y - y1
            ht, wd = data.shape
        else:
            data = self.pick_data
            x, y = self.pickcenter.x, self.pickcenter.y
        self.contour_data = data
        # Set pan position in contour plot
        self.plot_panx = float(x) / wd
        self.plot_pany = float(y) / ht

        self.w.ax.cla()
        try:
            # Create a contour plot
            xarr = numpy.arange(wd)
            yarr = numpy.arange(ht)
            self.w.ax.contourf(xarr, yarr, data, self.num_contours)
            # Mark the center of the object
            x, y = self.pickcenter.x, self.pickcenter.y
            self.w.ax.plot([x], [y], marker='x', ms=20.0,
                           color='black')

            # Set the pan and zoom position & redraw
            self.plot_panzoom()
            
        except Exception, e:
            self.logger.error("Error making contour plot: %s" % (
                str(e)))

    def clear_contours(self):
        self.w.ax.cla()
        
    def _plot_fwhm_axis(self, arr, medv, color1, color2, color3):
        N = len(arr)
        X = numpy.array(range(N))
        Y = arr
        # subtract sky background
        ## medv = numpy.median(Y)
        Y = Y - medv
        maxv = Y.max()
        # clamp to 0..max
        Y = Y.clip(0, maxv)
        self.logger.debug("Y=%s" % (str(Y)))
        self.w.ax2.plot(X, Y, color=color1, marker='.')

        fwhm, mu, sdev, maxv = self.iqcalc.calc_fwhm(arr)
        Z = numpy.array([self.iqcalc.gaussian(x, (mu, sdev, maxv)) for x in X])
        self.w.ax2.plot(X, Z, color=color1, linestyle=':')
        self.w.ax2.axvspan(mu-fwhm/2.0, mu+fwhm/2.0,
                           facecolor=color3, alpha=0.25)
        return (fwhm, mu, sdev, maxv)

    def clear_fwhm(self):
        self.w.ax2.cla()
        
    def plot_fwhm(self, qs):
        # Make a FWHM plot
        self.w.ax2.cla()
        x, y, radius = qs.x, qs.y, qs.fwhm_radius
        try:
            image = self.fitsimage.get_image()
            x0, y0, xarr, yarr = image.cutout_cross(x, y, radius)

            # get median value from the cutout area
            medv = numpy.median(self.pick_data)
            self.logger.debug("cutting x=%d y=%d r=%d med=%f" % (
                x, y, radius, medv))
            
            self.logger.debug("xarr=%s" % (str(xarr)))
            fwhm_x, mu, sdev, maxv = self._plot_fwhm_axis(xarr, medv,
                                                          'blue', 'blue', 'skyblue')

            self.logger.debug("yarr=%s" % (str(yarr)))
            fwhm_y, mu, sdev, maxv = self._plot_fwhm_axis(yarr, medv,
                                                          'green', 'green', 'seagreen')
            
            plt = self.w.ax2
            plt.legend(('data x', 'gauss x', 'data y', 'gauss y'),
                       'upper right', shadow=False, fancybox=False,
                       prop={'size': 8}, labelspacing=0.2)
            plt.set_title("FWHM X: %.2f  Y: %.2f" % (fwhm_x, fwhm_y))

            self.w.fig2.canvas.draw()
        except Exception, e:
            self.logger.error("Error making fwhm plot: %s" % (
                str(e)))

    def close(self):
        chname = self.fv.get_channelName(self.fitsimage)
        self.fv.stop_operation_channel(chname, str(self))
        return True
        
    def instructions(self):
        self.tw.setText("""Left-click to place region.  Left-drag to position region.  Redraw region with the right mouse button.""")
            
    def start(self):
        self.instructions()
        # insert layer if it is not already
        try:
            obj = self.fitsimage.getObjectByTag(self.layertag)

        except KeyError:
            # Add canvas layer
            self.fitsimage.add(self.canvas, tag=self.layertag)
            
        self.resume()

    def pause(self):
        self.canvas.ui_setActive(False)
        
    def resume(self):
        self.canvas.ui_setActive(True)
        self.fv.showStatus("Draw a rectangle with the right mouse button")
        
    def stop(self):
        # Delete previous peak marks
        objs = self.fitsimage.getObjectsByTagpfx('peak')
        self.fitsimage.deleteObjects(objs, redraw=False)

        # deactivate the canvas 
        self.canvas.ui_setActive(False)
        try:
            self.fitsimage.deleteObjectByTag(self.layertag)
        except:
            pass
        self.fv.showStatus("")
        
    def redo(self):
        serialnum = self.bump_serial()
        self.ev_intr.set()
        
        fig = self.canvas.getObjectByTag(self.picktag)
        if fig.kind != 'compound':
            return True
        bbox  = fig.objects[0]
        point = fig.objects[1]
        text = fig.objects[2]
        data_x, data_y = point.x, point.y

        # set the pick image to have the same cut levels and transforms
        self.fitsimage.copy_attributes(self.pickimage,
                                       ['transforms', 'cutlevels',
                                        'rgbmap'],
                                       redraw=False)
        
        try:
            image = self.fitsimage.get_image()

            # sanity check on region
            width = bbox.x2 - bbox.x1
            height = bbox.y2 - bbox.y1
            if (width > self.max_side) or (height > self.max_side):
                errmsg = "Image area (%dx%d) too large!" % (
                    width, height)
                self.fv.show_error(errmsg)
                raise Exception(errmsg)
        
            # Note: FITS coordinates are 1-based, whereas numpy FITS arrays
            # are 0-based
            fits_x, fits_y = data_x + 1, data_y + 1

            # Cut and show pick image in pick window
            #self.pick_x, self.pick_y = data_x, data_y
            self.logger.debug("bbox %f,%f %f,%f" % (bbox.x1, bbox.y1,
                                                    bbox.x2, bbox.y2))
            x1, y1, x2, y2, data = self.cutdetail(self.fitsimage,
                                                  self.pickimage,
                                                  int(bbox.x1), int(bbox.y1),
                                                  int(bbox.x2), int(bbox.y2))
            self.logger.debug("cut box %f,%f %f,%f" % (x1, y1, x2, y2))

            # calculate center of pick image
            wd, ht = self.pickimage.get_data_size()
            xc = wd // 2
            yc = ht // 2
            if not self.pickcenter:
                tag = self.pickimage.add(CanvasTypes.Point(xc, yc, 5,
                                                           linewidth=1,
                                                           color='red'))
                self.pickcenter = self.pickimage.getObjectByTag(tag)
            
            self.pick_x1, self.pick_y1 = x1, y1
            self.pick_data = data
            self.wdetail.sample_area.setText('%dx%d' % (x2-x1, y2-y1))

            point.color = 'red'
            text.text = 'Pick: calc'
            self.pickcenter.x = xc
            self.pickcenter.y = yc
            self.pickcenter.color = 'red'

            # clear contour and fwhm plots
            if have_mpl:
                self.clear_contours()
                self.clear_fwhm()

            # Delete previous peak marks
            objs = self.fitsimage.getObjectsByTagpfx('peak')
            self.fitsimage.deleteObjects(objs, redraw=False)

            # Offload this task to another thread so that GUI remains
            # responsive
            self.fv.nongui_do(self.search, serialnum, data,
                              x1, y1, wd, ht, fig)

        except Exception, e:
            self.logger.error("Error calculating quality metrics: %s" % (
                str(e)))
            return True

    def update_status(self, text):
        self.fv.gui_do(self.w.eval_status.setText, text)

    def init_progress(self):
        self.w.btn_intr_eval.setEnabled(True)
        self.w.eval_pgs.setValue(0)
        #self.w.eval_pgs.set_text("%.2f %%" % (0.0))
            
    def update_progress(self, pct):
        self.w.eval_pgs.setValue(int(pct * 100.0))
        #self.w.eval_pgs.set_text("%.2f %%" % (pct*100.0))
        
    def search(self, serialnum, data, x1, y1, wd, ht, fig):
        if serialnum != self.get_serial():
            return
        with self.lock2:
            self.pgs_cnt = 0
            self.ev_intr.clear()
            self.fv.gui_call(self.init_progress)
            
            msg, results, qs = None, None, None
            try:
                self.update_status("Finding bright peaks...")
                # Find bright peaks in the cutout
                peaks = self.iqcalc.find_bright_peaks(data,
                                                      threshold=self.threshold,
                                                      radius=self.radius)
                num_peaks = len(peaks)
                if num_peaks == 0:
                    raise Exception("Cannot find bright peaks")

                def cb_fn(obj):
                    self.pgs_cnt += 1
                    pct = float(self.pgs_cnt) / num_peaks
                    self.fv.gui_do(self.update_progress, pct)

                # Evaluate those peaks
                self.update_status("Evaluating %d bright peaks..." % (
                    num_peaks))
                objlist = self.iqcalc.evaluate_peaks(peaks, data,
                                                     fwhm_radius=self.radius,
                                                     cb_fn=cb_fn,
                                                     ev_intr=self.ev_intr)
                num_candidates = len(objlist)
                if num_candidates == 0:
                    raise Exception("Error evaluating bright peaks: no candidates found")

                self.update_status("Selecting from %d candidates..." % (
                    num_candidates))
                height, width = data.shape
                results = self.iqcalc.objlist_select(objlist, width, height,
                                                     minfwhm=self.min_fwhm,
                                                     maxfwhm=self.max_fwhm,
                                                     minelipse=self.min_ellipse,
                                                     edgew=self.edgew)

                if len(results) == 0:
                    raise Exception("No object matches selection criteria")
                qs = results[0]

            except Exception, e:
                msg = str(e)
                self.update_status(msg)

            if serialnum == self.get_serial():
                self.fv.gui_do(self.update_pick, serialnum, results, qs,
                               x1, y1, wd, ht, fig, msg)

    def update_pick(self, serialnum, objlist, qs, x1, y1, wd, ht, fig, msg):
        if serialnum != self.get_serial():
            return
        
        try:
            image = self.fitsimage.get_image()
            point = fig.objects[1]
            text = fig.objects[2]
            text.text = "Pick"

            if msg != None:
                raise Exception(msg)
            
            # Mark new peaks, if desired
            if self.show_candidates:
                for obj in objlist:
                    tag = self.fitsimage.add(CanvasTypes.Point(x1+obj.objx,
                                                               y1+obj.objy,
                                                               5,
                                                               linewidth=1,
                                                               color=self.candidate_color),
                                             tagpfx='peak', redraw=False)

            # Add back in offsets into image to get correct values with respect
            # to the entire image
            qs.x += x1
            qs.y += y1
            qs.objx += x1
            qs.objy += y1

            # Calculate X/Y of center of star
            obj_x = qs.objx
            obj_y = qs.objy
            self.logger.info("object center is x,y=%f,%f" % (obj_x, obj_y))
            fwhm = qs.fwhm
            fwhm_x, fwhm_y = qs.fwhm_x, qs.fwhm_y
            point.x, point.y = obj_x, obj_y
            text.color = 'cyan'

            self.wdetail.fwhm_x.setText('%.3f' % fwhm_x)
            self.wdetail.fwhm_y.setText('%.3f' % fwhm_y)
            self.wdetail.fwhm.setText('%.3f' % fwhm)
            self.wdetail.object_x.setText('%.3f' % (obj_x+1))
            self.wdetail.object_y.setText('%.3f' % (obj_y+1))
            self.wdetail.sky_level.setText('%.3f' % qs.skylevel)
            self.wdetail.background.setText('%.3f' % qs.background)
            self.wdetail.brightness.setText('%.3f' % qs.brightness)

            self.w.btn_sky_cut.setEnabled(True)
            self.w.btn_bright_cut.setEnabled(True)

            # Mark center of object on pick image
            i1 = point.x - x1
            j1 = point.y - y1
            self.pickcenter.x = i1
            self.pickcenter.y = j1
            self.pickcenter.color = 'cyan'
            self.pick_qs = qs
            self.pickimage.panset_xy(i1, j1, redraw=False)

            # Mark object center on image
            point.color = 'cyan'
            self.fitsimage.panset_xy(obj_x, obj_y, redraw=False)

            # Calc RA, DEC, EQUINOX of X/Y center pixel
            try:
                ra_txt, dec_txt = image.pixtoradec(obj_x, obj_y, format='str')
            except Exception, e:
                ra_txt = 'WCS ERROR'
                dec_txt = 'WCS ERROR'
            self.wdetail.ra.setText(ra_txt)
            self.wdetail.dec.setText(dec_txt)

            equinox = image.get_keyword('EQUINOX', 'UNKNOWN')
            self.wdetail.equinox.setText(str(equinox))

            # TODO: Get separate FWHM for X and Y
            try:
                cdelt1, cdelt2 = image.get_keywords_list('CDELT1', 'CDELT2')
                starsize = self.iqcalc.starsize(fwhm_x, cdelt1, fwhm_y, cdelt2)
                self.wdetail.star_size.setText('%.3f' % starsize)
            except Exception, e:
                self.wdetail.star_size.setText('ERROR')
                self.fv.show_error("Couldn't calculate star size: %s" % (
                    str(e)), raisetab=False)

            self.update_status("Done")
            self.plot_panx = float(i1) / wd
            self.plot_pany = float(j1) / ht
            if have_mpl:
                self.plot_contours()
                self.plot_fwhm(qs)

        except Exception, e:
            errmsg = "Error calculating quality metrics: %s" % (
                str(e))
            self.logger.error(errmsg)
            self.fv.show_error(errmsg, raisetab=False)
            for key in ('sky_level', 'background', 'brightness',
                        'star_size', 'fwhm_x', 'fwhm_y'):
                self.wdetail[key].setText('')
            self.wdetail.fwhm.setText('Failed')
            self.w.btn_sky_cut.setEnabled(False)
            self.w.btn_bright_cut.setEnabled(False)
            self.pick_qs = None
            text.color = 'red'

            self.plot_panx = self.plot_pany = 0.5
            #self.plot_contours()
            # TODO: could calc background based on numpy calc

        self.w.btn_intr_eval.setEnabled(False)
        self.pickimage.redraw(whence=3)
        self.canvas.redraw(whence=3)

        self.fv.showStatus("Click left mouse button to reposition pick")
        return True
    
    def eval_intr(self):
        self.ev_intr.set()
        
    def btndown(self, canvas, button, data_x, data_y):
        if not (button == 0x1):
            return
        
        try:
            obj = self.canvas.getObjectByTag(self.picktag)
            if obj.kind == 'rectangle':
                bbox = obj
            else:
                bbox  = obj.objects[0]
                point = obj.objects[1]
            self.dx = (bbox.x2 - bbox.x1) // 2
            self.dy = (bbox.y2 - bbox.y1) // 2
        except Exception, e:
            pass

        dx = self.dx
        dy = self.dy
        
        # Mark center of object and region on main image
        try:
            self.canvas.deleteObjectByTag(self.picktag, redraw=False)
        except:
            pass

        x1, y1 = data_x - dx, data_y - dy
        x2, y2 = data_x + dx, data_y + dy
        
        tag = self.canvas.add(CanvasTypes.Rectangle(x1, y1, x2, y2,
                                                    color='cyan',
                                                    linestyle='dash'))
        self.picktag = tag

        #self.setpickregion(self.canvas, tag)
        
    def update(self, canvas, button, data_x, data_y):
        if not (button == 0x1):
            return
        
        try:
            obj = self.canvas.getObjectByTag(self.picktag)
            if obj.kind == 'rectangle':
                bbox = obj
            else:
                bbox  = obj.objects[0]
                point = obj.objects[1]
            self.dx = (bbox.x2 - bbox.x1) // 2
            self.dy = (bbox.y2 - bbox.y1) // 2
        except Exception, e:
            obj = None
            pass

        dx = self.dx
        dy = self.dy
        
        x1, y1 = data_x - dx, data_y - dy
        x2, y2 = data_x + dx, data_y + dy
        
        if (not obj) or (obj.kind == 'compound'):
            # Replace compound image with rectangle
            try:
                self.canvas.deleteObjectByTag(self.picktag, redraw=False)
            except:
                pass

            tag = self.canvas.add(CanvasTypes.Rectangle(x1, y1, x2, y2,
                                                        color='cyan',
                                                        linestyle='dash'),
                                  redraw=False)
        else:
            # Update current rectangle with new coords
            bbox.x1, bbox.y1, bbox.x2, bbox.y2 = x1, y1, x2, y2
            tag = self.picktag

        self.setpickregion(self.canvas, tag)

        
    def drag(self, canvas, button, data_x, data_y):
        if not (button == 0x1):
            return

        obj = self.canvas.getObjectByTag(self.picktag)
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

        if (not obj) or (obj.kind == 'compound'):
            # Replace compound image with rectangle
            try:
                self.canvas.deleteObjectByTag(self.picktag, redraw=False)
            except:
                pass

            self.picktag = self.canvas.add(CanvasTypes.Rectangle(x1, y1, x2, y2,
                                                                 color='cyan',
                                                                 linestyle='dash'))
        else:
            # Update current rectangle with new coords and redraw
            bbox.x1, bbox.y1, bbox.x2, bbox.y2 = x1, y1, x2, y2
            self.canvas.redraw(whence=3)


    def setpickregion(self, canvas, tag):
        obj = canvas.getObjectByTag(tag)
        if obj.kind != 'rectangle':
            return True
        canvas.deleteObjectByTag(tag, redraw=False)

        if self.picktag:
            try:
                canvas.deleteObjectByTag(self.picktag, redraw=False)
            except:
                pass

        # determine center of rectangle
        x = obj.x1 + (obj.x2 - obj.x1) // 2
        y = obj.y1 + (obj.y2 - obj.y1) // 2
        
        tag = canvas.add(CanvasTypes.CompoundObject(
            CanvasTypes.Rectangle(obj.x1, obj.y1, obj.x2, obj.y2,
                                  color=self.pickcolor),
            CanvasTypes.Point(x, y, 10, color='red'),
            CanvasTypes.Text(obj.x1, obj.y2+4, "Pick",
                             color=self.pickcolor)),
                         redraw=False)
        self.picktag = tag

        #self.fv.raise_tab("detail")
        return self.redo()
    
    def reset_region(self):
        self.dx = region_default_width
        self.dy = region_default_height

        obj = self.canvas.getObjectByTag(self.picktag)
        if obj.kind != 'compound':
            return True
        bbox = obj.objects[0]
    
        # calculate center of bbox
        wd = bbox.x2 - bbox.x1
        dw = wd // 2
        ht = bbox.y2 - bbox.y1
        dh = ht // 2
        x, y = bbox.x1 + dw, bbox.y1 + dh

        # calculate new coords
        bbox.x1, bbox.y1, bbox.x2, bbox.y2 = (x-self.dx, y-self.dy,
                                              x+self.dx, y+self.dy)

        self.redo()


    def sky_cut(self):
        if not self.pick_qs:
            self.fv.showStatus("Please pick an object to set the sky level!")
            return
        loval = self.pick_qs.skylevel
        delta = self.w.sky_cut_delta.text()
        if len(delta) == 0:
            delta = 0.0
        oldlo, hival = self.fitsimage.get_cut_levels()
        try:
            self.delta_sky = float(delta)
            loval += self.delta_sky
            self.fitsimage.cut_levels(loval, hival)
            
        except Exception, e:
            self.fv.showStatus("No valid sky level: '%s'" % (loval))
            
    def bright_cut(self):
        if not self.pick_qs:
            self.fv.showStatus("Please pick an object to set the brightness!")
            return
        skyval = self.pick_qs.skylevel
        hival = self.pick_qs.brightness
        delta = self.w.bright_cut_delta.text()
        if len(delta) == 0:
            delta = 0.0
        loval, oldhi = self.fitsimage.fitsimage.get_cut_levels()
        try:
            self.delta_bright = float(delta)
            # brightness is measured ABOVE sky level
            hival = skyval + hival + self.delta_bright
            self.fitsimage.cut_levels(loval, hival)
            
        except Exception, e:
            self.fv.showStatus("No valid brightness level: '%s'" % (hival))
            
    def zoomset(self, fitsimage, zoomlevel, scale_x, scale_y):
        scalefactor = fitsimage.get_scale()
        self.logger.debug("scalefactor = %.2f" % (scalefactor))
        text = self.fv.scale2text(scalefactor)
        self.wdetail.zoom.setText(text)

    def detailxy(self, canvas, button, data_x, data_y):
        """Motion event in the pick fits window.  Show the pointing
        information under the cursor.
        """
        if button == 0:
            # TODO: we could track the focus changes to make this check
            # more efficient
            fitsimage = self.fv.getfocus_fitsimage()
            # Don't update global information if our fitsimage isn't focused
            if fitsimage != self.fitsimage:
                return True
        
            # Add offsets from cutout
            data_x = data_x + self.pick_x1
            data_y = data_y + self.pick_y1

            return self.fv.showxy(self.fitsimage, data_x, data_y)

    def cutdetail(self, srcimage, dstimage, x1, y1, x2, y2, redraw=True):
        image = srcimage.get_image()
        data, x1, y1, x2, y2 = image.cutout_adjust(x1, y1, x2, y2)

        dstimage.set_data(data, redraw=redraw)

        return (x1, y1, x2, y2, data)

    def show_candidates_cb(self, tf):
        self.show_candidates = tf
        if not self.show_candidates:
            # Delete previous peak marks
            objs = self.fitsimage.getObjectsByTagpfx('peak')
            self.fitsimage.deleteObjects(objs, redraw=True)
        
    def plot_scroll(self, event):
        delta = event.delta()
        direction = None
        if delta > 0:
            direction = 'up'
        elif delta < 0:
            direction = 'down'
        if direction == 'up':
            #delta = 0.9
            self.plot_zoomlevel += 1.0
        elif direction == 'down':
            #delta = 1.1
            self.plot_zoomlevel -= 1.0

        self.plot_panzoom()
        
##         x1, x2 = self.w.ax.get_xlim()
##         y1, y2 = self.w.ax.get_ylim()
##         self.w.ax.set_xlim(x1*delta, x2*delta)
##         self.w.ax.set_ylim(y1*delta, y2*delta)
##         self.w.canvas.draw()
        
    def pan_plot(self, xdelta, ydelta):
        x1, x2 = self.w.ax.get_xlim()
        y1, y2 = self.w.ax.get_ylim()
        
        self.w.ax.set_xlim(x1+xdelta, x2+xdelta)
        self.w.ax.set_ylim(y1+ydelta, y2+ydelta)
        self.w.canvas.draw()
        
    def plot_button_press(self, event):
        buttons = event.buttons()
        x, y = event.x(), event.y()

        button = 0
        if buttons & QtCore.Qt.LeftButton:
            button |= 0x1
        if buttons & QtCore.Qt.MidButton:
            button |= 0x2
        if buttons & QtCore.Qt.RightButton:
            button |= 0x4
        self.logger.debug("button down event at %dx%d, button=%x" % (
            x, y, button))

        self.plot_x, self.plot_y = x, y
        return True

    def plot_button_release(self, event):
        # note: for mouseRelease this needs to be button(), not buttons()!
        buttons = event.button()
        x, y = event.x(), event.y()
        
        button = self.kbdmouse_mask
        if buttons & QtCore.Qt.LeftButton:
            button |= 0x1
        if buttons & QtCore.Qt.MidButton:
            button |= 0x2
        if buttons & QtCore.Qt.RightButton:
            button |= 0x4
        self.logger.debug("button release at %dx%d button=%x" % (x, y, button))
            
    def plot_motion_notify(self, event):
        buttons = event.buttons()
        x, y = event.x(), event.y()
        
        button = 0
        if buttons & QtCore.Qt.LeftButton:
            button |= 0x1
        if buttons & QtCore.Qt.MidButton:
            button |= 0x2
        if buttons & QtCore.Qt.RightButton:
            button |= 0x4

        if button & 0x1:
            xdelta = x - self.plot_x
            ydelta = y - self.plot_y
            self.pan_plot(xdelta, ydelta)

    def __str__(self):
        return 'pick'

class MyFigureCanvas(FigureCanvas):

    def setDelegate(self, delegate):
        self.delegate = delegate
        
    def keyPressEvent(self, event):
        self.delegate.pan_plot(event)
        
    def mousePressEvent(self, event):
        self.delegate.plot_button_press(event)

    def mouseReleaseEvent(self, event):
        self.delegate.plot_button_release(event)

    def mouseMoveEvent(self, event):
        self.delegate.plot_motion_notify(event)

    def wheelEvent(self, event):
        self.delegate.plot_scroll(event)

        
    
#END
