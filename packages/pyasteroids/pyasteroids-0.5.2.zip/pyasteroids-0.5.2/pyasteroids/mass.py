from math import pi, cos, sin, sqrt, atan
from random import random, randint, choice

MIN_RADIUS = 20
MAX_DENSITY = 0.05

class Point(object):
    def __init__(self, position, arena):
        self.arena = arena
        self.arena.place(self, *position)

    def position(self):
        return self.arena.where_is(self)

    def difference(self, other):
        my_pos = self.position()
        your_pos = other.position()
        return (my_pos[0] - your_pos[0], my_pos[1] - your_pos[1])

    def distance(self, other):
        dx, dy = self.difference(other)
        return sqrt(dx**2 + dy**2)

    def angle(self, other):
        dx, dy = self.difference(other)
        return atan(dy/dx)

    def draw(self, cr, *coefficients):
        cr.set_source_rgb(1, 1, 1)
        x, y = self.position()
        radius = 1
        cr.arc(coefficients[0]*x, coefficients[1]*y, radius * min(coefficients), 0, 2 * pi)
        cr.fill()


class Mass(Point):
    def __init__(self, position, mass, velocity, density, arena):
        """position (x, y) in m, mass in kg, velocity (x, y) in m/tick"""
        self.mass = float(mass)
        self.velocity = velocity
        self.density = density
        super(Mass, self).__init__(position, arena)

    def radius(self):
        return MIN_RADIUS + sqrt((self.mass/self.density)/pi)

    def momentum(self):
        return [v * self.mass for v in self.velocity]

    def apply_force(self, x, y):
        """forces in Newtons"""
        self.velocity = [v + f/self.mass for f, v in zip([x, y], self.velocity)]

#    @activate(level='move')
    def move(self):
        self.arena.move(self, *self.velocity)

    def energy(self):
        return 0.5 * self.mass * (self.velocity[0]**2 + self.velocity[1]**2)

#    @activate(level='collision_response')
#    def on_collision_response(self):
#        """
#        If masses collide they pass energy to each other
#        depending on the direction of travel
#        velocity in the x-direction
#        """
#        warnings = [item for item, message in self.arena.collision_checker.collisions[self] if message == 'warning']
#        if warnings:
#            other = choice(warnings)
#            force = tuple([v * self.mass * 0.5 for v in self.velocity])#deceleration to zero * mass
#            self.apply_force(*tuple(-1*f for f in force))
#            other.apply_force(*force)            
#
#        collisions = [item for item, message in self.arena.collision_checker.collisions[self] if message == 'collision']
#        if collisions:
#            other = choice(collisions)
#            force = tuple([v * self.mass for v in self.velocity])#deceleration to zero * mass
#            self.apply_force(*tuple(-1*f for f in force))
#            other.apply_force(*force)

    def draw(self, cr, *coefficients):
        cr.set_source_rgba(1, 1, 1, self.density/MAX_DENSITY)
        x, y = self.position()
        cr.arc(coefficients[0]*x, coefficients[1]*y, self.radius() * min(coefficients), 0, 2 * pi)
        cr.fill()

