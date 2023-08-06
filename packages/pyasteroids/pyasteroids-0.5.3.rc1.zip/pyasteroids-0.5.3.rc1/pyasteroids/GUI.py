import logging
import pygtk
pygtk.require('2.0')
import gtk

import math
from model import Model

from gobject import timeout_add
import cairo

class gtkArena(gtk.DrawingArea):
    def __init__(self, arena):
        super(gtk.DrawingArea, self).__init__()
        self.arena = arena
        self.connect("expose_event", self.expose)

    def expose(self, widget, event):
        self.context = widget.window.cairo_create()
        self.context.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        self.context.clip()
        self.draw(self.context)

    def draw(self, cr):
        rect = self.get_allocation()
        cr.set_source_rgb(0, 0, 0)
        cr.rectangle(0, 0, rect.width, rect.height)
        cr.fill()
        cr.set_line_width(0.25)
        coefficients = float(rect.width)/self.arena.width, float(rect.height)/self.arena.height
        for thing in self.arena.stuff:
            thing.draw(cr, *coefficients)

class GUI(object):
    def __init__(self, width, height, n_asteroids, timeout=200):
        window = gtk.Window()
        window.resize(600, 600)
        window.set_position(gtk.WIN_POS_CENTER)
        window.set_title("Asteroids")
        window.connect("destroy", gtk.main_quit)
        self.lbl_status = gtk.Label()
        self.model = Model(width, height, n_asteroids)
        self.arena = gtkArena(self.model.arena)
        window.add(self.arena)
        window.show_all()
        timeout_add(timeout, self.tick)
        timeout_add(10000, self.level_up)
        window.connect('key_press_event', self.on_key_press_event)
        window.connect('key_release_event', self.on_key_up_event)

    def on_key_press_event(self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        func = getattr(self, 'keypress_' + keyname, None)
        if func:
            return func()
        print "Key %s (%d) was pressed" % (keyname, event.keyval)

    def on_key_up_event(self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        func = getattr(self, 'keyrelease_' + keyname, None)
        if func:
            return func()
        print "Key %s (%d) was released" % (keyname, event.keyval)        

    def keypress_Left(self):
        self.model.ship.steer_left()

    def keypress_Right(self):
        self.model.ship.steer_right()

    def keyrelease_Left(self):
        self.model.ship.straighten()

    def keyrelease_Right(self):
        self.model.ship.straighten()

    def keypress_Up(self):
        if self.model.ship.decelerating:
            self.model.ship.decelerate(False)
        else:
            self.model.ship.accelerate(True)

    def keypress_Down(self):
        if self.model.ship.accelerating:
            self.model.ship.accelerate(False)
        else:
            self.model.ship.decelerate(True)

    def keyrelease_Up(self):
        self.model.ship.stop()

    def keyrelease_Down(self):
        self.model.ship.stop()

    def keypress_space(self):
        self.model.ship.shoot()

    def keyrelease_space(self):
        pass

    def tick(self):
        self.model.tick()
        self.lbl_status.set_text(str(self.model._tick))
        self.arena.queue_draw()
        return self.model.ship.health >= 0

    def level_up(self):
        self.model.add_asteroid()
        return True
