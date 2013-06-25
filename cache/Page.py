import cStringIO

class Page(object):
    def __init__(self):
        self.Nests = {}
        self.buffer = cStringIO.StringIO()
