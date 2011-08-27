import wx

class EhApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        self.local_map_windows = {}
