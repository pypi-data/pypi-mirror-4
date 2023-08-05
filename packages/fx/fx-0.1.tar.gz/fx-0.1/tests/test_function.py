from fx import f

from functools import partial
from operator import add, sub, mul, truediv, neg
# wrap them all with f objects
add, sub, mul, truediv, neg = f(add), f(sub), f(mul), f(truediv), f(neg)


def test_constructor():
    # works with lambda expressions
    assert f(lambda: 42) == 42
    assert f(lambda a, b: a + b)(5, 6) == 11

    # works with buildin functions
    assert f(len)([1, 1, 2, 3, 5]) == 5
    assert f(min)(3, 2, 1) == 1

    # works with type constructors
    assert f(set)() == set()
    assert f(list)(range(3)) == [0, 1, 2]


def test_clone():
    # clone should always return a new instance.
    the_answer = f(42)
    assert the_answer is the_answer
    assert the_answer is not the_answer.clone(the_answer)
    assert the_answer is not the_answer.clone(42)
    assert the_answer.clone(the_answer) is not the_answer.clone(42)
    assert the_answer.clone(the_answer) is not the_answer.clone(the_answer)
    assert the_answer.clone(42) is not the_answer.clone(42)
    assert the_answer is the_answer


def test_partial_compatible():
    # f object works with partial functions (created by functools.partial)
    add = lambda a, b: a + b
    add_1 = partial(add, 1)
    assert add_1(2) == 3
    assert f(add_1) << 2 == 3


def test_as_identity():
    # f works as identity function on constant (non-callable)
    assert f(1) == 1
    assert f(2) != 1

    # f wraps functions and works as original functions
    assert f(sum(range(10))) == f(sum)(range(10)) == sum(f(range)(10)) == 45


def test_auto_eval():
    # equality test on invokes function wrap by f object
    # this is done by overloading operator == and != of f object
    assert f(sum(range(1, 11))) == 55

    # works in both directions
    assert 55 == f(sum(range(1, 11)))

    # even with f objects on both sides
    assert f(sum(range(1, 11))) == f(sum(range(1, 11)))

    g = f(sum(range(1, 101)))
    assert g == g.value == g() == g.call() == g.invoke() == 5050


def test_invoke():
    # f.invoke can be used to invoke the wrapped function
    res = add.invoke(1, 2)
    assert res == 3


def test_call():
    # f.call is an alias for f.invoke
    res = add.call(1, 2)
    assert res == 3


def test_value():
    # a read-only property 'value' on f object, will invoke the function as
    # well
    assert add.apply(3, 8).value == 11


def test_operator_high_cohesive_invoke():
    # f objects can be called as functions
    assert add(1, 2) == 3
    assert sub(7, 3) == 4
    assert mul(3, 7) == 21
    assert truediv(32, 4) == 8
    assert neg(1) == -1

    # works with arbitrary numbers of arguments
    assert f(bool)() is False
    assert f(max)([1]) == 1
    assert f(max)(6, 1) == 6
    assert f(max)(6, 1, 9) == 9
    assert f(max)(*range(10)) == 9

    # works with keyword arguments
    assert f(int)('10', base=16) == 16


def test_operator_low_cohesive_invoke():
    # operator positive (unary +) invokes function
    res = +(neg.apply(1))
    assert res == -1
    # both member accessing (dot .) and call operator have higher precedence
    # than this operator, so the above expression can be writte as:
    res = +neg.apply(1)
    assert res == -1


def test_apply():
    # applying arguments to f object returns partial applied functions.
    # when apply one by one, it's called currying.
    assert add.apply(1).apply(2)() == 3
    assert sub.apply(1).apply(2)() == -1

    # apply can accept more than one arguments at a time
    add_1_4 = add.apply(1, 4)
    assert add_1_4 == 5

    # supports keyword arguments as well, notice named argument 'base' is
    # supposed to be the second argument of int
    from_hex = f(int).apply(base=16)
    assert from_hex('0a') == 10
    assert from_hex('0b') == 11
    assert from_hex('0c') == 12
    assert from_hex('0d') == 13
    assert from_hex('0e') == 14
    assert from_hex('0f') == 15
    assert from_hex('10') == 16


def test_operator_high_cohesive_apply():
    # operator << on f object is overloaded, works as f.apply
    assert (add << 1 << 2) == 3
    assert (sub << 1 << 2) == -1

    # because of operator == has lower precedence than operator <<,
    # parentheses around f object can be omitted.
    assert add << 1 << 2 == 3
    assert sub << 1 << 2 == -1

    # add takes two arguments
    assert add(1, 2) == 3
    # apply one argument to it, make it a curried function that takes one
    # argument
    add_1 = add << 1
    # invokes it with one argument yields result.
    assert add_1(1) == 2
    assert add_1(2) == 3
    assert add_1(3) == 4
    # curry again, becomes a function takes no argument
    add_1_to_4 = add_1 << 4
    assert add_1_to_4() == 5
    # do it all in one expression
    assert (add << 1 << 4)() == 5

    # chaining apply
    res = list(str(n) for n in range(10))
    assert f(map) << str << range(10) | list == res

    # augmented assignments supported, too
    fm = f(map)
    fm <<= str
    fm <<= range(10)
    assert list(fm.value) == res

    # combine with other operators
    list_of_numbers = ~f(map) << range(5) | list
    add_1 = f(1 .__add__)
    assert list_of_numbers << add_1 == [1, 2, 3, 4, 5]
    times_2 = f(2 .__mul__)
    assert list_of_numbers << times_2 == [0, 2, 4, 6, 8]
    divided_by_2 = ~f(truediv) << 2
    assert list_of_numbers << divided_by_2 == [0, 0.5, 1, 1.5, 2]


def test_operator_low_cohesive_apply():
    # when using higher-order functions, parentheses might be needed
    assert f(map) << (add << 1) << range(5) | list == [1, 2, 3, 4, 5]
    # with low cohesive apply operator, parentheses can be omitted
    assert f(map) & add << 1 & range(5) | list == [1, 2, 3, 4, 5]


def test_compose():
    # make some curried functions
    add_2 = add << 2
    mul_5 = mul << 5

    # and make sure they work
    assert add_2(4) == 6
    assert mul_5(3) == 15

    # compose functions with them
    # this one multiplis input by 5, then adds 2 to the result.
    add_2_mul_5 = add_2.compose(mul_5)

    # should work
    assert add_2_mul_5(1) == 7
    assert add_2_mul_5(2) == 12
    assert add_2_mul_5(3) == 17


def test_operator_compose():
    # make some curried functions
    add_2 = add << 2
    mul_5 = mul << 5

    # and make sure they work
    assert add_2(4) == 6
    assert mul_5(3) == 15

    # operator ** can be used for function composition
    add_2_mul_5 = add_2 ** mul_5
    assert add_2_mul_5(1) == 7
    assert add_2_mul_5(2) == 12
    assert add_2_mul_5(3) == 17

    # pay attention to the order of evaluation, operator ** is
    # right-associative, this is in accordance with the function composition
    # operator in haskell, the dot operator (.)
    mul_5_add_2 = mul_5 ** add_2
    assert mul_5_add_2(1) == 15
    assert mul_5_add_2(2) == 20
    assert mul_5_add_2(3) == 25

    # one more example of right-associative
    assert neg ** abs << -1 == -1

    # function composition in action
    from itertools import count, takewhile as tw
    takewhile = f(tw)
    lt_20 = lambda n: n < 20
    reverse = lambda s: s[::-1]
    r = [19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    assert reverse ** list ** (takewhile << lt_20) ** count == r

    # result of function composition will alway be f object, which means, in a
    # chain of function composition, we can have as few as a well-placed
    # single f object to make the expression valid.  in order words, both
    # __pow__ and __rpow__ are implemented.
    assert f(list) ** f(map) << (add << 1) << range(10) == list(range(1, 11))
    assert list ** f(map) << (add << 1) << range(10) == list(range(1, 11))

    # to see it more clearly with identity function
    identity = lambda x: x
    # __pow__ in action
    assert f(identity) ** 42 == 42
    # __rpow__ in action
    assert identity ** f(42) == 42
    assert identity ** identity ** f(42) == 42
    assert identity ** identity ** identity ** f(42) == 42
    assert identity ** identity ** identity ** identity ** f(42) == 42


def test_pipe():
    one = f(1)

    res = one.pipe(add << 2).pipe(mul << 5).pipe(sub.flip << 40).pipe(neg)
    # -(40 - (1 + 2) * 5) == 25
    assert res == 25
    # equivalent operator pipe form
    res = one | add << 2 | mul << 5 | sub.flip << 40 | neg
    assert res == 25

    g = (add << 2).pipe(mul << 5).pipe(sub.flip << 40).pipe(neg)
    res = one.pipe(g)
    assert res == 25

    # equivalent operator pipe form
    g = add << 2 | mul << 5 | sub.flip << 40 | neg
    res = one | g
    assert res == 25


def test_operator_pipe():
    filter_ = f(filter)
    map_ = f(map)

    odd = lambda n: n % 2 == 1
    snd = lambda e: e[1]

    # as the name implies, it works like pipe in POSIX shell
    odd_num = range(10) | filter_ << odd | enumerate | map_ << snd | list
    assert odd_num == [1, 3, 5, 7, 9]
    # pipe is equivalent to function composition in reversed order
    fc = list ** (map_ << snd) ** enumerate ** (filter_ << odd) ** range(10)
    assert fc == odd_num


def test_reverse_apply():
    minus = f(lambda a, b: a - b)
    assert minus(2, 1) == 1
    assert minus.reverse_apply()(2, 1) == -1

    # support more than 2 arguments
    make_list = f(lambda *args: list(args))
    make_reversed_list = make_list.reverse_apply()
    assert make_list(1, 2, 3, 4, 5) == [1, 2, 3, 4, 5]
    assert make_reversed_list(1, 2, 3, 4, 5) == [5, 4, 3, 2, 1]


def test_flip():
    # f.flip, as function flip in haskell
    minus = f(lambda a, b: a - b)
    assert minus << 3 << 2 == 1

    two_minus = minus << 2
    assert two_minus << 1 == 1

    minus_two = minus.flip << 2
    assert minus_two << 1 == -1

    # flip twice yield the same function (sort of, there might be overhead
    # added in reality)
    assert minus(2, 1) == minus.flip.flip(2, 1)


def test_operator_flip():
    minus = f(lambda a, b: a - b)

    # operator ~ works as f.flip
    minus_two = ~minus << 2
    assert minus_two << 1 == -1


def test_contains():
    # for function with single value
    f_always_true = f(True)

    # works like equality check
    assert True in f_always_true
    assert False not in f_always_true

    # for function with sequence as value
    one_to_ten = range(1, 11)
    list_of_one_to_ten = f(list) << one_to_ten
    # performs membership test on value
    for i in one_to_ten:
        assert i in list_of_one_to_ten
    # make sure it did check membership instead of return True blindly
    minus_one_to_ten = range(-1, -11, -1)
    for i in minus_one_to_ten:
        assert i not in list_of_one_to_ten


def test_iter():
    one_to_ten = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # f object support iteration on it's output
    func = f(map) << 1 .__add__ << range(10) | list
    assert func.value == one_to_ten
    # func is an f object, not a list
    assert type(func) == f != list

    # f object is iterable
    res = []
    for n in func:
        res.append(n)
    assert res == one_to_ten

    # works in list comprehension
    res = [n for n in func]
    assert res == one_to_ten

    # and as arguments for functions that expect an iterator
    res = list(func)
    assert res == one_to_ten

    # works with functions return a single non-iterable value, too
    # f object will trun it into a 1-tuple
    answer = f(42)
    res = []
    for n in answer:
        res.append(n)
    assert res == [42]

    res = [n for n in answer]
    assert res == [42]

    res = list(answer)
    assert res == [42]
