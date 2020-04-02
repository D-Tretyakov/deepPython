from collections import OrderedDict

class ICache:
    def __init__(self, capacity: int=10) -> None:
        self.cache = OrderedDict()
        self.maxsize = capacity

    def get(self, key: str) -> str:
        return self.cache[key] if key in self.cache else ''

    def add(self, key: str, value: str) -> None:
        if key in self.cache:
            self.cache[key] = value
            self.cache.move_to_end(key)
        else:
            self.cache[key] = value

        if len(self.cache) > self.maxsize:
            self.cache.popitem(last=False)

    def remove(self, key: str) -> None:
        if key in self.cache:
            del self.cache[key]
        else:
            raise KeyError('No such element')