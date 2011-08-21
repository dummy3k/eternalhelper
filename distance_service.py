import math
from lxml import etree

class DistanceService():
    def __init__(self, ms):
        self.ms = ms
        self.doc = etree.ElementTree(file='distances.xml')

    def in_map_distance(self, alpha, beta):
        return math.sqrt((alpha.loc[0] - beta.loc[0])**2 +
                         (alpha.loc[1] - beta.loc[1])**2)

    def cost(self, alpha, beta):
        return 1

    def nearest_door(self, loc):
        doors = self.ms.doors(loc.map_name)
        tmp = map(lambda x: (self.in_map_distance(loc, x), x), doors)
        tmp.sort()
        return tmp[0][1]

