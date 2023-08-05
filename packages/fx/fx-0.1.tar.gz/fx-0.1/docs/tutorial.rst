.. testsetup:: *

  from fx import compose, flip, Function, f


========
Tutorial
========

  "Divide et impera."

.. currentmodule:: fx.Function


Function Creation
=================

:class:`~fx.Function` is a function/callable wrapper.

  >>> from fx import Function
  >>> length = Function(len)
  >>> length([1, 2, 3])
  3

Alias :class:`~fx.f` can be used instead,
for convenience and succinctness.

  >>> from fx import f
  >>> length = f(len)
  >>> length(range(5))
  5

When used on a non-callable object,
the newly created :class:`~fx.Function` instance
will return the same object when called as a function.

  >>> the_answer = f(42)
  >>> the_answer()
  42


Function Invocation
===================

Calling method :meth:`invoke` on a :class:`~fx.Function` instance
will invoke the wrapped function with supplied arguments.

  >>> minus = f(lambda a, b: a - b)
  >>> minus.invoke(5, 2)
  3

:meth:`call` is an alias to :meth:`invoke`.

  >>> minus.call(5, 2)
  3

:class:`~fx.Function` overloads :meth:`__call__`,
which means, instance of :class:`~fx.Function` can be invoked like a normal function.

  >>> minus(3, 2)
  1

Keyword arguments are supported as well.

  >>> minus.invoke(b=2, a=3)
  1
  >>> minus.call(b=2, a=3)
  1
  >>> minus(b=2, a=3)
  1

:class:`~fx.Function` overloads :meth:`__pos__`,
which implements unary operator ``+``,
when used, calls :meth:`invoke` with no arguments.

  >>> lst = f(list)
  >>> lst()
  []
  >>> +lst
  []
  >>> lst() == +lst
  True

:attr:`value` is a read-only property, when accessed,
calls :meth:`invoke` with no arguments.

  >>> lst(range(3))
  [0, 1, 2]
  >>> lst.value
  []


Function Application
====================

Partial function application can be done with method :meth:`apply`.

  >>> five_minus = minus.apply(5)
  >>> five_minus(2)
  3
  >>> five_minus_four = five_minus.apply(4)
  >>> five_minus_four.value
  1

:meth:`apply` accepts arbitrary arguments that wrapped function accepts.

  >>> five_minus_four = minus.apply(5, 4)
  >>> five_minus_four.value
  1
  >>> five_minus_four = minus.apply(b=4, a=5)
  >>> five_minus_four.value
  1

Operator :meth:`\<\< <__lshift__>` is overloaded as function application operator,
so the above code can be rewritten with ``<<`` like this.

  >>> five_minus = minus << 5
  >>> five_minus(2)
  3
  >>> five_minus_four = five_minus << 4
  >>> five_minus_four.value
  1
  >>> five_minus_four = minus << 5 << 4
  >>> five_minus_four.value
  1

``<<=`` works as well.

  >>> m = minus
  >>> m <<= 5
  >>> m <<= 4
  >>> m()
  1
  >>> m.value
  1

Operator :meth:`& <__and__>` is overloaded as function application operator, too.

  >>> five_minus = minus & 5
  >>> five_minus(2)
  3
  >>> five_minus_four = five_minus & 4
  >>> five_minus_four.value
  1
  >>> five_minus_four = minus & 5 & 4
  >>> five_minus_four.value
  1
  >>> m = minus
  >>> m &= 5
  >>> m &= 4
  >>> m()
  1
  >>> m.value
  1

Why do we need two different operators doing seemingly the same thing?
It is because they have different precedence, and that helps.

Consider this scenario,
we want to do something to each element in a sequence,
one way to do it is using ``map`` maps a function over this sequence.

  >>> seq = [1, 3, 5, 7, 9]
  >>> list(map(str, seq))
  ['1', '3', '5', '7', '9']

With partial function application,
even functions require more than one arguments can be used to map over a single sequence,
for example, we can double every element in this way.

  >>> mul = f(lambda a, b: a * b)
  >>> double = mul << 2
  >>> list(map(double, seq))
  [2, 6, 10, 14, 18]

Instead of hard-coding ``seq`` here,
we can use partial function application technique again,
creating a function that can be re-used over and over again.

  >>> double_all = f(map) << double
  >>> list(double_all(seq))
  [2, 6, 10, 14, 18]
  >>> list(double_all(range(5)))
  [0, 2, 4, 6, 8]
  >>> list(double_all('Hello'))
  ['HH', 'ee', 'll', 'll', 'oo']

If we don't need all these intermediate functions,
``double_all`` can be coded in one line.

  >>> double_all = f(map) << (f(lambda a, b: a * b) << 2)
  >>> list(double_all(seq))
  [2, 6, 10, 14, 18]

This is where operator :meth:`& <__and__>` comes in handy,
by using both function application operators,
we can eliminate some parentheses.

  >>> double_all = f(map) & f(lambda a, b: a * b) << 2
  >>> list(double_all(seq))
  [2, 6, 10, 14, 18]


Function Composition
====================

In the above example,
we have to wrap the result of ``map`` with a list constructor ``list``
just to make sure the result will be the same in Python 2.x and Python 3.x,
because this is one place where Python 2.x and Python 3.x differ.

  >>> double_all = f(map) & f(lambda a, b: a * b) << 2
  >>> list(double_all(seq))
  [2, 6, 10, 14, 18]

But typing all these ``list(`` and ``)`` is no fun,
there is a way to avoid this,
we can compose ``double_all`` with ``list``.

  >>> new_double_all = f(list).compose(double_all)
  >>> new_double_all(seq)
  [2, 6, 10, 14, 18]

:meth:`** <__pow__>` is the function composition operator,
keep in mind that this operator is **right-associative**,
just like the function composition operator ``(.)`` in Haskell.

  >>> new_double_all = f(list) ** double_all
  >>> new_double_all(seq)
  [2, 6, 10, 14, 18]

Because both :meth:`__pow__` and :meth:`__rpow__` are implemented,
of the two operants of operator :meth:`** <__pow__>`,
one instance of :class:`~fx.Function` will suffice to make it work.

Since ``double_all`` is already an instance of :class:`~fx.Function`,
there is no need to wrap ``list`` in a ``Function``.

  >>> new_double_all = list ** double_all
  >>> new_double_all(seq)
  [2, 6, 10, 14, 18]

With function composition operator :meth:`** <__pow__>`,
it is possible to refine ``double_all`` into a one-liner.

  >>> double_all = list ** f(map) & f(lambda a, b: a * b) << 2
  >>> double_all(seq)
  [2, 6, 10, 14, 18]

Here is a more complicated example.

  >>> from itertools import count, takewhile as tw
  >>> takewhile = f(tw)
  >>> select = f(filter)
  >>> odd = lambda n: n % 2
  >>> lt_20 = lambda n: n < 20
  >>> reverse = lambda s: s[::-1]
  >>> + reverse ** list ** (select << odd) ** (takewhile << lt_20) ** count
  [19, 17, 15, 13, 11, 9, 7, 5, 3, 1]

It's easier to read function composition expressions from right to left:

  From all whole numbers (``count``),
  we keep taking numbers as long as it is less than 20 (``takewhile << lt_20``),
  pick all odd numbers from the resulting sequence (``select << odd``),
  make it into a list (``list``),
  reverse it (``reverse``),
  and get the result (``+``).

.. warning::

  Coding in this style is fun, but tend to get hairy soon.
  *Don't Try This at Home.*


Function Pipeline
=================

When called with a callable,
method :meth:`pipe` will return an instance of :class:`~fx.Function`,
which when invoked,
will pipe the output of current function into that callable.
It works very similarly to `pipelines in Unix-like systems`_,
thus the name.

.. _pipelines in Unix-like systems: https://en.wikipedia.org/wiki/Pipeline_%28Unix%29

To put it simply,
piping the output of functions does the same thing as function composition,
just in reversed direction,
that is,
it is evaluated from left to right.

Remember the examples from last section?

  >>> double_all = f(map) & f(lambda a, b: a * b) << 2
  >>> list(double_all(seq))
  [2, 6, 10, 14, 18]
  >>> new_double_all = f(list).compose(double_all)
  >>> new_double_all(seq)
  [2, 6, 10, 14, 18]

Rewriting ``new_double_all`` with :meth:`pipe`.

  >>> new_double_all = double_all.pipe(list)
  >>> new_double_all(seq)
  [2, 6, 10, 14, 18]

Like in a Unix shell, we can use :meth:`| <__or__>` as pipe operator.

  >>> new_double_all = double_all | list
  >>> new_double_all(seq)
  [2, 6, 10, 14, 18]

Both :meth:`__or__` and :meth:`__ror__` are implemented,
so only one of the two operants needs to be an instance of :class:`~fx.Function` to make it work.

Let's take a look at the last example of last section, again.

  >>> from itertools import count, takewhile as tw
  >>> takewhile = f(tw)
  >>> select = f(filter)
  >>> odd = lambda n: n % 2
  >>> lt_20 = lambda n: n < 20
  >>> reverse = lambda s: s[::-1]
  >>> + reverse ** list ** (select << odd) ** (takewhile << lt_20) ** count
  [19, 17, 15, 13, 11, 9, 7, 5, 3, 1]

The following proves that function pipeline is equivalent to function composition in reversed direction.

  >>> s = count | (takewhile << lt_20) | (select << odd) | list | reverse
  >>> +s
  [19, 17, 15, 13, 11, 9, 7, 5, 3, 1]

Since operator :meth:`\<\< <__lshift__>` has higher precedence than :meth:`| <__or__>`,
parentheses can often be omitted.

  >>> s = count | takewhile << lt_20 | select << odd | list | reverse
  >>> +s
  [19, 17, 15, 13, 11, 9, 7, 5, 3, 1]


Reversed Function Application
=============================

It is sometimes convenient to reverse the expected order of arguments,
method :meth:`reverse_apply` helps in this situation.

It returns an instance of :class:`~fx.Function`,
which takes arguments like the original one,
but in reversed order.

  >>> minus = f(lambda a, b: a - b)
  >>> minus(2, 1)
  1
  >>> subtract = minus.reverse_apply()
  >>> subtract(2, 1)
  -1

You can get the 'flipped' function via read-only property :attr:`flip`, too.
It's named after Haskell's ``flip`` function.

  >>> subtract = minus.flip
  >>> subtract(2, 1)
  -1
  >>> minus.flip(2, 1)
  -1

Flipping a 'flipped' function again will cancel each other out.

  >>> minus(2, 1)
  1
  >>> minus.flip(2, 1)
  -1
  >>> minus.flip.flip(2, 1)
  1
  >>> minus.flip.flip.flip(2, 1)
  -1
  >>> minus.flip.flip.flip.flip(2, 1)
  1

The flip operator :meth:`~ <__invert__>` does the same thing.

  >>> minus(2, 1)
  1
  >>> (~minus)(2, 1)
  -1
  >>> (~~minus)(2, 1)
  1
  >>> (~~~minus)(2, 1)
  -1
  >>> (~~~~minus)(2, 1)
  1


Implicit Function Invocation
============================

Operators :meth:`\!= <__ne__>` and :meth:`== <__eq__>` are overloaded,
so that when using these two operators to compare anything to an instance of :class:`~fx.Function`,
it is equivalent to compare against that instance's :attr:`value`.

For example:

  >>> s = f(range) | list
  >>> (s << 3).value
  [0, 1, 2]
  >>> s << 3 == [0, 1, 2]
  True
  >>> s << 3 != [0, 1, 2]
  False
  >>> f(range) << 3 | list == [0, 1, 2]
  True
  >>> [0, 1, 2] != f(range) << 3 | list
  False
  >>> f(range) << 3 | list == f(range) << 3 | list
  True
  >>> f(range) << 3 | list != s << 3
  False

We can test if a value is in a :class:`~fx.Function`'s output,
in the form of ``value in function``.

For :class:`~fx.Function` that its :attr:`value` supports membership test operator ``in``,
(either by supporting the iterator protocol or implementing it's ``__contains__`` method),
membership testing will be delegated to its :attr:`value`.

  >>> one_to_ten = list ** f(range) << 1 << 11
  >>> 1 in one_to_ten
  True
  >>> 10 in one_to_ten
  True
  >>> 11 in one_to_ten
  False
  >>> one_to_ten.value
  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

For :class:`~fx.Function` that its :attr:`value` does not support membership test operator ``in``,
equality is checked instead.

  >>> the_answer = len ** f(range) << 42
  >>> 42 in the_answer
  True
  >>> 41 in the_answer
  False
  >>> the_answer()
  42

Instances of :class:`~fx.Function` support iterator protocol.

For :class:`~fx.Function` which its :attr:`value` is an iterable object,
iteration is delegated to that object.

  >>> one_to_three = f(range) << 1 << 4
  >>> for i in one_to_three:
  ...     print(i)
  1
  2
  3
  >>> [i * 2 for i in one_to_three]
  [2, 4, 6]

For :class:`~fx.Function` which its :attr:`value` is not an iterable,
a 1-tuple with :attr:`value` as the only element will be used to iterated over.

  >>> the_answer = f(42)
  >>> the_answer()
  42
  >>> [i for i in the_answer]
  [42]


.. warning::

  If you don't know how these features work, as described in this section,
  they might lead to surprising results and possibly cause more problems than they solve.
  *You've been warned.*


Overloaded Operators
====================

In summary, :class:`~fx.Function` overloads the following operators.

========================================= =====================================
Operator                                  Description
========================================= =====================================
``value`` :meth:`in <__contains__>` ``f`` `Check if value in f's output`_
:meth:`\!= <__ne__>`, :meth:`== <__eq__>` `Evaluates then compare`_
:meth:`| <__or__>`                        `Pipe operator`_
:meth:`& <__and__>`                       `Low cohesive application operator`_
:meth:`\<\< <__lshift__>`                 `High cohesive application operator`_
:meth:`+f <__pos__>`                      `Low cohesive invoke operator`_
:meth:`~x <__invert__>`                   `Flip operator`_
:meth:`** <__pow__>`                      `Function composition operator`_
:meth:`f(arguments...) <__call__>`        `High cohesive invoke operator`_
========================================= =====================================

.. _Check if value in f's output: `Implicit Function Invocation`_
.. _Evaluates then compare: `Implicit Function Invocation`_
.. _Pipe operator: `Function Pipeline`_
.. _Low cohesive application operator: `Function Application`_
.. _High cohesive application operator: `Function Application`_
.. _Low cohesive invoke operator: `Function Invocation`_
.. _Flip operator: `Reversed Function Application`_
.. _Function composition operator: `Function Composition`_
.. _High cohesive invoke operator: `Function Invocation`_


Utility Functions
=================

Package :mod:`fx` also provides a couple utility functions, :meth:`~fx.compose` and :meth:`~fx.flip`.

They work like :class:`~fx.Function`'s methods with the same name,
except that two functions instead of one are required because there is no ``self``.

  >>> from fx import compose
  >>> g = compose(lambda n: -n, abs)
  >>> g(-1)
  -1

  >>> from fx import flip
  >>> greater_then = lambda a, b: a > b
  >>> greater_then(1, 2)
  False
  >>> less_then = flip(greater_then)
  >>> less_then(1, 2)
  True

