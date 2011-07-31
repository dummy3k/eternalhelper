import logging
import logging.config
import wx
import Image, ImageDraw, ImageFont
import os
from lxml import etree

from get_location import get_last_location

if __name__ == '__main__':
    logging.config.fileConfig("logging.conf")

log = logging.getLogger(__name__)

class MapFrame(wx.Frame):
    def __init__(self, parent, id=wx.ID_ANY, title="MapFrame", pos=wx.DefaultPosition,
                 size=(500,500), style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)

        self.image = None
        self.loc = None

    def OnMouse(self, event):
        if not event.LeftDown():
            return
        log.debug("OnMouse!")
        ex = get_last_location()
        log.debug("map_name: %s, loc: %s" % (ex.map_name, ex.loc))

        doc = etree.ElementTree(file='map.xml')
        map_xml = doc.xpath('//map[@name="%s"]' % ex.map_name)
        if not map_xml:
            log.warn("unkown map '%s'" % ex.map_name)
        else:
            bg_image_path = os.path.expanduser('~/bin/el_linux/maps')
            bg_image_path = os.path.join(bg_image_path, map_xml[0].get('image'))
            self.image = wx.Image(bg_image_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            self.loc = ex.loc
            self.Draw()


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

        if self.image:
            png_dc = wx.MemoryDC()
            png_dc.SelectObject(self.image)
            dc.Blit(0, 0, self.image.GetWidth(), self.image.GetHeight(),
                    png_dc, 0, 0)

        if self.loc:
            dc.SetPen(wx.Pen('blue'))
            dc.DrawLine(self.loc[0] - 10,
                        self.loc[1] - 10,
                        self.loc[0] + 10,
                        self.loc[1] + 10)
            dc.DrawLine(self.loc[0] + 10,
                        self.loc[1] - 10,
                        self.loc[0] - 10,
                        self.loc[1] + 10)


def main():
    app = wx.App()
    win =  MapFrame(None, pos=(0,0))
    win.Show()

    log.info("entering main loop")
    app.MainLoop()

