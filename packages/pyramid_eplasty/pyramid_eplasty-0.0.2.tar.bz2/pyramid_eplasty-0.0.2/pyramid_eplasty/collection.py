import abc
from eplasty.object.exc import NotFound
import weakref

class Collection(metaclass=abc.ABCMeta):
    """Collection wrap around object classes and allow dictionary-like
    lookup"""

    def __init__(self, **kwargs):
        for kwarg in ['class_', 'field', 'request']:
            if kwarg in kwargs:
                setattr(self, kwarg, kwargs[kwarg])
        if 'request' in kwargs:
            self.session = kwargs['request'].ep_session
    
    def mount(self, parent, name):
        self.__parent__ = weakref.proxy(parent)
        self.__name__ = name
        parent[name] = self

    def get_all(self):
        result = list(self.class_.find(session=self.session))
        for item in result:
            item.__parent__ = self
        return result

    def __getitem__(self, key):
        try:
            result = self.class_.get(
                getattr(self.class_, self.field) == key, session=self.session
            )
        except NotFound:
            raise KeyError(key)
        result.__parent__ = self
        if not (hasattr(result, '__name__') and result.__name__):
            result.__name__ = key
        return result
