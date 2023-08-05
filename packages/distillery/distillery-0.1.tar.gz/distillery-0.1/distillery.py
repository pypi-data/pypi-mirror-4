# -*- coding: utf-8 -*-
import weakref


#  Stores all lazy attributes for counter creation
_lazies = []


def lazy(f):
    """Stores the method creation counter and sets it as a classmethod.
    """
    _lazies.append(f)
    f.counter = len(_lazies)
    return classmethod(f)


class Distillery(object):
    """Base class for ORM dependent distilleries.
    """
    @classmethod
    def create(cls, **kwargs):
        """Inits, populates and saves a object instance.
        """
        instance = cls.init(**kwargs)
        return cls.save(instance)

    @classmethod
    def init(cls, **kwargs):
        """Inits and populate object instance.
        """
        cls._sequence = cls.get_next_sequence()

        def set(instance, attr, value):
            if not hasattr(instance, attr):
                raise AttributeError("`%s` has no attribute `%s`." \
                    % (instance.__class__.__name__, attr))
            setattr(instance, attr, value)

        instance = cls.__model__()
        #  kwargs
        for key in kwargs:
            set(instance, key, kwargs.get(key))

        def get_counter((k, m)):
            return m.counter if hasattr(m, 'counter') else 0

        #  Class members
        #  Sets basic attributes then lazy ones by creation order
        for key, member in sorted([(k, getattr(cls, k)) for k in dir(cls)],
                key=get_counter):
            if not key in Distillery.__dict__ and not key.startswith('_') \
                    and not key in kwargs:
                if callable(member):
                    value = member(instance, cls._sequence)
                else:
                    value = member
                set(instance, key, value)
        return instance

    @classmethod
    def save(cls, instance):
        """Saves given object instance.
        """
        raise NotImplementedError()

    @classmethod
    def get_next_sequence(cls):
        """Returns the next sequence value for lazies.
        """
        if not hasattr(cls, '_sequence'):
            return 0
        return cls._sequence + 1


class SetMeta(type):
    """Adds a `_set_class` property to all fixtures class in a set.
    """
    def __new__(meta, name, bases, dict_):
        new = type.__new__(meta, name, bases, dict_)
        for key in dict_:
            if not key.startswith('_'):
                setattr(getattr(new, key), '_set_class', new)
        return new


class Set(object):
    """Fixtures dataset.
    """
    __metaclass__ = SetMeta
    _instances = {}

    def __new__(cls, *args, **kwargs):
        """Creates new `cls` instance or return the existing one.
        """
        if Set._instances.get(cls.__name__):
            return Set._instances.get(cls.__name__)()
        new = super(Set, cls).__new__(cls, *args, **kwargs)
        new._fixtures = {}
        new._foreign_sets = {}
        Set._instances[cls.__name__] = weakref.ref(new)
        return new

    def __init__(self, on_demand=False):
        if not hasattr(self, '__distillery__'):
            raise AttributeError('A Set must have a `__distillery__` member.')
        self._on_demand = on_demand
        if not on_demand:
            for member in dir(self):
                if not member.startswith('_'):
                    getattr(self, member)

    def __getattribute__(self, attr):
        if attr.startswith('_'):
            return super(Set, self).__getattribute__(attr)
        elif not attr in dir(self):
            raise AttributeError('Invalid fixture `%s`.' % attr)
        elif not attr in self._fixtures:
            fixture = super(Set, self).__getattribute__(attr)
            kwargs = {}
            for key in dir(fixture):
                if not key.startswith('_'):
                    kwargs[key] = self._get_member(fixture, key)
            self._fixtures[attr] = self.__distillery__.create(**kwargs)
        return self._fixtures[attr]

    def __del__(self):
        try:
            del Set._instances[self.__class__.__name__]
        except KeyError:
            pass

    @classmethod
    def _get_instance(cls, on_demand):
        if cls.__name__ in Set._instances:
            return Set._instances[cls.__name__]()
        return cls(on_demand)

    def _get_member(self, fixture, key):
        def _get_foreign(member):
            try:
                set_ =  member._set_class._get_instance(self._on_demand)
                self._foreign_sets[member._set_class.__name__] = set_
                return getattr(set_, member.__name__)
            except AttributeError:
                raise Exception('%s does not appear to be a valid fixture' \
                    % member)

        member = getattr(fixture, key)
        if hasattr(member, '_set_class'):
            member = _get_foreign(member)
        elif isinstance(member, list) or isinstance(member, tuple):
            member = [_get_foreign(m) for m in member]

        return member


class DjangoDistillery(Distillery):
    @classmethod
    def save(cls, instance):
        instance.save()
        return instance


class SQLAlchemyDistillery(Distillery):
    @classmethod
    def save(cls, instance):
        cls.__session__.add(instance)
        cls.__session__.commit()
        return instance
