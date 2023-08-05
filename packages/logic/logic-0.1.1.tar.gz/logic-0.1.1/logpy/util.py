class frozendict(dict):
    __slots__ = ('_hash',)
    def __hash__(self):
        h = getattr(self, '_hash', None)
        if not h:
            rval = self._hash = hash(frozenset(self.iteritems()))
        return h
