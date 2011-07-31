import re, os

class Extractor():
    def __init__(self):
        self.map_name = None
        self.loc = None

    def feed(self, s):
        m = re.match('.*Welcome to the (.*)', s)
        if m:
            self.map_name = m.group(1)
            return True

        m = re.match('.*You are in (.*)\s+\[(\d+),(\d+)\]', s)
        if m:
            map_name = m.group(1).strip()
            if map_name:
                self.map_name = map_name
            self.loc = (int(m.group(2)), int(m.group(3)))
            return True

        return False

def get_last_location():
    ex = Extractor()
    with open(os.path.expanduser('~/.elc/main/chat_log.txt')) as f:
        for line in f:
            ex.feed(line.strip())

    return ex

if __name__ == '__main__':
    ex = Extractor()
    with open(os.path.expanduser('~/.elc/main/chat_log.txt')) as f:
        for line in f:
            if ex.feed(line.strip()):
                print "%s\t'%s'" % (ex.loc, ex.map_name)
    pass


