def hash_everything(l):
    try:
        return hash(l)
    except TypeError:
        try:
            xs = iter(l)
        except TypeError:
            return 0

        h = 0
        for x in xs:
            h = h ^ hash_everything(x)
        return h

class HashItAnyway:
    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.h = hash_everything(wrapped)

    def __eq__(self, other): 
        return isinstance(other,HashItAnyway) and self.wrapped == other.wrapped

    def __hash__(self):
        return self.h


class Tracker():
    def __init__(self):
        self.contents = set()

    def already_seen(self,x):
        k = HashItAnyway(x)
        if k not in self.contents:
            self.contents.add(k)
            return False
        else:
            return True

