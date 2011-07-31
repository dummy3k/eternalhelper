import math
from lxml import etree
from copy import copy
from pprint import pprint
from dijkstra import Node, add_edge, solve, get_route

class LocatableObject():
    def __init__(self, xml):
        self.xml = xml

    def __repr__(self):
        m = self.xml.getparent()
        return "LocatableObject(map: %s, name: %s)" %\
            (m.get('name'),
             self.xml.get('name'))
        #~ return etree.tostring(self.xml)

    def loc_touple(self):
        retval = self.xml.get('loc').split(',')
        return (int(retval[0]), int(retval[1]))

    def target(self):
        return self.xml.get('target')

    def map_name(self):
        return self.xml.getparent().get('name')

doc = etree.ElementTree(file='map.xml')
dist_doc = etree.ElementTree(file='distances.xml')
all_nodes = []
for map_xml in doc.xpath('//map'):
    #~ for item in doc.xpath('//map[@name="Desert Pines"]/door'):
    nodes = []
    for item in map_xml.xpath('door'):
        node = Node(LocatableObject(item))
        nodes.append(node)

    #connected locations on same map
    unconnted = copy(nodes)
    while len(unconnted) > 0:
        current = unconnted.pop()
        for item in unconnted:
            from_loc = current.payload.xml.get('loc')
            to_loc = item.payload.xml.get('loc')
            #~ print "from_loc: %s, to_loc: %s" % (from_loc, to_loc)
            dist_xml = dist_doc.xpath('//distance[@from="%s"][@to="%s"]'\
                % (from_loc, to_loc))
            if not dist_xml:
                dist_xml = dist_doc.xpath('//distance[@from="%s"][@to="%s"]'\
                    % (to_loc, from_loc))

            if dist_xml:
                #~ print "dist_xml: %s" % etree.tostring(dist_xml[0])
                cost = int(dist_xml[0].get('seconds'))
            else:
                from_loc = current.payload.loc_touple()
                to_loc = item.payload.loc_touple()
                cost = math.sqrt( (from_loc[0] - to_loc[0])**2 +\
                                  (from_loc[1] - to_loc[1])**2)
                cost = int(cost)

            add_edge(cost, current, item)

    all_nodes.extend(nodes)

#connect doors
unconnted = copy(all_nodes)
while len(unconnted) > 0:
    current = unconnted.pop()
    for item in unconnted:
        if current.payload.target() == item.payload.target():
            unconnted.remove(item)
            add_edge(1, current, item)


for item in all_nodes:
    print item
    for subitem in item.edges:
        print "-->" + str(subitem)

def find_location_obj(map_name, loc):
    for item in all_nodes:
        p = item.payload
        if p.map_name() == map_name and p.loc_touple() == loc:
            return item

    raise Exception("not found")


# South Exit to Portland
where_am_i = find_location_obj('Desert Pines', (172,12))
where_am_i.cost = 0

solve(all_nodes)
for item in all_nodes:
    print item

# Crystal Cavern, North Entrance
destination_location = find_location_obj('Desert Pines', (44,302))

print "\nRoute"
for item in get_route(all_nodes, destination_location):
    print item
