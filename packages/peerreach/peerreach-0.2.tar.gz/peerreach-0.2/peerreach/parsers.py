import json


class RawParser(object):
    def parse(self, raw):
        return raw


class JSONParser(object):
    def parse(self, raw):
        return json.loads(raw)


class PeerreachObject(object):
    def __init__(self, raw):
        data = json.loads(raw)
        self.__dict__.update(data)


class ObjectParser(object):
    def __init__(self, klass=PeerreachObject):
        self.klass = klass

    def parse(self, raw):
        return self.klass(raw)
