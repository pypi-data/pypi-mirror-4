from pyagents import Agent, activate
from math import pi, cos, sin, sqrt, atan
from random import random, randint, choice
from mass import Mass, MAX_DENSITY

MIN_MASS = 50.0

class Asteroid(Mass, Agent):
    def __init__(self, position, mass, velocity, density, arena):
        Mass.__init__(self, position, mass, velocity, density, arena)
        Agent.__init__(self)
        self.shape = [random() for i in xrange(24)]
        self.direction = 0
        self.omega = (random() - 0.5) * (pi/50)

    @activate(level='move')
    def on_move(self):
        self.direction += self.omega
        self.direction %= (2 * pi)
        self.move()

    def explode(self, mv):
        total_mass = float(self.mass - min([MIN_MASS, self.mass]))  #remove some mass that is 'vapourised'
        total_mv = tuple([total_mass * av + mv_i for av, mv_i in zip(self.velocity, mv)])        
        n_pieces = randint(2, 5)  #number of bits to break into
        mean_mv = tuple([mv_i / n_pieces for mv_i in total_mv]) #mean mass of bits
        mean_mass = total_mass / n_pieces #mean mass of bits
        position = self.position()
        new_pieces = [{
            'mv': tuple([mean_mv_i * (random() - 0.5) for mean_mv_i in mean_mv]), 
            'mass': mean_mass * 0.2 + random() * mean_mass * 0.8, 
        } for i in range(n_pieces - 1)]

        new_pieces = [p for p in new_pieces if p['mass'] > 0]

        remaining_mass = total_mass
        remaining_mv = list(total_mv)
        for piece in new_pieces:
            remaining_mass -= piece['mass']
            remaining_mv[0] -= piece['mv'][0]
            remaining_mv[1] -= piece['mv'][1]
            piece['velocity'] = (piece['mv'][0] / piece['mass'], piece['mv'][1] / piece['mass'])

        if remaining_mass > 0:
            new_pieces.append({
                'mv': remaining_mv,
                'mass': remaining_mass,
                'velocity': (remaining_mv[0]/remaining_mass, remaining_mv[1]/remaining_mass)
            })

        for piece in new_pieces:
            child = Asteroid(position, piece['mass'], piece['velocity'], self.density, self.arena)

        self.arena.remove(self)

    def draw(self, cr, *coefficients):
        cr.set_line_width(1)
        cr.set_source_rgba(0, 0.5, 0, 1)            
        x, y = self.position()
        area = self.mass * self.density
        radius = self.radius()
        one_slice = 2*pi/len(self.shape)
        for i, shape in enumerate(self.shape):
            angle = (i * one_slice + self.direction) % (2 * pi)
            distance = radius + radius * 0.5 * (shape - 0.5)
            cr.line_to(coefficients[0] * (x + sin(angle) * distance), coefficients[1] * (y + cos(angle) * distance))
        cr.close_path()
        cr.stroke_preserve()
        cr.set_source_rgba(0, 0.5, 0, self.density/(MAX_DENSITY*2))
        cr.fill()
