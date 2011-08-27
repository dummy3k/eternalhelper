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

def el_to_dc(ms, loc):
    map_size = ms.map_size(loc.map_name)
    __zoom__ = 512. / map_size[0]
    return (loc.loc[0] * __zoom__,
            (map_size[1] - loc.loc[1]) * __zoom__)


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

class LocalMapSprite():
    def __init__(self, ms, map_name):
        self.map_size = ms.map_size(map_name)
        self.__zoom__ = 512. / self.map_size[0]

    def __to_dc__(self, loc):
        return (loc[0] * self.__zoom__,
                (self.map_size[1] - loc[1]) * self.__zoom__)

class DoorSprite(LocalMapSprite):
    def __init__(self, ms, door):
        LocalMapSprite.__init__(self, ms, door.map_name)
        self.door = door
        self.__dc_loc__ = self.__to_dc__(door.loc)
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

class RoomSprite(LocalMapSprite):
    def __init__(self, ms, map_name, p1, p2):
        LocalMapSprite.__init__(self, ms, map_name)
        log.debug("p1: %s, p1: %s" % (p1, p2))
        self.__p1_dc__ = self.__to_dc__(p1)
        self.__p2_dc__ = self.__to_dc__(p2)

    def Draw(self, dc):
        dc.DrawRectangle(self.__p1_dc__[0],
                         self.__p1_dc__[1],
                         self.__p2_dc__[0] - self.__p1_dc__[0],
                         self.__p2_dc__[1] - self.__p1_dc__[1])

class LocalMapWindow(wx.Window):
    def __init__(self, parent, ms, map_name):
        wx.Window.__init__(self, parent, id=wx.ID_ANY,
                            style=wx.WANTS_CHARS
                          #| wx.RAISED_BORDER
                          #| wx.SUNKEN_BORDER
                           , name="sink")

        self.map_name = map_name
        doc = etree.ElementTree(file='map.xml')
        map_xml = doc.xpath('//map[@name="%s"]' % map_name)[0]

        if map_xml.get('image'):
            bg_image_path = os.path.expanduser('~/bin/el_linux/maps/%s' % map_xml.get('image'))
            self.image = wx.Image(bg_image_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        else:
            self.image = None


        self.ms = ms
        self.doors = map(lambda x: DoorSprite(self.ms, x),
                         self.ms.doors(map_name))

        self.rooms = map(lambda x: RoomSprite(ms, map_name,
                                              str_to_touple(x.get('p1')),
                                              str_to_touple(x.get('p2'))),
                         map_xml.xpath('room'))
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
        dc.SetBackground(wx.Brush('black'))
        dc.Clear()
        #~ dc.SetBrush(wx.Brush('red', wx.TRANSPARENT))

        if self.image:
            png_dc = wx.MemoryDC()
            png_dc.SelectObject(self.image)
            dc.Blit(0, 0, self.image.GetWidth(), self.image.GetHeight(),
                    png_dc, 0, 0)

        dc.SetPen(wx.Pen('black'))
        for item in self.rooms:
            item.Draw(dc)
        for item in self.doors:
            item.Draw(dc)

        if wx.GetApp().GetNavFrom() and wx.GetApp().GetNavFrom().map_name == self.map_name:
            s = LocalMapSprite(self.ms, self.map_name)
            l = s.__to_dc__(wx.GetApp().GetNavFrom().loc)
            dc.SetPen(wx.Pen('blue'))
            DrawMarker(dc, l[0], l[1],  5)

        if wx.GetApp().GetNavTo() and wx.GetApp().GetNavTo().map_name == self.map_name:
            s = LocalMapSprite(self.ms, self.map_name)
            l = s.__to_dc__(wx.GetApp().GetNavTo().loc)
            dc.SetPen(wx.Pen('red'))
            DrawMarker(dc, l[0], l[1],  5)

        if wx.GetApp().GetRoute():
            dc.SetPen(wx.Pen('blue'))
            last_pos = None
            for item in wx.GetApp().GetRoute():
                if item.payload.map_name != self.map_name:
                    continue
                log.debug(item)
                pos = el_to_dc(self.ms, item.payload)
                if last_pos:
                    dc.DrawLine(last_pos[0], last_pos[1],
                                pos[0], pos[1])
                last_pos = pos


    def HitTest(self, x, y):
        for item in self.doors:
            if item.HitTest(x, y):
                return item
        return None

class LocalMapFrame(wx.Frame):
    def __init__(self, parent, ms, map_name, id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=(512,512), style=wx.DEFAULT_FRAME_STYLE):

        title = map_name
        self.map_name = map_name
        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        wx.GetApp().local_map_windows[map_name] = self

        self.ms = ms
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

        if event.ButtonDClick():
            log.debug("Close!")
            wx.GetApp().local_map_windows.pop(self.map_name)
            self.Close()

        hit = self.wnd.HitTest(event.GetX(), event.GetY())
        if hit:
            hit = hit.door
            self.status_bar.SetStatusText(str(hit), 0)
        else:
            self.status_bar.SetStatusText("", 0)

        if hit and event.LeftDown():
            log.debug("hit: %s" % hit)
            other_side = self.ms.other_side(hit)
            log.debug("other_side: %s" % other_side)

            if other_side.map_name not in wx.GetApp().local_map_windows:
                log.debug("other_side.map_name: %s" % other_side.map_name)
                win =  LocalMapFrame(None, self.ms, other_side.map_name)
                win.Show()

        if not hit and event.LeftDown():
            map_size = self.ms.map_size(self.map_name)
            zoom = map_size[0] / 512.
            loc = (int(event.GetX() * zoom),
                   map_size[1] - int(event.GetY() * zoom))
            log.debug("OnMouse(%s, %s) -> (%s, %s)" % (event.GetX(),
                                                       event.GetY(),
                                                       loc[0],
                                                       loc[1]))
            wx.GetApp().SetNavTo(Location(self.map_name, loc))


def main():
    from eh_app import EhApp
    app = EhApp()
    win =  LocalMapFrame(None, MapService(), 'Portland', pos=(0,0))
    #~ win =  LocalMapFrame(None, MapService(), 'Portland Cave', pos=(0,0))
    win.Show()

    log.info("entering main loop")
    app.MainLoop()

