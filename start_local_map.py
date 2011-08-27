import logging
import logging.config

if __name__ == '__main__':
    logging.config.fileConfig("logging.conf")

log = logging.getLogger(__name__)

if __name__ == '__main__':
    import gui.local_map
    gui.local_map.main()
