import wx
from local_map import LocalMapFrame
from map_service import MapService

class EhApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        self.ms = MapService()
        self.local_map_windows = {}
        self.__nav__from = None

    def GetLocalMapWindow(self, map_name):
        if map_name in self.local_map_windows:
            return self.local_map_windows[map_name]

        win =  LocalMapFrame(None, self.ms, map_name)
        win.Show()
        self.local_map_windows[map_name] = win
        return win

    def SetNavFrom(self, loc):
        self.__nav__from = loc
        #~ if loc.map_name in self.local_map_windows:
            #~ self.local_map_windows[loc.map_name].wnd.Draw()
        for item in self.local_map_windows.values():
            item.wnd.Draw()

    def GetNavFrom(self):
        return self.__nav__from
