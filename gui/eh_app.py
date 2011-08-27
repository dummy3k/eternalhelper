import wx
from local_map import LocalMapFrame
from map_service import MapService

class EhApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        self.ms = MapService()
        self.local_map_windows = {}
        self.__nav_from__ = None
        self.__nav_to__ = None

    def GetLocalMapWindow(self, map_name):
        if map_name in self.local_map_windows:
            return self.local_map_windows[map_name]

        win =  LocalMapFrame(None, self.ms, map_name)
        win.Show()
        self.local_map_windows[map_name] = win
        return win

    def SetNavFrom(self, loc):
        self.__nav_from__ = loc
        for item in self.local_map_windows.values():
            item.wnd.Draw()

    def GetNavFrom(self):
        return self.__nav_from__

    def SetNavTo(self, loc):
        self.__nav_to__ = loc
        for item in self.local_map_windows.values():
            item.wnd.Draw()

    def GetNavTo(self):
        return self.__nav_to__
