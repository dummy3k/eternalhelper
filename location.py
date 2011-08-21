import logging

log = logging.getLogger(__name__)

class Location():
    def __init__(self, map_name, loc):
        self.map_name = map_name
        self.loc = loc

    def __repr__(self):
        return "Loc('%s', '%s')" % (self.map_name, self.loc)

    def __eq__(self, other):
        log.debug("%s == %s" % (self, other))
        return self.map_name == other.map_name and self.loc == other.loc

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.map_name.__hash__() ^ self.map_name.__hash__()
