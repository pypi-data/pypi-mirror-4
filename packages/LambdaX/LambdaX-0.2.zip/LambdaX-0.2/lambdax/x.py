"A lambda replacement which is shorter, pickle-able, and cooler."

import operator

def identity(x):
    return x

class _Return(object):
    "Pickle-able!"
    def __init__(self, value):
        self._value = value

    def __call__(self, *args):
        return self._value

    def __hash__(self):
        return hash(self._value)

    def __repr__(self):
        return repr(self._value)

class _Partial(object):
    "Pickle-able!"
    def __init__(self, callable):
        self._callable = callable

    def __call__(self, *args):
        return self._callable(*args)

    def __hash__(self):
        return hash(self._callable)

    def __repr__(self):
        return repr(self._callable)

class _X(object):
    def __init__(self, func, *args_to_run):
        self.__func = func
        self.__args_to_run = tuple(args_to_run)
        self._X_compl = (_SameX,)

    def __hash__(self):
        return hash(self.__func) + hash(self.__args_to_run)

    def __getstate__(self):
        return self.__func, self.__args_to_run
    def __setstate__(self, state):
        self.__func, self.__args_to_run = state
    def __reduce__(self):
        #raise Exception("Deprecated!")
        return object.__reduce__(self)

    def __arg_wrapper(self, arg):
        return _Partial(arg) if type(arg) in self._X_compl else _Return(arg)

    def __apply_un_func(self, func ):
        return type(self)(func, _Partial(self))
    def __apply_bin_func(self, func, arg ):
        return type(self)(func, _Partial(self), self.__arg_wrapper(arg))
    def __apply_rbin_func(self, func, arg ):
        return type(self)(func, self.__arg_wrapper(arg), _Partial(self))
    def __apply_multargs_func(self, func, *args ):
        return type(self)(func, _Partial(self), *map(_Return,args))

    def __call__(self, *args):
        for arg in args:
            self = self.__func(*[x(arg) for x in self.__args_to_run])
        return self

    def __getattr__(self, attr):
        return self.__apply_bin_func( getattr, attr )

    def _(self, *args, **kwargs):
        if kwargs:
            return self.__apply_multargs_func( apply, args, kwargs)
        else:
            return self.__apply_multargs_func( apply, args )    # prevent hashing only if must

    # Containers
    def __getitem__(self, other):
        return self.__apply_bin_func( operator.getitem, other )
    def in_(self, other):
        return self.__apply_rbin_func( operator.contains, other )

    # Arith
    def __add__(self, other):
        return self.__apply_bin_func( operator.add, other )
    def __sub__(self, other):
        return self.__apply_bin_func( operator.sub, other )
    def __mul__(self, other):
        return self.__apply_bin_func( operator.mul, other )
    def __div__(self, other):
        return self.__apply_bin_func( operator.div, other )
    def __floordiv__(self, other):
        return self.__apply_bin_func( operator.floordiv, other )
    def __truediv__(self, other):
        return self.__apply_bin_func( operator.truediv, other )
    def __mod__(self, other):
        return self.__apply_bin_func( operator.mod, other )
    def __pow__(self, other):
        return self.__apply_bin_func( operator.pow, other )

    def __radd__(self, other):
        return self.__apply_rbin_func( operator.add, other )
    def __rsub__(self, other):
        return self.__apply_rbin_func( operator.sub, other )
    def __rmul__(self, other):
        return self.__apply_rbin_func( operator.mul, other )
    def __rdiv__(self, other):
        return self.__apply_rbin_func( operator.div, other )
    def __rfloordiv__(self, other):
        return self.__apply_rbin_func( operator.floordiv, other )
    def __rtruediv__(self, other):
        return self.__apply_rbin_func( operator.truediv, other )
    def __rmod__(self, other):
        return self.__apply_rbin_func( operator.mod, other )
    def __rpow__(self, other):
        return self.__apply_rbin_func( operator.pow, other )

    # bitwise
    def __and__(self, other):
        return self.__apply_bin_func( operator.and_, other )
    def __or__(self, other):
        return self.__apply_bin_func( operator.or_, other )
    def __xor__(self, other):
        return self.__apply_bin_func( operator.xor, other )

    def __rand__(self, other):
        return self.__apply_rbin_func( operator.and_, other )
    def __ror__(self, other):
        return self.__apply_rbin_func( operator.or_, other )
    def __rxor__(self, other):
        return self.__apply_rbin_func( operator.xor, other )

    def __rshift__(self, other):
        return self.__apply_bin_func( operator.rshift, other )
    def __lshift__(self, other):
        return self.__apply_bin_func( operator.lshift, other )

    # Comparison
    def __lt__(self, other):
        return self.__apply_bin_func( operator.lt, other )
    def __le__(self, other):
        return self.__apply_bin_func( operator.le, other )
    def __eq__(self, other):
        return self.__apply_bin_func( operator.eq, other )
    def __ne__(self, other):
        return self.__apply_bin_func( operator.ne, other )
    def __ge__(self, other):
        return self.__apply_bin_func( operator.ge, other )
    def __gt__(self, other):
        return self.__apply_bin_func( operator.gt, other )

    def __abs__(self):
        return self.__apply_un_func( abs )
    def __neg__(self):
        return self.__apply_un_func( operator.neg )

    # Misc
    def __str__(self):
        return self.__apply_un_func( str )
    def __repr__(self):
        if self.__func == identity and self.__args_to_run==(identity,):
            return 'X'
        return 'X:%s%s' % (self.__func.__name__, self.__args_to_run)


class _SameX(_X):
    def __init__(self, *args):
        _X.__init__(self, *args)
        self._X_compl = self._X_compl + (_X,)

X = _X(identity, identity)
SameX = _SameX(identity, identity)

