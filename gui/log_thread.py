import logging
import logging.config

if __name__ == '__main__':
    logging.config.fileConfig("logging.conf")

import os
import wx
import wx.lib.newevent
from threading import Thread
from time import sleep
from get_location import Extractor

log = logging.getLogger(__name__)
(LocationChangedEvent, EVT_LOCATION_CHANGED) = wx.lib.newevent.NewEvent()

class LogThread(Thread):
    def __init__(self, window=None):
        Thread.__init__(self)
        self.x = False
        self.window = window

    def run(self):
        ex = Extractor()
        with open(os.path.expanduser('~/.elc/main/chat_log.txt')) as f:
            line = f.readline()
            while line != "":
                ex.feed(line.strip())
                line = f.readline()

            while True:
                line = f.readline()
                while line != "":
                    if ex.feed(line.strip()):
                        log.info("changed location %s, '%s'" % (ex.loc, ex.map_name))
                        if self.window:
                            #~ log.debug("posting event")
                            evt = LocationChangedEvent(map_name=ex.map_name, loc=ex.loc)
                            #~ evt = LocationChangedEvent()
                            wx.PostEvent(self.window, evt)
                    line = f.readline()

                log.debug("Sleeping...")
                sleep(1)
        self.x = True
        print "thread!"
        #~ app.MainLoop()


#~ if __name__ == '__main__':
def main():
    t = LogThread()
    t.run()
    print "end"
    if t.is_alive():
        t.join(1)
    print "past end"

