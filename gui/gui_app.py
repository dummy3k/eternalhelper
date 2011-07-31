import logging
import logging.config
import wx

if __name__ == '__main__':
    logging.config.fileConfig("logging.conf")

log = logging.getLogger(__name__)

class GuiApp(wx.App):
    pass

def main():
    app = wx.App()
    win =  MapFrame(None, pos=(0,0))
    win.Show()

    log.info("entering main loop")
    app.MainLoop()


if __name__ == '__main__':
    main()
