import logging
import logging.config

if __name__ == '__main__':
    logging.config.fileConfig("logging.conf")

log = logging.getLogger(__name__)

if __name__ == '__main__':
    import gui.log_thread
    gui.log_thread.main()
