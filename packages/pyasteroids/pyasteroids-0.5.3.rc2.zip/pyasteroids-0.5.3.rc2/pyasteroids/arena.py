from math import sqrt
from collision_checker import CollisionChecker

class ArenaError(Exception): pass

class Arena(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.collision_checker = CollisionChecker(self)
        self.stuff = {}

    def agents(self):
        result = list(self.stuff.keys())
        result.append(self.collision_checker)
        return result

    def place(self, something, x, y):
        """place something on the arena"""
        x %= self.width
        y %= self.height
        if x > self.width:
            raise ArenaError("%s is too high for x (0 - %s)" % (x, self.width))
        if y > self.height:
            raise ArenaError("%s is too high for y (0 - %s)" % (y, self.height))
        self.stuff[something] = {'coordinates': (x, y)}

    def remove(self, something):
        try:
            del self.stuff[something]
            self.collision_checker.forget(something)
        except KeyError:
            pass

    def where_is(self, something):
        return self.stuff[something]['coordinates']

    def neighbours_of(self, centre, distance, _type):
        x, y = self.stuff[centre]['coordinates']
        distance_2 = distance**2
        for thing, data in self.stuff.iteritems():
            if not isinstance(thing, _type):
                continue
            dx = x - data['coordinates'][0]
            dy = y - data['coordinates'][1]
            if dx**2 + dy**2 > distance_2:
                continue
            yield thing

    def move(self, thing, dx, dy):
        x, y = self.stuff[thing]['coordinates']
        x, y = x + dx, y + dy
        x = x % self.width
        y = y % self.height
        self.stuff[thing]['coordinates'] = (x, y)

    def __repr__(self):
        return "Arena"
