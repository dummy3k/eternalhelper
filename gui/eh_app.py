import logging
import wx
from local_map import LocalMapFrame
from map_service import MapService
from distance_service import DistanceService
from dijkstra import Node, add_edge, solve, get_route

log = logging.getLogger(__name__)

class EhApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        self.ms = MapService()
        self.ds = DistanceService(self.ms)
        self.local_map_windows = {}
        self.__nav_from__ = None
        self.__nav_to__ = None
        self.__route__ = None

    def GetLocalMapWindow(self, map_name):
        if map_name in self.local_map_windows:
            return self.local_map_windows[map_name]

        win =  LocalMapFrame(None, self.ms, map_name)
        win.Show()
        self.local_map_windows[map_name] = win
        return win

    def SetNavFrom(self, loc):
        self.__nav_from__ = loc
        self.__nav_from_to__changed()

    def GetNavFrom(self):
        return self.__nav_from__

    def SetNavTo(self, loc):
        self.__nav_to__ = loc
        self.__nav_from_to__changed()

    def __nav_from_to__changed(self):
        if self.__nav_from__ and self.__nav_to__:
            self.__calc_route__()

        for item in self.local_map_windows.values():
            item.wnd.Draw()

    def GetNavTo(self):
        return self.__nav_to__

    def GetRoute(self):
        return self.__route__

    def __calc_route__(self):
        node_dict = {}
        map_dict = {}
        for item in self.ms.all_doors():
            node = Node(item)
            node_dict[item] = node
            if not item.map_name in map_dict:
                map_dict[item.map_name] = []

            map_dict[item.map_name].append(node)

        from_node = Node(wx.GetApp().GetNavFrom())
        map_dict[wx.GetApp().GetNavFrom().map_name].append(from_node)

        to_node = Node(wx.GetApp().GetNavTo())
        map_dict[wx.GetApp().GetNavTo().map_name].append(to_node)


        for map_name, map_nodes in map_dict.items():
            for index, item_a in enumerate(map_nodes):
                for item_b in map_nodes[index + 1:]:
                    cost = self.ds.in_map_distance(item_a.payload, item_b.payload)
                    add_edge(cost, item_a, item_b)

        for item, node in node_dict.items():
            other_item = self.ms.other_side(item)
            cost = self.ds.cost(item, other_item)
            cost = 1
            node.edges.append((cost, node_dict[other_item]))

        node_dict[wx.GetApp().GetNavFrom()] = from_node
        node_dict[wx.GetApp().GetNavTo()] = to_node

        nodes = node_dict.values()
        for item in nodes:
            log.debug(item)
            for item_b in item.edges:
                log.debug("  %s" % str(item_b))

        from_node.cost = 0
        solve(nodes)
        for item in nodes:
            log.debug(item)
        log.debug("ROUTE:")
        self.__route__ = get_route(nodes, node_dict[wx.GetApp().GetNavTo()])
