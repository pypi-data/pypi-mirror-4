from pydi.utils import Resolve
from pydi.exceptions import InitializationFailed


class Component(object):

    def __init__(self, cls, container=None, **kwargs):
        self.cls = cls
        self.kwargs = kwargs
        self.dependencies = []
        self.container = container

        self._shared = False
        self._instance = None

    def shared(self):
        self._shared = True

    def depends(self, cls, **kwargs):

        if type(cls) == Resolve and cls.container == None:
            cls.container = self.container

        self.dependencies.append(Component(cls, **kwargs))
        return self

    def __call__(self, **kwargs):
        if self._shared and self._instance:
            return self._instance

        args = map(lambda x: x(**x.kwargs), self.dependencies)

        target = self.cls
        try:
            obj = target(*args, **kwargs) if callable(target) else target
        except TypeError:
            raise InitializationFailed(target=target,
                                       target_args=args,
                                       target_kwargs=kwargs)

        if self._shared:
            self._instance = obj

        return obj


class Container(dict):

    def register(self, cls, name=None):
        key = cls.__name__.lower() if name is None else name
        component = Component(cls, container=self)
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
