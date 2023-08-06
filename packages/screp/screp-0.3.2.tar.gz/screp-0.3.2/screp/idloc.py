

class Location(object):
    def __init__(self, source, index):
        self.source = source
        self.index = index


    def __str__(self):
        return "%s:%s" % (self.source, self.index)


    __repr__ = __str__


class Identification(object):
    def __init__(self, name, type, location):
        self.name = name
        self.type = type
        self.location = location


    def __str__(self):
        return "%s %s(at %s)" % (self.type, self.name, self.location)


    __repr__ = __str__


class LocationFactory(object):
    def __init__(self, source, index_offset=0):
        self.source = source
        self.index_offset = index_offset


    def make_location(self, index):
        return Location(self.source, index + self.index_offset)


