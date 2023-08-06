class NagList(list):
    def __getattr__(self, name):

        if name == 'first':
            if self:
                return self[0]
            else:
                return None

        if name == 'names':
            return [x.name for x in self]

        obj = [x for x in self if x.name == name]
        if obj:
            if len(obj) == 1:
                return obj[0]
            else:
                raise AttributeError('Multiple instances found')

        raise AttributeError
