import logging
import logging.config
import wx
import Image, ImageDraw, ImageFont
import os
from lxml import etree
from pprint import pprint

from location import Location
from map_service import MapService, Door
from helper import str_to_touple

if __name__ == '__main__':
    logging.config.fileConfig("logging.conf")

log = logging.getLogger(__name__)

def DrawMarker(dc, x, y, size):
    dc.DrawCircle(x, y, 4)
    dc.DrawLine(x - size,
                y - size,
                x + size,
                y + size)
    dc.DrawLine(x + size,
                y - size,
                x - size,
                y + size)

class DoorSprite():
    def __init__(self, ms, door):
        self.door = door
        #~ self.__xml__ = xml

        #~ map_size = str_to_touple(self.__xml__.getparent().get('size'))
        map_size = ms.map_size(door.map_name)
        #~ loc = str_to_touple(self.__xml__.get('loc'))
        loc = door.loc
        zoom = 512. / map_size[0]
        self.__dc_loc__ = (loc[0] * zoom, (map_size[1] - loc[1]) * zoom)
        self.__dc_size = 5

    def __repr__(self):
        return "DoorSprite('%s')" % self.door

    def Draw(self, dc):
        DrawMarker(dc,
                   self.__dc_loc__[0],
                   self.__dc_loc__[1],
                   self.__dc_size)

    def HitTest(self, x, y):
        if x >= self.__dc_loc__[0] - self.__dc_size and\
           x <= self.__dc_loc__[0] + self.__dc_size and\
           y >= self.__dc_loc__[1] - self.__dc_size and\
           y <= self.__dc_loc__[1] + self.__dc_size:
               return True

        return False

class LocalMapWindow(wx.Window):
    def __init__(self, parent, ms, map_name):
        wx.Window.__init__(self, parent, id=wx.ID_ANY,
                            style=wx.WANTS_CHARS
                          #| wx.RAISED_BORDER
                          #| wx.SUNKEN_BORDER
                           , name="sink")

        doc = etree.ElementTree(file='map.xml')
        map_xml = doc.xpath('//map[@name="%s"]' % map_name)[0]

        bg_image_path = os.path.expanduser('~/bin/el_linux/maps/%s' % map_xml.get('image'))
        self.image = wx.Image(bg_image_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()

        self.ms = ms
        self.doors = map(lambda x: DoorSprite(self.ms, Door(map_name, x)),
                         map_xml.xpath('door'))

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)

    def OnSize(self, event):
        log.debug("OnSize!")
        self.Width, self.Height = self.GetClientSizeTuple()
        self._Buffer = wx.EmptyBitmap(self.Width, self.Height)
        self.Draw()

    def OnPaint(self, event):
        log.debug("OnPaint()")
        self.Draw()

    def OnMouse(self, event):
        if not event.LeftDown() and not event.RightDown():
            return
        log.debug("OnMouse(%s, %s)" % (event.GetX(), event.GetY()))

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

        for item in self.doors:
            item.Draw(dc)

    def HitTest(self, x, y):
        for item in self.doors:
            if item.HitTest(x, y):
                return item
        return None

class LocalMapFrame(wx.Frame):
    def __init__(self, parent, map_name, id=wx.ID_ANY,
                 title="LocalMapFrame", pos=wx.DefaultPosition,
                 size=(512,512), style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self.ms = MapService()

        self.wnd = LocalMapWindow(self, self.ms, map_name)
        self.wnd.SetSize(self.GetSize())

        self.status_bar = wx.StatusBar(self)
        self.SetStatusBar(self.status_bar)

        self.SetSize((size[0], size[1] + self.status_bar.GetSize()[1]))

        self.wnd.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)

    def OnMouse(self, event):
        #~ if not event.LeftDown() and not event.RightDown():
            #~ return
        #~ log.debug("OnMouse(%s, %s)" % (event.GetX(), event.GetY()))
        hit = self.wnd.HitTest(event.GetX(), event.GetY())
        if hit:
            hit = hit.door
            log.debug("hit: %s" % hit)
            other_side = self.ms.other_side(hit)
            log.debug("other_side: %s" % other_side)
            self.status_bar.SetStatusText(str(hit), 0)
        else:
            self.status_bar.SetStatusText("", 0)

def main():
    app = wx.App()
    win =  LocalMapFrame(None, pos=(0,0), map_name='Portland')
    win.Show()

    log.info("entering main loop")
    app.MainLoop()

