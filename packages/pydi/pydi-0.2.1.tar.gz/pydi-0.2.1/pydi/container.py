class Component(object):

    def __init__(self, cls, **kwargs):
        self.cls = cls
        self.kwargs = kwargs
        self.dependencies = []

        self._shared = False
        self._instance = None

    def shared(self):
        self._shared = True

    def depends(self, cls, **kwargs):
        self.dependencies.append(Component(cls, **kwargs))
        return self

    def __call__(self, **kwargs):
        if self._shared and self._instance:
            return self._instance

        args = map(lambda x: x(**x.kwargs), self.dependencies)

        target = self.cls
        obj = target(*args, **kwargs) if callable(target) else target

        if self._shared:
            self._instance = obj

        return obj


class Container(dict):

    def register(self, cls):
        key = cls.__name__.lower()
        component = Component(cls)
        self[key] = component

        return component

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key.lower())
        except KeyError:
            raise KeyError(key)

    def __getattr__(self, key):
        try:
            return dict.__getitem__(self, key.lower())
        except KeyError:
            raise AttributeError(key)
