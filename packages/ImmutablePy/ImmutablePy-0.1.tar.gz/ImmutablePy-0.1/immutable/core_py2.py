import abc
import collections
import itertools
import types

#
# The metaclass is meant to be used only once, for defining the class
# Immutable. Its role is to rename the __init__ method and to prevent
# subclasses of Immutable to redefine mutation methods.
#
class ImmutableMeta(abc.ABCMeta):

    def __new__(mcls, name, bases, namespace):
        if name != 'Immutable' or bases != (object,) \
               or namespace['__module__'] != mcls.__module__:
            if '__init__' in namespace:
                init_method = namespace['__init__']
                def init_wrapper(self, *args, **kwargs):
                    self.__init_caller__(init_method, *args, **kwargs)
                namespace['__init__'] = init_wrapper
            for methodname in ['__setattr__', '__delattr__',
                               '__setitem__', '__delitem__']:
                if methodname in namespace:
                    raise TypeError("method %s not allowed " % methodname +
                                    "in an immutable type")
        cls = super(ImmutableMeta, mcls).__new__(mcls, name, bases, namespace)
        return cls

#
# Immutable is an abstract base class for immutable Python objects.
# It allows assignments to attributes only inside __init__, and verifies
# that all attribute values are themselves immutable.
#
class Immutable(object):
    __metaclass__ = ImmutableMeta

    __locked = False
    __init_nesting = 0

    def __init_caller__(self, method, *args, **kwargs):
        if self.__locked:
            raise ValueError("immutable object already initialized")
        try:
            if method is not None:
                self.__init_nesting += 1
                method(self, *args, **kwargs)
                self.__init_nesting -= 1
            if self.__init_nesting == 0:
                for attr, value in  self.__dict__.iteritems():
                    if not isinstance(value, Immutable):
                        raise TypeError("value of attribute %s not immutable"
                                        % attr)
        finally:
            if self.__init_nesting == 0:
                self.__locked = True

    def __init__(self):
        self.__init_caller__(None)

    def __setattr__(self, *args):
        if self.__locked:
            raise TypeError("immutable instances cannot be modified")
        object.__setattr__(self, *args)

    def __delattr__(self, *args):
        if self.__locked:
            raise TypeError("immutable instances cannot be modified")
        object.__delattr__(self, *args)

    def __setitem__(self, *args):
        if self.__locked:
            raise TypeError("immutable instances cannot be modified")
        object.__setitem__(self, *args)

    def __delitem__(self, *args):
        if self.__locked:
            raise TypeError("immutable instances cannot be modified")
        object.__delitem__(self, *args)

    # Default implementation of equality, based on value equality
    # of all attributes.
    def __eq__(self, other):
        return self.__class__ is other.__class__ \
               and set(self.__dict__.keys()) == set(other.__dict__.keys()) \
               and all(self.__dict__[k] == other.__dict__[k]
                       for k in self.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    # Default implementation of hash
    def __hash__(self):
        return hash(tuple(self.__dict__.itervalues()))


# Standard Python types that are immutable
Immutable.register(bool)
Immutable.register(int)
Immutable.register(long)
Immutable.register(float)
Immutable.register(str)
Immutable.register(unicode)
Immutable.register(type(None))
Immutable.register(types.BuiltinFunctionType)
Immutable.register(types.FunctionType)
Immutable.register(types.BuiltinMethodType)
Immutable.register(types.MethodType)
Immutable.register(types.GeneratorType)

#
# An ImmutableTuple differs from a standard tuple in that all its elements
# must be immutable.
#
class ImmutableTuple(tuple):

    __slots__ = []

    def __init__(self, *args):
        for i, elt in enumerate(self):
            if not isinstance(elt, Immutable):
                raise TypeError("tuple element %s is not immutable" % i)

    def __add__(self, other):
        return ImmutableTuple(tuple.__add__(self, other))

    # __getslice__ is called in Python 2.x
    def __getslice__(self, start, end):
        return ImmutableTuple(tuple.__getslice__(self, start, end))

    # __getitem__ with slice argument is called in Python 3.x
    def __getitem__(self, item):
        if isinstance(item, slice):
            return ImmutableTuple(tuple.__getitem__(self, item))
        else:
            return tuple.__getitem__(self, item)

    def append(self, item):
        return self + ImmutableTuple((item,))

Immutable.register(ImmutableTuple)

#
# An ImmutableSet differs from a frozenset in that all its elements
# must be immutable.
#
class ImmutableSet(frozenset):

    __slots__ = []

    def __new__(cls, *args):
        obj = super(ImmutableSet, cls).__new__(cls, *args)
        for i, elt in enumerate(obj):
            if not isinstance(elt, Immutable):
                raise TypeError("set element %s is not immutable" % i)
        return obj

    def add(self, item):
        return ImmutableSet(itertools.chain(iter(self), (item,)))

# Add a wrapper around all built-in methods of frozenset that return sets.
def fix_method(method_name):
    method = getattr(frozenset, method_name)
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        return ImmutableSet(result)
    setattr(ImmutableSet, method_name, wrapper)
method_names = ['__' + prefix + name + '__'
                for name in ['and', 'or', 'sub', 'xor']
                for prefix in ['', 'r']] + \
               ['copy', 'difference', 'intersection',
                'symmetric_difference', 'union']
for method_name in method_names:
    fix_method(method_name)

Immutable.register(ImmutableSet)

#
# An ImmutableDict has immutable keys and values and doesn't permit any
# modifications after initialization.
#
class ImmutableDict(collections.Mapping):

    __slots__ = ['_d']
    __locked = False

    def __init__(self, *args, **kwargs):
        self._d = dict(*args, **kwargs)
        for key, value in  self._d.iteritems():
            if not isinstance(key, Immutable):
                raise TypeError("key %s is not immutable"
                                % str(key))
            if not isinstance(value, Immutable):
                raise TypeError("value for key %s is not immutable"
                                % str(key))
        __locked = True

    def __getitem__(self, item):
        return self._d[item]

    def __iter__(self):
        return iter(self._d)
    
    def __len__(self):
        return len(self._d)

    def __hash__(self):
        return hash(frozenset(self.iteritems()))

    def __setattr__(self, attr, value):
        if self.__locked:
            raise TypeError("immutable objects cannot be modified")
        object.__setattr__(self, attr, value)

    def __delattr__(self, attr):
        raise TypeError("immutable objects cannot be modified")

    def update(self, *args, **kwargs):
        d = self._d.copy()
        d.update(*args, **kwargs)
        return ImmutableDict(d)

Immutable.register(ImmutableDict)

#
# A utility function to convert nested combinations of lists, tuples,
# sets, and dictionaries to an immutable equivalent.
#
_immutable_conversion = {}

def immutable(obj):
    if isinstance(obj, Immutable):
        return obj
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return ImmutableTuple(immutable(x) for x in obj)
    elif isinstance(obj, set) or isinstance(obj, frozenset):
        return ImmutableSet(immutable(x) for x in obj)
    elif isinstance(obj, dict):
        return ImmutableDict((immutable(key), immutable(value))
                             for key, value in obj.iteritems())
    else:
        for klass, converter in _immutable_conversion.iteritems():
            if isinstance(obj, klass):
                return converter(obj)
        raise ValueError("object has no known immutable equivalent")

def register_immutable_converter(klass, converter):
    if klass in _immutable_conversion:
        raise ValueError("converter for %s already set" % str(klass))
    _immutable_conversion[klass] = converter
