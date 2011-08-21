from lxml import etree
from location import Location

class Door(Location):
    def __init__(self, map_name, xml):
        loc = xml.get('loc').split(',')
        loc = (int(loc[0]), int(loc[1]))
        Location.__init__(self, map_name, loc)

class MapService():
    def __init__(self):
        self.doc = etree.ElementTree(file='map.xml')

    def doors(self, map_name):
        retval = []
        for item in self.doc.xpath('//map[@name="%s"]/door' % map_name):
            retval.append(Door(map_name, item))
        return retval
