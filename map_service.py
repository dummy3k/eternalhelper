import logging
from lxml import etree
from location import Location
from helper import str_to_touple

log = logging.getLogger(__name__)

class Door(Location):
    def __init__(self, map_name, xml):
        loc = xml.get('loc').split(',')
        loc = (int(loc[0]), int(loc[1]))
        Location.__init__(self, map_name, loc)
        self.target = xml.get('target')
        self.name = xml.get('name')

    def __repr__(self):
        return "Door('%s', '%s' ['%s'])" % (self.map_name, self.name, self.loc)

class MapService():
    def __init__(self):
        self.doc = etree.ElementTree(file='map.xml')

    def doors(self, map_name):
        retval = []
        for item in self.doc.xpath('//map[@name="%s"]/door' % map_name):
            retval.append(Door(map_name, item))
        return retval

    def all_doors(self):
        retval = []
        for item in self.doc.xpath('//door'):
            map_name = item.getparent().get('name')
            retval.append(Door(map_name, item))
        return retval

    def other_side(self, door):
        for item in self.doc.xpath('//door[@target="%s"]' % door.target):
            other = Door(item.getparent().get('name'), item)
            if other != door:
                log.debug("%s != %s" % (other, door))
                return other
        return None

    def map_size(self, map_name):
        map_xml = self.doc.xpath('//map[@name="%s"]' % map_name)[0]
        return str_to_touple(map_xml.get('size'))
