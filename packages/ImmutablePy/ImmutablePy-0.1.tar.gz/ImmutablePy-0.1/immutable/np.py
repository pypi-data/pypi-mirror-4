#
# Immutable version of numpy.ndarray
#

import immutable
import numpy

class ImmutableNDArray(numpy.ndarray):

    def __new__(cls, *args, **kwargs):
        return numpy.ndarray.__new__(cls, *args, **kwargs)

    def __array_finalize__(self, obj):
        if obj is not None and obj.flags['WRITEABLE']:
            raise ValueError("can't make an immutable view of a mutable array")
        self.setflags(write=False)

immutable.Immutable.register(ImmutableNDArray)

def array(obj, dtype=None, copy=True, order=None, subok=False, ndmin=0):
    if isinstance(obj, ImmutableNDArray) \
       and (dtype is None or dtype == obj.dtype) \
       and ndmin < len(obj.shape):
        return obj
    a = numpy.array(obj, dtype,
                    copy=True, order=order, subok=subok, ndmin=ndmin)
    a.setflags(write=False)
    return a.view(ImmutableNDArray)

immutable.register_immutable_converter(numpy.ndarray, array)

def _new_array_wrapper(f):
    def wrapper(*args, **kwargs):
        a = f(*args, **kwargs)
        a.setflags(write=False)
        return a.view(ImmutableNDArray)
    wrapper.__doc__ = "Immutable version of:\n\n" + f.__doc__
    return wrapper

arange = _new_array_wrapper(numpy.arange)
ones = _new_array_wrapper(numpy.ones)
ones_like = _new_array_wrapper(numpy.ones_like)
zeros_like = _new_array_wrapper(numpy.zeros_like)
zeros = _new_array_wrapper(numpy.zeros)
