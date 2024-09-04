from collections import namedtuple


class Item:
    def __init__(self, id=None, type=None, url=None):
        self.id = id
        self.type = type
        self.url = url

    def __str__(self):
        return f"Item(id={self.id}, type={self.type}, url={self.url})"


BpmRange = namedtuple("bpmrange", ["min", "max"])
