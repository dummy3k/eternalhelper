import logging
import logging.config

if __name__ == '__main__':
    logging.config.fileConfig("logging.conf")

log = logging.getLogger(__name__)

if __name__ == '__main__':
    import gui.map_frame
    gui.map_frame.main()
