from lxml import etree

def load_by_alias(map_name):
    doc = etree.ElementTree(file='map.xml')
    map_xml = doc.xpath('//map[@name="%s"]' % map_name)
    if map_xml:
        return map_xml
    else:
        map_xml = doc.xpath('//alias[@name="%s"]' % map_name)
        if map_xml is not None:
            return map_xml[0].getparent()
        return None

