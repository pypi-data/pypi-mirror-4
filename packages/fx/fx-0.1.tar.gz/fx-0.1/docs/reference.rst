.. testsetup:: *

  from fx import compose, flip, Function


=============
API Reference
=============

.. module:: fx


Function Wrapper
================

.. autoclass:: Function

  .. automethod:: clone

  .. note::

    All methods and operators that return an instance of :class:`Function`,
    return a copy created by :meth:`clone`.
    That is, :class:`Function` object will not be changed in place by it's methods and operators.

  .. automethod:: __init__

  .. automethod:: invoke

  .. method:: call(*args, **kwargs)

    an alias to :meth:`invoke`.

  .. attribute:: value

    read-only property, with :meth:`invoke` as getter.

  .. method:: __call__(*args, **kwargs)

    an alias to :meth:`invoke`,
    implements high cohesive invoke operator ``()``.

  .. method:: __pos__

    an alias to :meth:`invoke`,
    implements low cohesive invoke operator (unary) ``+``.

  .. automethod:: compose

  .. method:: __pow__(function)

    an alias to :meth:`~Function.compose`,
    implements function composition operator ``**``.

  .. method:: __ror__(function)

    an alias to :meth:`~Function.compose`,
    implements pipe operator ``|``
    (reflected operands version).

  .. automethod:: pipe

  .. method:: __or__(function)

    an alias to :meth:`pipe`,
    implements pipe operator ``|``.

  .. method:: __rpow__(function)

    an alias to :meth:`pipe`,
    implements function composition operator ``**``
    (reflected operands version).

  .. automethod:: apply

  .. method:: __lshift__(argument)

    an alias to :meth:`apply`,
    implements high cohesive application operator ``<<``.

  .. method:: __and__(argument)

    an alias to :meth:`apply`,
    implements low cohesive application operator ``&``.

  .. automethod:: reverse_apply

  .. attribute:: flip

    read-only property,
    evaluates to the 'flipped' version of current function.

  .. method:: __invert__

    an alias to :meth:`reverse_apply`,
    implements flip operator ``~``.

  .. automethod:: __eq__

    implements operator ``==``,
    which means evaluate then check for equality.

  .. automethod:: __ne__

    implements operator ``!=``,
    which means evaluate then check for inequality.

  .. automethod:: __contains__

  .. automethod:: __iter__


Utility Functions
=================

.. autofunction:: compose
.. autofunction:: flip


Alias
=====

.. class:: f

  an alias to :class:`Function` for less typing.

Instead of using ``Function()`` every time, you can:

  >>> from fx import f
  >>> all_odd = all ** f(map) << (lambda n: n % 2)
  >>> all_odd([2, 3, 4])
  False
  >>> all_odd([7, 5, 9])
  True
