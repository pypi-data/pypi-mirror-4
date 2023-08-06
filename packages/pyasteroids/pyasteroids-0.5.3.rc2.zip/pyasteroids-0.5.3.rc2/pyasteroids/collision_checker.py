from pyagents import Agent, activate
from ship import Ship, Bullet
from asteroid import Asteroid, MIN_MASS
from random import random, randint, choice
from math import pi, cos, sin, sqrt#, atan

class CollisionChecker(Agent):
    def __init__(self, arena):
        self.arena = arena
        self.collisions = {}
        self.pairs = {}
        Agent.__init__(self)

    def forget(self, something):
        for pair in self.pairs.keys():
            if something in pair:
                del self.pairs[pair]

    @activate(level='collision_check')
    def on_collision_check(self):
        self.remembered = self.pairs
        self.pairs = {}
        self.collisions = {}
        for thing, c1 in self.arena.stuff.iteritems():
            x1, y1 = c1['coordinates']
            self.collisions[thing] = []
            for another_thing, c2 in self.arena.stuff.iteritems():
                if thing == another_thing:
                    continue
                if self.pairs.has_key((another_thing, thing)):
                    continue
                x2, y2 = c2['coordinates']
                dx = x1 - x2#abs(x1 - x2) % (self.arena.width/2)
                dy = y1 - y2#abs(y1 - y2) % (self.arena.height/2)
                distance = sqrt(dx**2 + dy**2)
                threshold = thing.radius() + another_thing.radius()
                if distance > threshold * 5                                                                         :
                    continue
                if distance > threshold * 1.2:
                    self.collisions[thing].append((another_thing, 'OK'))
                elif distance > threshold:
                    self.collisions[thing].append((another_thing, 'warning'))
                else:
                    self.collisions[thing].append((another_thing, 'collision'))
                    self.pairs[(thing, another_thing)] = 1
#                    self.calculate(thing, another_thing)

    @activate(level='collision_response')
    def collide(self):
    #TODO this loop is removing items from self.pairs but the call to keys only happens once
        for item1, item2 in self.pairs.keys():
            if self.remembered.has_key((item1, item2)):
                continue

            if not self.pairs.has_key((item1, item2)):
                continue

            if (isinstance(item1, Bullet) or isinstance(item2, Bullet)):
                if isinstance(item1, Asteroid):
                    self.destructive(item2, item1)
                if isinstance(item2, Asteroid):
                    self.destructive(item1, item2)
            elif isinstance(item1, Ship):
                self.damage(item2, item1)
            elif isinstance(item2, Ship):
                self.damage(item1, item2)
            else:
                self.elastic(item1, item2)
                
    def elastic(self, item1, item2):
        x1, y1 = item1.position()
        x2, y2 = item2.position()
        m1, m2 = item1.mass, item2.mass
        normal_vector = (x2 - x1, y2 - y1)
        magnitude = sqrt((x2 - x1)**2 + (y2 - y1)**2)
        unit_normal = tuple([nv/magnitude for nv in normal_vector])
        unit_tangent = (-unit_normal[1], unit_normal[0])
        v1 = item1.velocity
        v2 = item2.velocity
        v1_normal = dot(v1, unit_normal)
        v2_normal = dot(v2, unit_normal)
        v1_tangent = dot(v1, unit_tangent)
        v2_tangent = dot(v2, unit_tangent)
        new_v1_normal = (v1_normal * (m1 - m2) + 2 * m2 * v2_normal) / (m1 + m2)
        new_v2_normal = (v2_normal * (m2 - m1) + 2 * m1 * v1_normal) / (m1 + m2)
        new_v1_normal_vector = tuple([new_v1_normal * v for v in unit_normal])
        new_v2_normal_vector = tuple([new_v2_normal * v for v in unit_normal])
        new_v1_tangent_vector = tuple([v1_tangent * v for v in unit_tangent])
        new_v2_tangent_vector = tuple([v2_tangent * v for v in unit_tangent])
        new_v1 = tuple([n+t for n, t in zip(new_v1_normal_vector, new_v1_tangent_vector)])
        new_v2 = tuple([n+t for n, t in zip(new_v2_normal_vector, new_v2_tangent_vector)])
        item1.velocity = new_v1
        item2.velocity = new_v2

    def destructive(self, bullet, asteroid):
        asteroid.explode(bullet.momentum())
        self.arena.remove(bullet)
        
    def damage(self, item, ship):
        ship.health -= 0.1
        self.elastic(item, ship)


def dot(vector1, vector2):
    return sum(p*q for p,q in zip(vector1, vector2))
    
