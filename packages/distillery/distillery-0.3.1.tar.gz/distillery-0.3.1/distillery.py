# -*- coding: utf-8 -*-
import weakref
import types


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
            if not attr in dir(instance):
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
                member = getattr(new, key)
                if not isinstance(member, types.MethodType):
                    setattr(member, '_set_class', new)
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
            if isinstance(fixture, types.MethodType):
                #  Fixture is a callable
                instance = fixture()
                expected_class = self.__distillery__.__model__
                if not isinstance(instance, expected_class):
                    raise Exception("%s must return a %s instance" % \
                        (fixture, expected_class.__name__))
            elif issubclass(fixture, Set):
                #  Fixture is an embedded set
                instance = self._get_foreign_set_instance(fixture)
            else:
                #  Fixture is a fixture
                kwargs = {}
                for key in dir(fixture):
                    if not key.startswith('_'):
                        kwargs[key] = self._get_member(fixture, key)
                instance = self.__distillery__.create(**kwargs)
            if not issubclass(instance.__class__, Set) and \
                    hasattr(fixture, '_after_create'):
                fixture._after_create(instance)
            self._fixtures[attr] = instance
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

    def _get_foreign_set_instance(self, set_class):
        set_ = set_class._get_instance(self._on_demand)
        self._foreign_sets[set_class.__name__] = set_
        return set_

    def _get_member(self, fixture, key):
        def _get_foreign(member):
            try:
                if hasattr(member, '_set_class'):
                    set_class = member._set_class
                else:
                    set_class = member.im_class
                set_ = self._get_foreign_set_instance(set_class)
                return getattr(set_, member.__name__)
            except AttributeError:
                raise Exception('%s does not appear to be a valid fixture' \
                    % member)

        member = getattr(fixture, key)
        if isinstance(member, list) or isinstance(member, tuple):
            member = [_get_foreign(m) for m in member]
        elif callable(member):
            member = _get_foreign(member)
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
