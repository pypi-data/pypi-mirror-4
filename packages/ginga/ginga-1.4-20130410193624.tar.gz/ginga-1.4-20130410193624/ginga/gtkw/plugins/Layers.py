#
# Layers.py -- Layers plugin for fits viewer
# 
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c) Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
import gtk
#import pango
from ginga.gtkw import GtkHelp

import numpy
import re, os
import time

from ginga.misc import Bunch
from ginga import BaseImage, LayerImage
from ginga import GingaPlugin
from ginga.gtkw import FitsImageCanvasGtk

class Layers(GingaPlugin.LocalPlugin):

    def __init__(self, fv, fitsimage):
        # superclass defines some variables for us, like logger
        super(Layers, self).__init__(fv, fitsimage)

        self.lidx = 0
        self.limage = None
        self.naxispath = []
        self.compositing = 'alpha'

    def build_gui(self, container):
        vpaned = gtk.VPaned()

        sfi = FitsImageCanvasGtk.FitsImageCanvas(logger=None)
        sfi.enable_autozoom('on')
        sfi.enable_autocuts('on')
        sfi.enable_flip(True)
        sfi.enable_rotate(True)
        sfi.enable_pan(True)
        #sfi.set_zoom_algorithm('rate')
        sfi.enable_zoom(True)
        sfi.enable_draw(False)
        sfi.enable_cuts(True)
        sfi.set_bg(0.4, 0.4, 0.4)
        self.layerimage = sfi

        iw = sfi.get_widget()
        self.w.layerimage = iw
        iw.set_size_request(200, 200)
        iw.show()
        vpaned.pack1(iw, resize=True, shrink=True)

        sw = gtk.ScrolledWindow()
        sw.set_border_width(2)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox1 = gtk.VBox()
        sw.add_with_viewport(vbox1)

        fr = gtk.Frame("Compositing")
        fr.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        fr.set_label_align(0.5, 0.5)

        captions = (("Combine", 'combobox'),
                    ("New Image", 'button'),
                    ("Layer Name", 'entry'),
                    ("Layer Alpha", 'hscale'),
                    ("Insert Image", 'button'),
                    ("Store Mask", 'button'),
                    ("Insert Color", 'button', "Color", 'hbox'),
                    ("Bit Plane", 'entry'),
                    ("Decompose", 'button', "Std Greyscale", 'button'),
                    )
        w, b = GtkHelp.build_info(captions)
        self.w.update(b)

        combobox = b.combine
        index = 0
        for name in ('Alpha', 'RGB'):
            combobox.insert_text(index, name)
            index += 1
        combobox.set_active(0)
        combobox.sconnect('changed', self.set_combine_cb)

        b.new_image.connect('clicked', lambda w: self.new_cb())
        b.insert_image.connect('clicked', lambda w: self.insert_cb())
        b.insert_color.connect('clicked', lambda w: self.insert_colored_cb2())
        b.store_mask.connect('clicked', lambda w: self.store_mask_cb())
        b.decompose.connect('clicked', lambda w: self.decompose_cb())
        b.std_greyscale.connect('clicked', lambda w: self.std_greyscale_cb())

        scale = b.layer_alpha
        adj = scale.get_adjustment()
        lower, upper = 0.0, 1.0
        adj.configure(upper, lower, upper, upper/100.0, upper/10.0, 0.0)
        scale.set_digits(3)
        scale.set_draw_value(True)
        scale.set_value_pos(gtk.POS_BOTTOM)
        scale.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
        scale.add_mark(lower, gtk.POS_BOTTOM, "%.1f" % lower)
        scale.add_mark(upper, gtk.POS_BOTTOM, "%.1f" % upper)

        clrbtn = gtk.ColorButton()
        self.w.clrbtn = clrbtn
        b.color.pack_start(clrbtn, padding=2, fill=True, expand=False)
        
        fr.add(w)
        vbox1.pack_start(fr, padding=4, fill=True, expand=False)

        fr = gtk.Frame("Layers")
        
        fr.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        fr.set_label_align(0.5, 0.5)

        self.w.scales = gtk.VBox()
        fr.add(self.w.scales)
        vbox1.pack_start(fr, padding=4, fill=True, expand=False)

        btns = gtk.HButtonBox()
        btns.set_layout(gtk.BUTTONBOX_START)
        btns.set_spacing(3)
        btns.set_child_size(15, -1)

        btn = gtk.Button("Close")
        btn.connect('clicked', lambda w: self.close())
        btns.add(btn)
        vbox1.pack_start(btns, padding=4, fill=True, expand=False)

        vpaned.pack2(sw, resize=True, shrink=True)
        vpaned.set_position(280)
        vpaned.show_all()
        
        container.pack_start(vpaned, padding=0, fill=True, expand=True)

    def _config_scale(self, idx):
        scale = GtkHelp.HScale()
        adj = scale.get_adjustment()
        lower, upper = 0.0, 1.0
        adj.configure(upper, lower, upper, upper/100.0, upper/10.0, 0.0)
        scale.set_digits(3)
        scale.set_draw_value(True)
        scale.set_value_pos(gtk.POS_BOTTOM)
        scale.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
        scale.add_mark(lower, gtk.POS_BOTTOM, "%.1f" % lower)
        scale.add_mark(upper, gtk.POS_BOTTOM, "%.1f" % upper)
        scale.sconnect('value-changed', self.set_opacity_cb, idx)
        scale.set_size_request(200, -1)
        return scale

    def _gui_config_layers(self):
        # remove all old scales
        for child in self.w.scales.get_children():
            self.w.scales.remove(child)

        # construct a new vbox of sliders
        vbox = gtk.VBox()
        num_layers = self.limage.numLayers()
        for i in xrange(num_layers):
            layer = self.limage.getLayer(i)
            hbox = gtk.HBox()
            scale = self._config_scale(i)
            scale.set_value(layer.alpha)
            lbl = gtk.Label("%-12.12s" % (layer.name))
            hbox.pack_start(lbl, expand=False, fill=False)
            hbox.pack_end(scale, expand=True, fill=True)
            vbox.pack_start(hbox, expand=False, fill=True)
        vbox.show_all()

        self.w.scales.pack_start(vbox, expand=True, fill=True)
        
            
    # def set_layer_cb(self, w):
    #     idx = w.get_active()
    #     self.lidx = idx
    #     layer = self.limage.getLayer(self.lidx)
    #     val = numpy.mean(layer.alpha)
    #     self.w.opacity.set_value(val)
        
    def set_combine_cb(self, w):
        if self.limage == None:
            self.new_cb()
        idx = w.get_active()
        combine = ['alpha', 'rgb']
        name = combine[idx]
        self.limage.setComposeType(name)
        #self.fitsimage.redraw(whence=0)

    def get_imageclass(self, imageclass):
        # create a dynamic image class that has the LayerImage mixin
        class klass(imageclass, LayerImage.LayerImage):
            def __init__(self, *args, **kwdargs):
                imageclass.__init__(self, *args, **kwdargs)
                LayerImage.LayerImage.__init__(self)
        return klass
    
    def new_cb(self, imageclass=BaseImage.BaseImage):
        klass = self.get_imageclass(imageclass)
        name = str(time.time())
        self.limage = klass(logger=self.logger)
        #self.limage.add_callback('modified', )
        self._gui_config_layers()
        self.limage.set(name=name)

        # Reflect transforms, colormap, etc.
        self.fitsimage.copy_attributes(self.layerimage,
                                       ['transforms', 'cutlevels',
                                        'rgbmap', 'rotation'],
                                       redraw=False)

    def _get_layer_attributes(self):
        # Get layer name
        s = self.w.layer_name.get_text().strip()
        if len(s) > 0:
            name = s
        else:
            name = None

        # Get alpha
        alpha = self.w.layer_alpha.get_value()
        bnch = Bunch.Bunch(name=name, alpha=alpha)
        return bnch
        
    def insert_cb(self):
        image = self.fitsimage.get_image()
        attrs = self._get_layer_attributes()
        if self.limage == None:
            self.new_cb(imageclass=image.__class__)
            print "getting metadata"
            metadata = image.get_metadata()
            print "updating metadata"
            self.limage.update_metadata(metadata)
        print "inserting layer"
        self.limage.insertLayer(0, image, name=attrs.name,
                                alpha=attrs.alpha)
        self._gui_config_layers()

        #self.fitsimage.set_image(self.limage)
        name = self.limage.get('name')
        self.layerimage.set_image(self.limage)
        self.fv.add_image(name, self.limage)
        print "insert done"
        
    ## def insert_colored_cb(self):
    ##     image = self.fitsimage.get_image()
    ##     imageclass = image.__class__
    ##     if self.limage == None:
    ##         self.new_cb(imageclass=imageclass)

    ##     klass = self.get_imageclass(imageclass)
    ##     cimage = klass(logger=self.logger)
    ##     color = self.w.clrbtn.get_color()
    ##     cimage.insertLayer(0, image, alpha=color.red_float,
    ##                        name="Red")
    ##     cimage.insertLayer(1, image, alpha=color.green_float,
    ##                        name="Green")
    ##     cimage.insertLayer(2, image, alpha=color.blue_float,
    ##                        name="Blue")
    ##     cimage.setComposeType('rgb')
        
    ##     attrs = self._get_layer_attributes()
    ##     self.limage.insertLayer(0, cimage, name=attrs.name,
    ##                             alpha=attrs.alpha)
    ##     self._gui_config_layers()

    ##     self.layerimage.set_image(self.limage)
    ##     name = self.limage.get('name')
    ##     self.fv.add_image(name, self.limage)
        
    def store_mask_cb(self):
        image = self.fitsimage.get_image()
        self.mask_image = image
        self.mask_data  = image.get_data().astype('uint')
        self.layerimage.onscreen_message("Mask stored", delay=1.0)
        
    def insert_colored_cb2(self):
        imageclass = self.mask_image.__class__
        if self.limage == None:
            self.new_cb(imageclass=imageclass)

        klass = self.get_imageclass(imageclass)
        cimage = klass(logger=self.logger)

        bitplane = self.w.bit_plane.get_text().strip()
        bitmask = 0x1 << int(bitplane)

        # Get the real data values array
        # TODO: cannot assume data is in bottom layer
        idx = self.limage.numLayers() - 1
        layer = self.limage.getLayer(idx)
        klass = self.get_imageclass(layer.image.__class__)
        values = layer.image.get_data()

        # Prepare data array for colored (unmasked) values
        # TODO: I think this can be made more efficient
        data = numpy.zeros(values.shape)
        data[numpy.nonzero(self.mask_data & bitmask)] = 1.0
        #data *= values
        data = data * values
        nimage = klass(data_np=data, logger=self.logger)

        # Prepare a color image
        color = self.w.clrbtn.get_color()
        cimage.insertLayer(0, nimage, alpha=color.red_float,
                           name="Red", compose=False)
        cimage.insertLayer(1, nimage, alpha=color.green_float,
                           name="Green", compose=False)
        cimage.insertLayer(2, nimage, alpha=color.blue_float,
                           name="Blue", compose=False)
        cimage.setComposeType('rgb')

        attrs = self._get_layer_attributes()
        self.limage.insertLayer(0, cimage, alpha=attrs.alpha,
                                name=attrs.name)
        self._gui_config_layers()

        self.layerimage.set_image(self.limage)
        name = self.limage.get('name')
        self.fv.add_image(name, self.limage)
        
    def decompose_cb(self):
        cimage = self.fitsimage.get_image()
        if self.limage == None:
            self.new_cb(imageclass=cimage.__class__)
        self.limage.rgb_decompose(cimage)
        self._gui_config_layers()

        self.layerimage.set_image(self.limage)
        name = self.limage.get('name')
        self.fv.add_image(name, self.limage)
        
    def std_greyscale_cb(self):
        # standard color to greyscale conversion RGB alphas:
        std_cvt = (0.292, 0.594, 0.114)
        self.limage.setAlphas(std_cvt)

        self.layerimage.set_image(self.limage)
        self.fitsimage.set_image(self.limage)
        
    ## def save_image_cb(self):
    ##     image = self.fitsimage.get_image()
    ##     path = image.get('path', None)
    ##     newname = self.w.save_as.get_text().strip()
    ##     if path != None:
    ##         path = os.join(path, newname)
    ##     else:
    ##         path = newname
    ##     image.save_file_as(path)
        
    def set_opacity_cb(self, w, idx):
        print "set opacity %d" % idx
        val = w.get_value()
        self.limage.setAlpha(idx, val)

        self.layerimage.redraw(whence=0)
        self.fitsimage.redraw(whence=0)
        
    def close(self):
        chname = self.fv.get_channelName(self.fitsimage)
        self.fv.stop_operation_channel(chname, str(self))
        return True
        
    def start(self):
        self.resume()

    def pause(self):
        pass
        
    def resume(self):
        self.redo()
        
    def stop(self):
        self.fv.showStatus("")
        
        
    def redo(self):
        pass
    
    def __str__(self):
        return 'layers'
    
#END
