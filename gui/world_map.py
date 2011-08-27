import logging
import logging.config
import wx
import Image, ImageDraw, ImageFont
import os
from lxml import etree
from pprint import pprint

#~ import map_info
#~ from get_location import get_last_location
#~ from log_thread import LogThread, LocationChangedEvent, EVT_LOCATION_CHANGED
from location import Location
from map_service import MapService
from distance_service import DistanceService

#~ from route import

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

class WordMapWindow(wx.Window):
    def __init__(self, parent):
        wx.Window.__init__(self, parent, id=wx.ID_ANY,
                            style=wx.WANTS_CHARS
                          #| wx.RAISED_BORDER
                          #| wx.SUNKEN_BORDER
                           , name="sink")

        bg_image_path = os.path.expanduser('~/bin/el_linux/maps/seridia.bmp')
        self.image = wx.Image(bg_image_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        doc = etree.ElementTree(file='map.xml')

        self.sprites = []
        self.current_map = None
        for item in doc.xpath('//map'):
            if not item.get('loc'):
                continue
            if not item.get('size'):
                continue

            loc = item.get('loc').split(',')
            loc = (int(loc[0]), int(loc[1]))
            size = item.get('size').split(',')
            size = (int(size[0]), int(size[1]))
            self.sprites.append(MapSprite(loc, size, item.get('name')))

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
            MAP_OFFSET[0] += 1
        elif event.GetKeyCode() == wx.WXK_LEFT:
            MAP_OFFSET[0] -= 1
        elif event.GetKeyCode() == wx.WXK_UP:
            MAP_OFFSET[1] -= 1
        elif event.GetKeyCode() == wx.WXK_DOWN:
            MAP_OFFSET[1] += 1

        self.Draw()
        log.debug("MAP_OFFSET: %s" % MAP_OFFSET)

    def OnMouse(self, event):
        if event.LeftDown():
            for item in self.sprites:
                if item.HitTest(event.GetX(), event.GetY()):
                    self.current_map = item
                    wx.GetApp().GetLocalMapWindow(item.map_name).Raise()

            self.Draw()

        if not event.LeftDown() and not event.RightDown():
            return
        log.debug("OnMouse(%s, %s)" % (event.GetX(), event.GetY()))
        self.SetFocus()


        for item in self.sprites:
            loc = item.HitTest(event.GetX(), event.GetY())
            if loc:
                #~ log.debug(loc)
                if event.RightDown():
                    wx.GetApp().SetNavFrom(loc)
                #~ else:
                    #~ self.nav_to = loc

        self.Draw()

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


        dc.SetPen(wx.Pen('black'))
        for item in self.sprites:
            item.Draw(dc)

        if self.current_map:
            dc.SetPen(wx.Pen('yellow'))
            self.current_map.Draw(dc)

        ms = MapService()
        ds = DistanceService(ms)

        if wx.GetApp().GetNavTo():
            dc.SetPen(wx.Pen('red'))
            DrawElLocation(dc, wx.GetApp().GetNavTo())

            dc.SetPen(wx.Pen('yellow'))
            for item in ms.doors(wx.GetApp().GetNavTo().map_name):
                DrawElLocation(dc, item)
            dc.SetPen(wx.Pen('green'))
            DrawElLocation(dc, ds.nearest_door(wx.GetApp().GetNavTo()))

        if wx.GetApp().GetNavFrom():
            dc.SetPen(wx.Pen('blue'))
            DrawElLocation(dc, wx.GetApp().GetNavFrom())

            dc.SetPen(wx.Pen('yellow'))
            for item in ms.doors(wx.GetApp().GetNavFrom().map_name):
                DrawElLocation(dc, item)
            dc.SetPen(wx.Pen('green'))
            DrawElLocation(dc, ds.nearest_door(wx.GetApp().GetNavFrom()))


        if wx.GetApp().GetNavTo() and wx.GetApp().GetNavFrom():
            route = wx.GetApp().GetRoute()
            #~ for item in route:
                #~ log.debug(item)

            dc.SetPen(wx.Pen('blue'))
            last_pos = el_to_dc(route[0].payload)
            for item in route[1:]:
                pos = el_to_dc(item.payload)
                dc.DrawLine(last_pos[0], last_pos[1],
                            pos[0], pos[1])
                last_pos = pos

class WordMapFrame(wx.Frame):
    def __init__(self, parent, id=wx.ID_ANY, title="WordMapFrame", pos=wx.DefaultPosition,
                 size=(512,512), style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)


        self.wnd = WordMapWindow(self)
        self.wnd.SetSize(self.GetSize())

def main():
    from eh_app import EhApp
    app = EhApp()
    win =  WordMapFrame(None, pos=(0,0))
    win.Show()

    log.info("entering main loop")
    app.MainLoop()

