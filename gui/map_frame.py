import logging
import logging.config
import wx
import Image, ImageDraw, ImageFont
import os

if __name__ == '__main__':
    logging.config.fileConfig("logging.conf")

log = logging.getLogger(__name__)

class MapFrame(wx.Frame):
    def __init__(self, parent, id=wx.ID_ANY, title="MapFrame", pos=wx.DefaultPosition,
                 size=(640,480), style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        bg_image_path = os.path.expanduser('~/bin/el_linux/maps/map15f.bmp')
        self.image = wx.Image(bg_image_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()

    def OnSize(self, event):
        log.debug("OnSize!")
        self.Width, self.Height = self.GetClientSizeTuple()
        self._Buffer = wx.EmptyBitmap(self.Width, self.Height)
        self.Draw()

    def OnPaint(self, event):
        log.debug("OnPaint()")
        self.Draw()

    def Draw(self):
        log.info("Draw()")
        dc = wx.BufferedPaintDC(self, self._Buffer)
        dc.Clear()
        #~ dc.SetPen(wx.Pen('black'))

        if self.image:
            png_dc = wx.MemoryDC()
            png_dc.SelectObject(self.image)
            dc.Blit(0, 0, self.image.GetWidth(), self.image.GetHeight(),
                    png_dc, 0, 0)

def main():
    app = wx.App()
    win =  MapFrame(None, pos=(0,0))
    win.Show()

    log.info("entering main loop")
    app.MainLoop()


if __name__ == '__main__':
    main()
