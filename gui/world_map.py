import logging
import logging.config
import wx
import Image, ImageDraw, ImageFont
import os
from lxml import etree

import map_info
from get_location import get_last_location
from log_thread import LogThread, LocationChangedEvent, EVT_LOCATION_CHANGED

if __name__ == '__main__':
    logging.config.fileConfig("logging.conf")

log = logging.getLogger(__name__)

class WordMapWindow(wx.Window):
    def __init__(self, parent):
        wx.Window.__init__(self, parent, id=wx.ID_ANY,
                            style=wx.WANTS_CHARS
                          #| wx.RAISED_BORDER
                          #| wx.SUNKEN_BORDER
                           , name="sink")

        bg_image_path = os.path.expanduser('~/bin/el_linux/maps/seridia.bmp')
        self.image = wx.Image(bg_image_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()

        self.offset = [318, 234]

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    def OnSize(self, event):
        log.debug("OnSize!")
        self.Width, self.Height = self.GetClientSizeTuple()
        self._Buffer = wx.EmptyBitmap(self.Width, self.Height)
        self.Draw()

    def OnPaint(self, event):
        log.debug("OnPaint()")
        self.Draw()

    def OnKeyDown(self, event):
        log.debug("OnKeyDown()")
        #~ log.debug(event.GetKeyCode())
        if event.GetKeyCode() == wx.WXK_RIGHT:
            self.offset[0] += 1
        elif event.GetKeyCode() == wx.WXK_LEFT:
            self.offset[0] -= 1
        elif event.GetKeyCode() == wx.WXK_UP:
            self.offset[1] -= 1
        elif event.GetKeyCode() == wx.WXK_DOWN:
            self.offset[1] += 1

        self.Draw()
        log.debug("self.offset: %s" % self.offset)

    def OnMouse(self, event):
        if not event.LeftDown():
            return
        log.debug("OnMouse!")
        self.Draw()
        self.SetFocus()

    def Draw(self):
        log.debug("Draw()")
        dc = wx.BufferedPaintDC(self, self._Buffer)
        dc.Clear()

        if not self.image:
            return

        png_dc = wx.MemoryDC()
        png_dc.SelectObject(self.image)
        dc.Blit(0, 0, self.image.GetWidth(), self.image.GetHeight(),
                png_dc, 0, 0)

        el_to_bmp = 50. / 192
        el_to_bmp = 94. / 384
        el_to_bmp = 294. / (384 * 3)

        doc = etree.ElementTree(file='map.xml')

        for item in doc.xpath('//map'):
            if not item.get('loc'):
                continue
            if not item.get('size'):
                continue

            loc = item.get('loc').split(',')
            loc = (int(loc[0]), int(loc[1]))
            size = item.get('size').split(',')
            size = (int(size[0]), int(size[1]))

            loc = (loc[0] + self.offset[0], loc[1] + self.offset[1])
            log.debug("%s, %s, %s" % (item.get('name'), loc, size))

            dc.SetBrush(wx.Brush('red', wx.TRANSPARENT))
            dc.DrawRectangle(loc[0] * el_to_bmp,
                             loc[1] * el_to_bmp,
                             size[0] * el_to_bmp + 1,
                             size[1] * el_to_bmp + 1)

        for item in doc.xpath('//door'):
        #~ for item in doc.xpath('//door[@name="Storage Entrance"]'):
            if not item.getparent().get('loc'):
                continue
            if not item.getparent().get('size'):
                continue
            log.debug(item.get('name'))

            loc = item.get('loc').split(',')
            loc = (int(loc[0]), int(loc[1]))
            map_loc = item.getparent().get('loc').split(',')
            map_loc = (int(map_loc[0]), int(map_loc[1]))
            map_size = item.getparent().get('size').split(',')
            map_size = (int(map_size[0]), int(map_size[1]))

            loc = (map_loc[0] + loc[0],
                   map_loc[1] + map_size[1] - loc[1])
            log.debug(loc)
            loc = (loc[0] + self.offset[0], loc[1] + self.offset[1])
            dc.DrawCircle(loc[0] * el_to_bmp, loc[1] * el_to_bmp, 4)
            self.DrawCross(dc, loc[0] * el_to_bmp, loc[1] * el_to_bmp, 3)

    def DrawCross(self, dc, x, y, size):
        dc.DrawLine(x - size,
                    y - size,
                    x + size,
                    y + size)
        dc.DrawLine(x + size,
                    y - size,
                    x - size,
                    y + size)

class WordMapFrame(wx.Frame):
    def __init__(self, parent, id=wx.ID_ANY, title="WordMapFrame", pos=wx.DefaultPosition,
                 size=(512,512), style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)


        self.wnd = WordMapWindow(self)
        self.wnd.SetSize(self.GetSize())


def main():
    app = wx.App()
    win =  WordMapFrame(None, pos=(0,0))
    win.Show()

    log.info("entering main loop")
    app.MainLoop()

