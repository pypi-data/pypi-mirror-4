import logging
from random import random
from pyagents import Schedule
from arena import Arena
from asteroid import Asteroid, MAX_DENSITY
from collision_checker import CollisionChecker
from ship import Ship, Bullet

class Model(object):
    """
    Asteroids float in space
    """
    def __init__(self, width, height, n_asteroids, min_mass=800, max_mass=1000):
        self.min_mass = min_mass
        self.max_mass = max_mass
        self.schedule = Schedule('move', 'random', 'collision_check', 'collision_response')
        Asteroid.activate(self.schedule)
        Ship.activate(self.schedule)
        Bullet.activate(self.schedule)
        CollisionChecker.activate(self.schedule)
        self._tick = 0
        self.logger = logging.getLogger("Model")
        self.arena = Arena(width, height)
        for i in range(n_asteroids):
            self.add_asteroid()
        centre = [self.arena.width / 2, self.arena.height / 2]
        self.ship = Ship(centre, 1500, 150, 1500, self.arena)

    def add_asteroid(self):
        position = (random() * self.arena.width, random() * self.arena.height)
        mass = random() * (self.max_mass - self.min_mass) + self.min_mass
        velocity = [0, 0]
        density = MAX_DENSITY * 0.1 + random() * MAX_DENSITY * 0.9
        a = Asteroid(position, mass, velocity, density, self.arena)
        a.apply_force(10000 * (random() - 0.5), 10000 * (random() - 0.5))

    def tick(self):
        self._tick += 1
        self.schedule.execute(self.arena.agents())
