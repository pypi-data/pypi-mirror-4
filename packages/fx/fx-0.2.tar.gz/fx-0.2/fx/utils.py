# Copyright 2012, Philip Xu <pyx@xrefactor.com>
# License: BSD New, see LICENSE for details.
"""fx.utils - implements helper functions compose and flip."""

__all__ = ['compose', 'flip']


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
