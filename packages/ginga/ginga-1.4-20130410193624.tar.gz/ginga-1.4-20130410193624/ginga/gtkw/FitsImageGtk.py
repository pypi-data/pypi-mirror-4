#
# FitsImageGtk.py -- classes for the display of FITS files in Gtk widgets
# 
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c)  Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.

import sys, re
import gobject
import gtk
import cairo
import numpy
import threading
import math

import warnings
warnings.filterwarnings("ignore")

from ginga import FitsImage
from ginga import Mixins

class FitsImageGtkError(FitsImage.FitsImageError):
    pass

class FitsImageGtk(FitsImage.FitsImageBase):

    def __init__(self, logger=None, settings=None):
        #super(FitsImageGtk, self).__init__(logger=logger)
        FitsImage.FitsImageBase.__init__(self, logger=logger,
                                         settings=settings)

        imgwin = gtk.DrawingArea()
        imgwin.connect("expose_event", self.expose_event)
        # GTK3?
        #imgwin.connect("draw_event", self.draw_event)
        imgwin.connect("configure_event", self.configure_event)
        imgwin.set_events(gtk.gdk.EXPOSURE_MASK)
        self.imgwin = imgwin
        self.surface = None
        self.imgwin.show_all()

        self.message = None
        self.msgtask = None
        self.img_bg = None
        self.img_fg = None
        #self.set_bg(0.5, 0.5, 0.5, redraw=False)
        self.set_bg(0.0, 0.0, 0.0, redraw=False)
        self.set_fg(1.0, 1.0, 1.0, redraw=False)
        
        # cursors
        self.cursor = {}

        # optimization of redrawing
        self.defer_redraw = True
        self.defer_lagtime = 25
        self._defer_whence = 0
        self._defer_lock = threading.RLock()
        self._defer_flag = False

        # # For rotation of canvas
        # self.ctr_x = 0.0
        # self.ctr_y = 0.0
        self.cr = None

        self.t_.setDefaults(show_pan_position=False)
        
    def get_widget(self):
        return self.imgwin

    def _render_offscreen(self, surface, data, dst_x, dst_y,
                          width, height):
        # NOTE [A]
        daht, dawd, depth = data.shape
        self.logger.debug("data shape is %dx%dx%d" % (dawd, daht, depth))

        cr = cairo.Context(surface)
        self.cr = cr

        # fill surface with background color
        imgwin_wd, imgwin_ht = self.get_window_size()
        cr.rectangle(0, 0, imgwin_wd, imgwin_ht)
        r, g, b = self.img_bg
        cr.set_source_rgb(r, g, b)
        cr.fill()

        arr8 = data.astype(numpy.uint8).flatten()
        stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_RGB24,
                                                            width)

        img_surface = cairo.ImageSurface.create_for_data(arr8,
                                                         cairo.FORMAT_RGB24,
                                                         dawd, daht, stride)

        # Rotate to desired rotation
        ## self.ctr_x, self.ctr_y = imgwin_wd / 2.0, imgwin_ht / 2.0
        ## cr.translate(self.ctr_x, self.ctr_y)
        ## cr.rotate(math.radians(self.rotation))

        ## offx, offy = dst_x - self.ctr_x, dst_y - self.ctr_y
        ## cr.set_source_surface(img_surface, offx, offy)
        cr.set_source_surface(img_surface, dst_x, dst_y)
        cr.set_operator(cairo.OPERATOR_SOURCE)

        ## cr.rectangle(offx, offy, dawd, daht)
        cr.rectangle(dst_x, dst_y, dawd, daht)
        cr.fill()

        # Draw a cross in the center of the window in debug mode
        if self.t_['show_pan_position']:
            cr.set_source_rgb(1.0, 0.0, 0.0)
            cr.set_line_width(1)
            ctr_x, ctr_y = self.get_center()
            cr.move_to(ctr_x - 10, ctr_y)
            cr.line_to(ctr_x + 10, ctr_y)
            cr.move_to(ctr_x, ctr_y - 10)
            cr.line_to(ctr_x, ctr_y + 10)
            cr.close_path()
            cr.stroke_preserve()
        
        # render self.message
        if self.message:
            ## cr.rotate(math.radians(-self.rotation))
            ## cr.translate(-self.ctr_x, -self.ctr_y)
            self.draw_message(cr, imgwin_wd, imgwin_ht,
                              self.message)

    def draw_message(self, cr, width, height, message):
        r, g, b = self.img_fg
        #cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.set_source_rgb(r, g, b)
        cr.select_font_face('Sans Serif')
        cr.set_font_size(24.0)
        a, b, wd, ht, i, j = cr.text_extents(message)
        y = ((height // 3) * 2) - (ht // 2)
        x = (width // 2) - (wd // 2)
        cr.move_to(x, y)
        cr.show_text(self.message)

    def get_offscreen_context(self):
        if self.surface == None:
            raise FitsImageGtkError("No offscreen surface defined")
        cr = cairo.Context(self.surface)
        return cr

    def render_image(self, rgbobj, dst_x, dst_y):
        """Render the image represented by (rgbobj) at dst_x, dst_y
        in the pixel space.
        """
        self.logger.debug("redraw surface")
        if self.surface == None:
            return

        # Prepare array for Cairo rendering
        if sys.byteorder == 'little':
            arr = numpy.dstack((rgbobj.b, rgbobj.g, rgbobj.r, rgbobj.a))
        else:
            arr = numpy.dstack((rgbobj.a, rgbobj.r, rgbobj.g, rgbobj.b))

        (height, width) = rgbobj.r.shape
        return self._render_offscreen(self.surface, arr, dst_x, dst_y,
                                      width, height)

    def configure(self, width, height):
        arr8 = numpy.zeros(height*width*4).astype(numpy.uint8)
        stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_RGB24,
                                                            width)

        surface = cairo.ImageSurface.create_for_data(arr8,
                                                     cairo.FORMAT_RGB24,
                                                     width, height, stride)
        self.surface = surface
        self.set_window_size(width, height, redraw=True)
        
    def get_image_as_pixbuf(self):
        rgbobj = self.get_rgb_object()
        arr = numpy.dstack((rgbobj.r, rgbobj.g, rgbobj.b))

        try:
            pixbuf = gtk.gdk.pixbuf_new_from_array(arr, gtk.gdk.COLORSPACE_RGB,
                                                   8)
        except Exception, e:
            #print "ERROR MAKING PIXBUF", str(e)
            # pygtk might have been compiled without numpy support
            daht, dawd, depth = arr.shape
            rgb_buf = self._get_rgbbuf(arr)
            pixbuf = gtk.gdk.pixbuf_new_from_data(rgb_buf, gtk.gdk.COLORSPACE_RGB,
                                                  False, 8, dawd, daht, dawd*3)
            
        return pixbuf

    def get_image_as_widget(self):
        pixbuf = self.get_image_as_pixbuf()
        image = gtk.Image()
        image.set_from_pixbuf(pixbuf)
        image.show()
        return image

    def save_image_as_file(self, filepath, format='png', quality=90):
        pixbuf = self.get_image_as_pixbuf()
        options = {}
        if format == 'jpeg':
            options['quality'] = str(quality)
        pixbuf.save(filepath, format, options)
    
    def redraw(self, whence=0):
        if not self.defer_redraw:
            super(FitsImageGtk, self).redraw(whence=whence)
            return
        
        # This adds a redraw optimization to the base class redraw()
        # method. 
        with self._defer_lock:
            self._defer_whence = min(self._defer_whence, whence)
            defer_flag = self._defer_flag
            # indicate that a redraw is necessary
            self._defer_flag = True
            if not defer_flag:
                # if no redraw was scheduled, then schedule one in
                # defer_lagtime 
                self._defer_task = gobject.timeout_add(self.defer_lagtime,
                                                       self._redraw)
                
    def _redraw(self):
        # This is the optomized redraw method
        with self._defer_lock:
            # pick up the lowest necessary level of redrawing
            whence = self._defer_whence
            self._defer_whence = 3
            flag = self._defer_flag
            self._defer_flag = False

        if flag:
            # If a redraw was scheduled, do it now
            super(FitsImageGtk, self).redraw(whence=whence)
        
    def update_image(self):
        if not self.surface:
            return
            
        win = self.imgwin.window
        if win != None and self.surface != None:
            #imgwin_wd, imgwin_ht = self.get_window_size()
            win.invalidate_rect(None, True)
            # Process expose events right away so window is responsive
            # to scrolling
            win.process_updates(True)


    def draw_event(self, widget, cr):
        """GTK 3 event handler replacing expose_event().
        """
        self.logger.debug("updating window from surface")
        # redraw the screen from backing surface
        cr.set_source_surface(self.surface, 0, 0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        return False
        
    def expose_event(self, widget, event):
        """When an area of the window is exposed, we just copy out of the
        server-side, off-screen surface to that area.
        """
        x , y, width, height = event.area
        self.logger.debug("surface is %s" % self.surface)
        if self.surface != None:
            cr = widget.window.cairo_create()

            # set clip area for exposed region
            cr.rectangle(x, y, width, height)
            cr.clip()

            ## # Rotate if desired
            ## self.ctr_x, self.ctr_y = width / 2.0, height / 2.0
            ## cr.translate(self.ctr_x, self.ctr_y)
            ## cr.rotate(math.radians(self.rotation))
            
            # Paint from off-screen surface
            ## imgwin_wd, imgwin_ht = self.get_window_size()
            ## off_x, off_y = imgwin_wd, imgwin_ht
            ## cr.translate(off_x, off_y)
            cr.set_source_surface(self.surface, 0, 0)
            #cr.set_source_surface(self.surface, -off_x, -off_y)
            ## cr.set_source_surface(self.surface, -self.ctr_x, -self.ctr_y)
            cr.set_operator(cairo.OPERATOR_SOURCE)
            cr.paint()

        return False
        
    def configure_event(self, widget, event):
        self.surface = None
        x, y, width, height = widget.get_allocation()
        self.logger.debug("allocation is %d,%d %dx%d" % (
            x, y, width, height))
        #width, height = width*2, height*2
        self.configure(width, height)
        return True

    def set_cursor(self, cursor):
        win = self.imgwin.window
        if win != None:
            win.set_cursor(cursor.cur)
        
    def define_cursor(self, ctype, cursor):
        self.cursor[ctype] = cursor
        
    def get_cursor(self, ctype):
        return self.cursor[ctype]
        
    def switch_cursor(self, ctype):
        self.set_cursor(self.cursor[ctype])
        
    def _get_rgbbuf(self, data):
        buf = data.tostring(order='C')
        return buf

    ## def _get_color(self, r, g, b):
    ##     n = 65535.0
    ##     clr = gtk.gdk.Color(int(r*n), int(g*n), int(b*n))
    ##     return clr
        
    def set_bg(self, r, g, b, redraw=True):
        self.img_bg = (r, g, b)
        if redraw:
            self.redraw(whence=3)
        
    def set_fg(self, r, g, b, redraw=True):
        self.img_fg = (r, g, b)
        if redraw:
            self.redraw(whence=3)
        
    def onscreen_message(self, text, delay=None, redraw=True):
        if self.msgtask:
            try:
                gobject.source_remove(self.msgtask)
            except:
                pass
        self.message = text
        if redraw:
            self.redraw(whence=3)
        if delay:
            ms = int(delay * 1000.0)
            self.msgtask = gobject.timeout_add(ms, self.onscreen_message, None)

    def show_pan_mark(self, tf, redraw=True):
        self.t_.set(show_pan_position=tf)
        if redraw:
            self.redraw(whence=3)
        
    def pix2canvas(self, x, y):
        x, y = self.cr.device_to_user(x, y)
        return (x, y)
        
    def canvas2pix(self, x, y):
        x, y = self.cr.user_to_device(x, y)
        return (x, y)
        
        
class FitsImageEvent(FitsImageGtk):

    def __init__(self, logger=None, settings=None):
        #super(FitsImageEvent, self).__init__(logger=logger)
        FitsImageGtk.__init__(self, logger=logger, settings=settings)

        imgwin = self.imgwin
        imgwin.set_flags(gtk.CAN_FOCUS)
        imgwin.connect("map_event", self.map_event)
        imgwin.connect("focus_in_event", self.focus_event, True)
        imgwin.connect("focus_out_event", self.focus_event, False)
        imgwin.connect("enter_notify_event", self.enter_notify_event)
        imgwin.connect("leave_notify_event", self.leave_notify_event)
        imgwin.connect("motion_notify_event", self.motion_notify_event)
        imgwin.connect("button_press_event", self.button_press_event)
        imgwin.connect("button_release_event", self.button_release_event)
        imgwin.connect("key_press_event", self.key_press_event)
        imgwin.connect("key_release_event", self.key_release_event)
        imgwin.connect("scroll_event", self.scroll_event)
        mask = imgwin.get_events()
        imgwin.set_events(mask
                         | gtk.gdk.ENTER_NOTIFY_MASK
                         | gtk.gdk.LEAVE_NOTIFY_MASK
                         | gtk.gdk.FOCUS_CHANGE_MASK
                         | gtk.gdk.STRUCTURE_MASK
                         | gtk.gdk.BUTTON_PRESS_MASK
                         | gtk.gdk.BUTTON_RELEASE_MASK
                         | gtk.gdk.KEY_PRESS_MASK
                         | gtk.gdk.KEY_RELEASE_MASK
                         | gtk.gdk.POINTER_MOTION_MASK
                         | gtk.gdk.POINTER_MOTION_HINT_MASK
                         | gtk.gdk.SCROLL_MASK)

        # Set up widget as a drag and drop destination
        self.TARGET_TYPE_TEXT = 80
        toImage = [ ( "text/plain", 0, self.TARGET_TYPE_TEXT ) ]
        imgwin.connect("drag_data_received", self.drop_event)
        imgwin.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                             toImage, gtk.gdk.ACTION_COPY)
        
        # last known window mouse position
        self.last_win_x = 0
        self.last_win_y = 0
        # last known data mouse position
        self.last_data_x = 0
        self.last_data_y = 0
        # Does widget accept focus when mouse enters window
        self.follow_focus = True

        # User-defined keyboard mouse mask
        self.kbdmouse_mask = 0

        # @$%&^(_)*&^ gnome!!
        self._keytbl = {
            'shift_l': 'shift_l',
            'shift_r': 'shift_r',
            'control_l': 'control_l',
            'control_r': 'control_r',
            'asciitilde': '~',
            'grave': 'backquote',
            'exclam': '!',
            'at': '@',
            'numbersign': '#',
            'percent': '%',
            'asciicircum': '^',
            'ampersand': '&',
            'asterisk': '*',
            'dollar': '$',
            'parenleft': '(',
            'parenright': ')',
            'underscore': '_',
            'minus': '-',
            'plus': '+',
            'equal': '=',
            'braceleft': '{',
            'braceright': '}',
            'bracketleft': '[',
            'bracketright': ']',
            'bar': '|',
            'colon': ':',
            'semicolon': ';',
            'quotedbl': 'doublequote',
            'apostrophe': 'singlequote',
            'backslash': 'backslash',
            'less': '<',
            'greater': '>',
            'comma': ',',
            'period': '.',
            'question': '?',
            'slash': '/',
            'space': 'space',
            'escape': 'escape',
            'return': 'return',
            'tab': 'tab',
            'f1': 'f1',
            'f2': 'f2',
            'f3': 'f3',
            'f4': 'f4',
            'f5': 'f5',
            'f6': 'f6',
            'f7': 'f7',
            'f8': 'f8',
            'f9': 'f9',
            'f10': 'f10',
            'f11': 'f11',
            'f12': 'f12',
            }
        
        # Define cursors for pick and pan
        hand = openHandCursor()
        self.define_cursor('pan', hand)
        cross = thinCrossCursor('aquamarine')
        self.define_cursor('pick', cross)

        for name in ('motion', 'button-press', 'button-release',
                     'key-press', 'key-release', 'drag-drop', 
                     'scroll', 'map', 'focus', 'enter', 'leave',
                     ):
            self.enable_callback(name)

    def transkey(self, keyname):
        try:
            return self._keytbl[keyname.lower()]

        except KeyError:
            return keyname

    def set_kbdmouse_mask(self, mask):
        self.kbdmouse_mask |= mask
        
    def reset_kbdmouse_mask(self, mask):
        self.kbdmouse_mask &= ~mask
        
    def get_kbdmouse_mask(self):
        return self.kbdmouse_mask
        
    def clear_kbdmouse_mask(self):
        self.kbdmouse_mask = 0
        
    def set_followfocus(self, tf):
        self.followfocus = tf
        
    def map_event(self, widget, event):
        super(FitsImageZoom, self).configure_event(widget, event)
        return self.make_callback('map')
            
    def focus_event(self, widget, event, hasFocus):
        return self.make_callback('focus', hasFocus)
            
    def enter_notify_event(self, widget, event):
        if self.follow_focus:
            widget.grab_focus()
        return self.make_callback('enter')
    
    def leave_notify_event(self, widget, event):
        self.logger.debug("leaving widget...")
        return self.make_callback('leave')
    
    def key_press_event(self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        keyname = self.transkey(keyname)
        self.logger.debug("key press event, key=%s" % (keyname))
        return self.make_callback('key-press', keyname)

    def key_release_event(self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        keyname = self.transkey(keyname)
        self.logger.debug("key release event, key=%s" % (keyname))
        return self.make_callback('key-release', keyname)

    def button_press_event(self, widget, event):
        # event.button, event.x, event.y
        x = event.x; y = event.y
        button = self.kbdmouse_mask
        if event.button != 0:
            button |= 0x1 << (event.button - 1)
        self.logger.debug("button event at %dx%d, button=%x" % (x, y, button))

        data_x, data_y = self.get_data_xy(x, y)
        return self.make_callback('button-press', button, data_x, data_y)

    def button_release_event(self, widget, event):
        # event.button, event.x, event.y
        x = event.x; y = event.y
        button = self.kbdmouse_mask
        if event.button != 0:
            button |= 0x1 << (event.button - 1)
        self.logger.debug("button release at %dx%d button=%x" % (x, y, button))
            
        data_x, data_y = self.get_data_xy(x, y)
        return self.make_callback('button-release', button, data_x, data_y)

    def get_last_data_xy(self):
        return (self.last_data_x, self.last_data_y)

    def motion_notify_event(self, widget, event):
        button = self.kbdmouse_mask
        if event.is_hint:
            x, y, state = event.window.get_pointer()
        else:
            x, y, state = event.x, event.y, event.state
        self.last_win_x, self.last_win_y = x, y
        
        if state & gtk.gdk.BUTTON1_MASK:
            button |= 0x1
        elif state & gtk.gdk.BUTTON2_MASK:
            button |= 0x2
        elif state & gtk.gdk.BUTTON3_MASK:
            button |= 0x4
        # self.logger.debug("motion event at %dx%d, button=%x" % (x, y, button))

        data_x, data_y = self.get_data_xy(x, y)
        self.last_data_x, self.last_data_y = data_x, data_y

        return self.make_callback('motion', button, data_x, data_y)

    def scroll_event(self, widget, event):
        # event.button, event.x, event.y
        x = event.x; y = event.y
        direction = None
        if event.direction == gtk.gdk.SCROLL_UP:
            direction = 'up'
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            direction = 'down'
        elif event.direction == gtk.gdk.SCROLL_LEFT:
            direction = 'left'
        elif event.direction == gtk.gdk.SCROLL_RIGHT:
            direction = 'right'
        self.logger.debug("scroll at %dx%d event=%s" % (x, y, str(event)))

        # TODO: how about amount of scroll?
        return self.make_callback('scroll', direction)

    def drop_event(self, widget, context, x, y, selection, targetType,
                   time):
        if targetType != self.TARGET_TYPE_TEXT:
            return False
        paths = selection.data.split('\n')
        self.logger.debug("dropped filename(s): %s" % (str(paths)))
        return self.make_callback('drag-drop', paths)


class FitsImageZoom(Mixins.UIMixin, FitsImageEvent,
                    Mixins.FitsImageZoomMixin):

    def __init__(self, logger=None, settings=None):
        FitsImageEvent.__init__(self, logger=logger, settings=settings)
        Mixins.UIMixin.__init__(self)
        Mixins.FitsImageZoomMixin.__init__(self)

        
class thinCrossCursor(object):
    def __init__(self, color='red'):
        self.color = color
        height = 16
        width  = 16
        arr8 = numpy.zeros(height*width*4).astype(numpy.uint8)
        stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32,
                                                            width)

        surface = cairo.ImageSurface.create_for_data(arr8,
                                                     cairo.FORMAT_ARGB32,
                                                     width, height, stride)
        cr = cairo.Context(surface)
        # Fill square with full transparency
        cr.rectangle(0, 0, width, height)
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        cr.fill()

        # Set cursor color
        color = gtk.gdk.color_parse(color)
        rgb_s = color.to_string()
        match = re.match(r'^#(\w{4})(\w{4})(\w{4})$', rgb_s)
        r, g, b = map(lambda s: float(int(s, 16))/65535.0, match.groups())

        # Something I don't get about Cairo--why do I have to specify
        # BGRA for a method called set_source_RGBA &%^%*($ !!! 
        #cr.set_source_rgba(r, g, b, 1.0)
        cr.set_source_rgba(b, g, r, 1.0)
        cr.set_line_width(1)

        # NOTE: ".5" coordinates are to get sharp, single pixel lines
        # due to the way Cairo renders--more ^&$%(*@ !!
        # See http://cairographics.org/FAQ/#sharp_lines
        cr.move_to(0, 6.5)
        cr.line_to(5, 6.5)
        cr.move_to(0, 8.5)
        cr.line_to(5, 8.5)
        
        cr.move_to(10, 6.5)
        cr.line_to(15, 6.5)
        cr.move_to(10, 8.5)
        cr.line_to(15, 8.5)
        
        cr.move_to(6.5, 0)
        cr.line_to(6.5, 5)
        cr.move_to(8.5, 0)
        cr.line_to(8.5, 5)
        
        cr.move_to(6.5, 10)
        cr.line_to(6.5, 15)
        cr.move_to(8.5, 10)
        cr.line_to(8.5, 15)

        cr.stroke()

        data = arr8.reshape((height, width, 4))
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_array(data,
                                                   gtk.gdk.COLORSPACE_RGB, 8)
        except Exception, e:
            #print "ERROR MAKING PIXBUF", str(e)
            # pygtk might have been compiled without numpy support
            daht, dawd, depth = data.shape
            rgb_buf = data.tostring(order='C')
            pixbuf = gtk.gdk.pixbuf_new_from_data(rgb_buf, gtk.gdk.COLORSPACE_RGB,
                                                  False, 8, dawd, daht, dawd*3)
        # Is this always going to be the correct display?  Does it matter?
        display = gtk.gdk.display_get_default()
        self.cur = gtk.gdk.Cursor(display, pixbuf, 8, 8)
        

class openHandCursor(object):
    def __init__(self, color='red'):

        self.xpm_data = [
            "16 16 3 1 ",
            "  c black",
            ". c gray100",
            "X c None",
            "XXXXXXX  XXXXXXX",
            "XXX  X ..   XXXX",
            "XX ..  .. .. XXX",
            "XX ..  .. .. X X",
            "XXX .. .. ..  . ",
            "XXX .. .. .. .. ",
            "X  . ....... .. ",
            " ..  .......... ",
            " ... ......... X",
            "X ............ X",
            "XX ........... X",
            "XX .......... XX",
            "XXX ......... XX",
            "XXXX ....... XXX",
            "XXXXX ...... XXX",
            "XXXXXXXXXXXXXXXX"
            ]
        pixbuf = gtk.gdk.pixbuf_new_from_xpm_data(self.xpm_data)

        # Is this always going to be the correct display?  Does it matter?
        display = gtk.gdk.display_get_default()
        self.cur = gtk.gdk.Cursor(display, pixbuf, 8, 8)

#END
