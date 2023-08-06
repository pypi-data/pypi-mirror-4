from pyagents import Agent, activate
from mass import Mass, MAX_DENSITY
from math import pi, cos, sin#, sqrt, atan

BULLET_AGE = 25

class Ship(Mass, Agent):
    def __init__(self, position, mass, steer_power, thrust_power, arena):
        Mass.__init__(self, position, mass, [0, 0], 1, arena)
        Agent.__init__(self)
        self.direction = 0
        self.omega = 0
        self.decelerating, self.accelerating = False, False
        self.steer_power = steer_power
        self.thrust_power = thrust_power
        self.bullet_velocity = 50
        self.bullet_mass = 10
        self.health = 1
        
    def steer(self, force):
        self.omega = force/self.mass

    def steer_left(self):
        self.steer(self.steer_power)

    def steer_right(self):
        self.steer(-self.steer_power)

    def straighten(self):
        self.omega *= 0.1

    def stop(self):
        self.accelerating = False
        self.decelerating = False
        self.velocity = tuple([v * 0.9 for v in self.velocity])

    def accelerate(self, on):
        self.accelerating = on

    def decelerate(self, on):
        self.decelerating = on

    def thrust(self, force):
        self.apply_force(sin(self.direction) * force, cos(self.direction) * force)

    def shoot(self):
        bullet = Bullet(self)

    @activate(level='move')
    def on_move(self):
        if self.accelerating:
            self.apply_force(sin(self.direction) * self.thrust_power, cos(self.direction) * self.thrust_power)
        if self.decelerating:
            self.apply_force(sin(self.direction) * -self.thrust_power, cos(self.direction) * -self.thrust_power)
        self.direction += self.omega
        self.direction %= (2 * pi)
        self.move()

    def draw(self, cr, *coefficients):
        cr.set_line_width(2)
        cr.set_source_rgba(1-self.health, self.health, self.health, 1)
        x, y = self.position()
        radius = self.radius()
        my_angle = 2.5
        points = [
            (self.direction, radius),
            (self.direction + my_angle, radius),
            (self.direction + pi, radius/2),
            (self.direction - my_angle, radius),
            (self.direction, radius)
        ]
        for angle, distance in points:
            cr.line_to(coefficients[0] * (x + sin(angle) * distance), coefficients[1] * (y + cos(angle) * distance))
        cr.stroke_preserve()
        cr.set_source_rgba(1-self.health, self.health, self.health, self.health)
        cr.fill()


class Bullet(Mass, Agent):
    def __init__(self, parent):
        position = list(parent.position())
        velocity = list(parent.velocity)
        position[0] += sin(parent.direction) * parent.radius() * 3
        position[1] += cos(parent.direction) * parent.radius() * 3
        velocity[0] += sin(parent.direction) * parent.bullet_velocity
        velocity[1] += cos(parent.direction) * parent.bullet_velocity
        Mass.__init__(self, tuple(position), parent.bullet_mass, tuple(velocity), MAX_DENSITY, parent.arena)
        Agent.__init__(self)
        self.age = 0

    @activate(level='move')
    def on_move(self):
        self.move()
        self.age += 1
        if self.age > BULLET_AGE:
            self.arena.remove(self)

    def draw(self, cr, *c):
        cr.set_source_rgba(1, 0, 0, 0.5)
        x, y = self.position()
        cr.arc(c[0] * x, c[1] * y, self.radius()/3 * min(c), 0, 2 * pi)
        cr.arc(c[0] * x, c[1] * y, self.radius()/3 * min(c), 0, 2 * pi)
        cr.fill()

