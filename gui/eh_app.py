import wx
from local_map import LocalMapFrame
from map_service import MapService

class EhApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        self.ms = MapService()
        self.local_map_windows = {}

    def GetLocalMapWindow(self, map_name):
        if map_name in self.local_map_windows:
            return self.local_map_windows[map_name]

        win =  LocalMapFrame(None, self.ms, map_name)
        win.Show()
        self.local_map_windows[map_name] = win
        return win

