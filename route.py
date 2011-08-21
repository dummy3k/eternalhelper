import logging
import logging.config

from lxml import etree
from copy import copy
from location import Location

if __name__ == '__main__':
    logging.config.fileConfig("logging.conf")

log = logging.getLogger(__name__)
doc = etree.ElementTree(file='map.xml')


class Map():
    def __init__(self, name):
            self.map_name = doc.xpath('//map[@name="%s"]' % name)[0].get('name')

    def __repr__(self):
        return "Map('%s')" % self.map_name

    def doors(self):
        retval = []
        for door in doc.xpath('//map[@name="%s"]/door' % self.map_name):
            retval.append(Door(self.map_name, door.get('name')))
            #~ print door.get('target')
            #~ for other_side in doc.xpath('//door[@target="%s"]' % door.get('target')):
                #~ print etree.tostring(other_side)
                #~ print other_side.getparent().get('name')
                #~ retval.append(Map(other_side.getparent().get('name')))

        return retval

    def __eq__(self, other):
        return self.map_name == other.map_name

class Door(Location):
    def __init__(self, map_name, name):
            xml = doc.xpath('//map[@name="%s"]/door[@name="%s"]' % (map_name, name))[0]
            #~ print etree.tostring(xml)
            Location.__init__(self, map_name, xml.get('loc'))
            #~ Location.__init__(self, map_name, doc.xpath('//map[@name="%s"]/door[@name="%s"]' % (map_name, name))[0].get('loc'))
            self.door_name = name

            if not xml.get('target'):
                raise Exception("door without target: %s" % etree.tostring(xml))
            self.target = xml.get('target')

            #~ print xml.get('target')
            #~ print sides
            #~ print len(sides)

    def other_side(self):
            sides = doc.xpath('//door[@target="%s"]' % self.target)

            if sides[0].getparent().get('name') == self.map_name and\
               sides[0].get('name') == self.door_name:

                return Door(sides[1].getparent().get('name'), sides[1].get('name'))
            else:
                return Door(sides[0].getparent().get('name'), sides[0].get('name'))


    def __repr__(self):
        return "Door('%s', '%s')" % (Location.__repr__(self), self.door_name)

class Distance():
    def __init__(self, from_loc, to_loc):
        self.from_loc = from_loc
        self.to_loc = to_loc

        if isinstance(from_loc, Door) and isinstance(to_loc, Door) and\
            from_loc.target == to_loc.target:
            self.cost = 1
        else:
            self.cost = None

    def __repr__(self):
        return "Dist($%s, '%s' -> '%s')" % (self.cost, self.from_loc, self.to_loc)

class LevelPrinter():
    def __init__(self, level):
        self.level = level

    def print_it(self, s):
        log.debug(" " * self.level + str(s))

    def indent(self):
        return LevelPrinter(self.level + 1)

def find_routes(loc, route, destination, lvlprt):
    #~ print "find_routes(%s, %s, %s)" % (loc, route, destination)
    lvlprt.print_it("find_routes(%s, ...)" % (loc, ))
    #~ for item in route[-1].doors():
        #~ print item

    if loc == destination:
        #~ print "FOUND ROUTE(%s, %s, %s)" % (loc, route, destination)
        lvlprt.print_it("FOUND ROUTE")
        for item in route:
            #~ print item
            if item.cost:
                cost = item.cost
            else:
                cost = "?"
            lvlprt.print_it("$%s \t %s, %s \t %s, %s" % (cost, item.from_loc.map_name, item.from_loc.door_name, item.to_loc.map_name, item.to_loc.door_name))
            return

    door_dist = Distance(loc, loc.other_side())
    visited = map(lambda x: x.to_loc, route)
    if door_dist.to_loc in visited:
        lvlprt.print_it("visted")
        return

    #~ this_map = Map(loc.map_name)

    for door in Map(door_dist.to_loc.map_name).doors():
        new_route = copy(route)
        new_route.append(door_dist)

        map_dist = Distance(loc, door)
        new_route.append(map_dist)

        find_routes(door, new_route, destination, lvlprt.indent())


        #~ print item in route
        #~ if not item in route:

#~ def calc_distances(loc, ms, ds):

if __name__ == '__main__':
    #~ current_location = Location('Desert Pines Storage', 'Entrance')
    #~ destination_location = Location('Crystal Cavern', 'Rose Quartz')
    #~ current_location = Location(doc.xpath('//map[@name="Desert Pines"]/door[@name="Storage Entrance"]')[0])
    #~ current_location = Map('Desert Pines Storage')
    #~ current_location = Map('Portland')
    #~ current_location = Map('Desert Pines')
    current_location = Door('Desert Pines Storage', "Entrance")
    destination_location = Door("White Stone", "Ship to Isla Prima")
    #~ destination_location = Door("Crystal Cavern", "East Entrance")
    #~ destination_location = Map("Crystal Cavern")
    #~ destination_location = Location(doc.xpath('//map[@name="Crystal Cavern"]/harvestable[@type="Rose Quartz"]')[0])
    #~ destination_location =None

    print current_location
    print destination_location
    #~ print destination_location == Door("Crystal Cavern", "East Entrance")

    initial_route = [Distance(current_location, current_location.other_side)]
    find_routes(current_location, [], destination_location, LevelPrinter(0))

    #for door in current_location.doors():
        #print "--- %s" % door
        ##~ initial_route = [Dist(door, door.other_side)]
        #find_routes(door, [], destination_location, LevelPrinter(0))
    #~ find_routes([current_location], destination_location)

    #~ for e in doc.xpath('//map'):
        #~ print e.get('name')

    #~ for e in doc.xpath('//map[@name="Desert Pines"]/door'):
        #~ print etree.tostring(e)

    #~ doc.xpath('//map[@name="Desert Pines"]/door[@name="Storage Entrance"]')[0]


