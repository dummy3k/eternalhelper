import logging
import logging.config

if __name__ == '__main__':
    logging.config.fileConfig("logging.conf")

log = logging.getLogger(__name__)

if __name__ == '__main__':
    import gui.world_map
    gui.world_map.main()
