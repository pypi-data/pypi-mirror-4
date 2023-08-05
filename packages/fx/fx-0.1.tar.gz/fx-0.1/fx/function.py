# -*- coding: utf-8 -*-
# Copyright 2012, Philip Xu <pyx@xrefactor.com>
# License: BSD New, see LICENSE for details.
"""fx.function - a module with class Function and helpers compose and flip."""

__all__ = ['Function', 'compose', 'flip']

from functools import partial


def compose(f, g):
    """Function composition.

    ``compose(f, g) -> f . g``

    >>> add_2 = lambda a: a + 2
    >>> mul_5 = lambda a: a * 5
    >>> mul_5_add_2 = compose(add_2, mul_5)
    >>> mul_5_add_2(1)
    7
    >>> add_2_mul_5 = compose(mul_5, add_2)
    >>> add_2_mul_5(1)
    15
    """
    return lambda *args, **kwargs: f(g(*args, **kwargs))


def flip(f):
    """Creates a function that takes arguments in reverse order.

    ``flip(f) -> g``

    >>> minus = lambda a, b: a - b
    >>> minus(5, 3)
    2
    >>> subtract = flip(minus)
    >>> subtract(5, 3)
    -2
    >>> list(zip(range(5), range(5, 10), range(10, 15)))
    [(0, 5, 10), (1, 6, 11), (2, 7, 12), (3, 8, 13), (4, 9, 14)]
    >>> fzip = flip(zip)
    >>> list(fzip(range(5), range(5, 10), range(10, 15)))
    [(10, 5, 0), (11, 6, 1), (12, 7, 2), (13, 8, 3), (14, 9, 4)]
    """
    return lambda *args, **kwargs: f(*args[::-1], **kwargs)


class Function(object):
    """A function wrapper class.

    Implements operators for function composition, arguments flipping, partial
    application, and more.

    >>> fmap = Function(map)
    >>> double_all = fmap << 2 .__mul__ | list
    >>> double_all([1, 2, 3])
    [2, 4, 6]

    >>> mul = Function(lambda a, b: a * b)
    >>> double_all_str = fmap << str ** (mul << 2) | ' '.join
    >>> double_all_str([1, 2, 3])
    '2 4 6'
    """
    def __init__(self, function):
        """Creates a function wrapper object.

        >>> f = Function(42)
        >>> f() == 42
        True
        >>> f.value == 42
        True
        >>> f == 42
        True
        >>> g = Function(lambda a: a + 1)
        >>> g(1)
        2
        >>> g(f())
        43
        >>> succ = Function(g)
        >>> succ(0), succ(1), succ(2)
        (1, 2, 3)
        >>> times_2 = Function(2 .__mul__)
        >>> [times_2(n) for n in range(10)]
        [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
        """
        self.func = function if callable(function) else lambda: function

    @classmethod
    def clone(cls, function):
        """Creates a Function object of the same type as ``cls``."""
        func = function
        if isinstance(function, cls):
            # NOTE:
            # We are only interested in the underlying function, using it
            # instead of the whole Function object can reduce unnecessary
            # indirection with function calls.
            # This works right now, as there is no other internal state
            # (instance variables) of Function object, should there be any
            # other instance variable, it has to be copied accordingly.
            func = function.func
        return cls(func)

    def invoke(self, *args, **kwargs):
        """Invokes the wrapped function with ``args`` and ``kwargs``.

        Function invocation:

        >>> f = Function(int)
        >>> f.invoke('2')
        2

        ``call`` is an alias:

        >>> f.call('2')
        2

        ``value`` is a read-only property, when accessed, calls ``invoke``:

        >>> f.value
        0
        >>> two = f.apply('2')
        >>> two.value
        2

        High cohesive invoke operator ``()`` (a.k.a call operator):

        >>> f = Function(int)
        >>> f('2')
        2
        >>> f = Function(max)
        >>> f(1, 1, 2, 3, 5, 8)
        8

        Low cohesive invoke operator ``+`` (positive, unary plus):

        >>> f = Function(int)
        >>> two = f.apply('2')
        >>> +two
        2
        >>> +f.apply('2')
        2
        """
        return self.func(*args, **kwargs)

    # Read-only property represents function's output
    value = property(invoke)
    # Alias to invoke
    call = invoke
    # High cohesive invoke operator: ()
    __call__ = invoke
    # Low cohesive invoke operator: +
    __pos__ = invoke

    def compose(self, function):
        """Creates a Function as composition of ``function`` with ``self``.

        Function composition:

        >>> f = Function(lambda a: -a).compose(abs)
        >>> f(-1)
        -1

        Function composition operator ``**``:

        >>> f = Function(lambda a: -a) ** abs
        >>> f(-1)
        -1

        ``**`` works on either side, no need to wrap both sides:

        >>> f = Function(list) ** map << 1 .__add__
        >>> f(range(10))
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> f = list ** Function(map) << 1 .__add__
        >>> f(range(10))
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        """
        return self.clone(compose(self.invoke, self.clone(function)))

    # Function composition operator: **
    __pow__ = compose
    # Pipe operator: | (with reflected operands)
    __ror__ = compose

    def pipe(self, function):
        """Creates a Function that pipes output into ``function`` if invoked.

        Piping output:

        >>> f = Function(range).pipe(sum).pipe(int.__neg__)
        >>> f(1, 101)
        -5050

        Pipe operator ``|``:

        >>> f = Function(range) | sum | int.__neg__
        >>> f(1, 101)
        -5050

        >>> f = Function(map) << 1 .__add__ | list
        >>> f(range(10))
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        >>> sum_upto = 1 .__add__ | Function(range) << 1 | sum
        >>> sum_upto(100)
        5050
        """
        return self.clone(compose(function, self.invoke))

    # Pipe operator: |
    __or__ = pipe
    # Function composition operator: ** (with reflected operands)
    __rpow__ = pipe

    def apply(self, *args, **kwargs):
        """Creates a Function with partial function application.

        Currying:

        >>> add = Function(lambda a, b: a + b)
        >>> succ = add.apply(1)
        >>> succ(0)
        1

        High cohesive application operator ``<<``:

        >>> add_1 = add << 1
        >>> add_1(2)
        3

        Low cohesive application operator ``&``:

        >>> times = Function(lambda a, b: a * b)
        >>> f = Function(map) & times << 2 & range(8) | list
        >>> f.value
        [0, 2, 4, 6, 8, 10, 12, 14]

        Partial application:

        >>> f = Function(max) << 1 << 3 << 5 << 7 << 9 << 2 << 4 << 6 << 8
        >>> f.value
        9
        >>> f(20)
        20
        >>> f(-1)
        9

        Partial application with keyword argument:

        >>> int_from_hex = Function(int).apply(base=16)
        >>> int_from_hex('0xff')
        255
        """
        return self.clone(partial(self.invoke, *args, **kwargs))

    # High cohesive application operator: <<
    __lshift__ = apply
    # Low cohesive application operator: &
    __and__ = apply

    def reverse_apply(self):
        """Creates a Function that reversely apply positional arguments.

        Reversed positional arguments application:

        >>> minus = Function(lambda a, b: a - b)
        >>> minus(8, 5)
        3
        >>> subtract = minus.reverse_apply()
        >>> subtract(8, 5)
        -3

        ``flip`` is a read-only property for easier referencing:

        >>> minus.flip(8, 5)
        -3
        >>> minus.flip.flip(8, 5)
        3

        Flip operator ``~``

        >>> (~minus)(8, 5)
        -3
        >>> subtract = ~minus
        >>> subtract(8, 5)
        -3
        """
        return self.clone(flip(self.invoke))

    # Read-only property for easier referencing
    flip = property(reverse_apply)
    # Flip operator: ~
    __invert__ = reverse_apply

    def __eq__(self, other):
        """``self == other``

        Compares ``self.value`` with ``other`` for equality.

        >>> f = Function(sum) << [5, 4, 3, 2]
        >>> f == 14
        True
        """
        return self.value == other

    def __ne__(self, other):
        """``self != other``

        Compares ``self.value`` with ``other`` for inequality.

        >>> f = Function(sum) << [5, 4, 3, 2]
        >>> f != 14
        False
        """
        return self.value != other

    def __contains__(self, value):
        """``value in self``

        Returns True if ``value`` is in ``self.value``. If ``self.value`` is
        not iterable, equality is checked instead.

        >>> f = Function(range) << 100
        >>> 1 in f
        True
        >>> -1 in f
        False
        >>> f = Function(42)
        >>> 42 in f
        True
        >>> 43 in f
        False
        """
        output = self.value
        try:
            return value in output
        except TypeError:
            return value == output

    def __iter__(self):
        """Returns an iterator object.

        If ``self.value`` is iterable, returns ``iter(self.value)``, otherwise
        a 1-tuple with function's output will be created, and iterator of this
        tuple will be returned, so that calling ``iter()`` on a Function
        object will not fail.

        >>> f = Function(range) << 10
        >>> [n for n in f]
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> f = Function(42)
        >>> [n for n in f]
        [42]
        """
        output = self.value
        try:
            return iter(output)
        except TypeError:
            return iter((output,))
