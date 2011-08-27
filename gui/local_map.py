import logging
import logging.config
import wx
import Image, ImageDraw, ImageFont
import os
from lxml import etree
from pprint import pprint

from location import Location
from map_service import MapService
from distance_service import DistanceService

if __name__ == '__main__':
    logging.config.fileConfig("logging.conf")

log = logging.getLogger(__name__)

el_to_bmp = 50. / 192
el_to_bmp = 94. / 384
el_to_bmp = 294. / (384 * 3)
MAP_OFFSET = [318, 234]

def el_to_dc(el_loc):
    doc = etree.ElementTree(file='map.xml')
    map_xml = doc.xpath('//map[@name="%s"]' % el_loc.map_name)[0]

    map_loc = map_xml.get('loc').split(',')
    map_loc = (int(map_loc[0]), int(map_loc[1]))
    map_size = map_xml.get('size').split(',')
    map_size = (int(map_size[0]), int(map_size[1]))

    #~ dc_loc = el_to_dc((map_loc[0] + el_loc.loc[0],
                       #~ map_loc[1] + map_size[1] - el_loc.loc[1]))
#~
    #~ return ((loc[0] + MAP_OFFSET[0]) * el_to_bmp,
            #~ (loc[1] + MAP_OFFSET[1]) * el_to_bmp)

    loc = el_loc.loc
    return ((map_loc[0] + loc[0] + MAP_OFFSET[0]) * el_to_bmp,
            (map_loc[1] + map_size[1] - loc[1] + MAP_OFFSET[1]) * el_to_bmp)

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

def DrawElLocation(dc, el_loc):
    dc_loc = el_to_dc(el_loc)
    #~ log.debug(dc_loc)
    DrawMarker(dc, dc_loc[0], dc_loc[1], 3)

class MapSprite():
    def __init__(self, loc, size, map_name):
        self.__loc__ = loc
        self.__size__ = size
        self.map_name = map_name

    def __loc_size__(self):
        loc = self.__loc__
        loc = (loc[0] + MAP_OFFSET[0], loc[1] + MAP_OFFSET[1])
        return (loc, self.__size__)

    def Draw(self, dc):
        loc, size = self.__loc_size__()
        dc.SetBrush(wx.Brush('red', wx.TRANSPARENT))
        dc.DrawRectangle(loc[0] * el_to_bmp,
                         loc[1] * el_to_bmp,
                         size[0] * el_to_bmp + 1,
                         size[1] * el_to_bmp + 1)

    def HitTest(self, x, y):
        loc, size = self.__loc_size__()
        if x < loc[0] * el_to_bmp or\
           x > (loc[0] + size[0]) * el_to_bmp or\
           y < loc[1] * el_to_bmp or\
           y > (loc[1] + size[1]) * el_to_bmp:

            return False

        el_loc = (int(x / el_to_bmp), int(y / el_to_bmp))
        el_loc = (el_loc[0] - MAP_OFFSET[0] - self.__loc__[0],
                  self.__size__[1] - (el_loc[1] - MAP_OFFSET[1] - self.__loc__[1]))
        return Location(self.map_name, el_loc)

def str_to_touple(map_size):
    map_size = map_size.split(',')
    return (int(map_size[0]), int(map_size[1]))

class DoorSprite():
    def __init__(self, xml):
        self.__xml__ = xml

    def Draw(self, dc):
        map_size = str_to_touple(self.__xml__.getparent().get('size'))
        loc = str_to_touple(self.__xml__.get('loc'))
        zoom = 512. / map_size[0]
        DrawMarker(dc,
                   loc[0] * zoom,
                   (map_size[1] - loc[1]) * zoom,
                   5)

class LocalMapWindow(wx.Window):
    def __init__(self, parent, map_name):
        wx.Window.__init__(self, parent, id=wx.ID_ANY,
                            style=wx.WANTS_CHARS
                          #| wx.RAISED_BORDER
                          #| wx.SUNKEN_BORDER
                           , name="sink")

        doc = etree.ElementTree(file='map.xml')
        map_xml = doc.xpath('//map[@name="%s"]' % map_name)[0]

        bg_image_path = os.path.expanduser('~/bin/el_linux/maps/%s' % map_xml.get('image'))
        self.image = wx.Image(bg_image_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()

        self.doors = map(lambda x: DoorSprite(x), map_xml.xpath('door'))

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

class LocalMapFrame(wx.Frame):
    def __init__(self, parent, map_name, id=wx.ID_ANY,
                 title="LocalMapFrame", pos=wx.DefaultPosition,
                 size=(512,512), style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self.wnd = LocalMapWindow(self, map_name=map_name)
        self.wnd.SetSize(self.GetSize())

def main():
    app = wx.App()
    win =  LocalMapFrame(None, pos=(0,0), map_name='Portland')
    win.Show()

    log.info("entering main loop")
    app.MainLoop()

