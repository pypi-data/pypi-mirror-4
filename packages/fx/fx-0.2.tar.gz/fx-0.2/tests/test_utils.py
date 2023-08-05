from fx.utils import compose, flip


def test_compose():
    identity = lambda a: a

    # Left identity
    f = int
    g = compose(identity, f)

    assert f('42') == g('42')

    for n in range(42):  # this number is not significant here.
        assert f(n) == g(n)

    # Right identity
    f = str
    g = compose(f, identity)

    assert f(42) == g(42)

    for n in range(42):  # this number is not significant here.
        assert f(n) == g(n)

    # Associative

    # NOTE: these functions are specifically chosen, so that when composed in
    # different orders, yield different outputs.
    f = hash
    g = str
    h = type

    f1 = compose(f, compose(g, h))
    f2 = compose(compose(f, g), h)

    ns = [42, 0.5, '42', sum, f, lambda: 0]
    for n in ns:
        # make sure these functions yield different outputs when composed in
        # different order,
        assert f1(n) != compose(f, compose(h, g))(n)
        assert f2(n) != compose(f, compose(h, g))(n)
        assert f1(n) != compose(g, compose(f, h))(n)
        assert f2(n) != compose(g, compose(f, h))(n)
        assert f1(n) != compose(g, compose(h, f))(n)
        assert f2(n) != compose(g, compose(h, f))(n)
        assert f1(n) != compose(h, compose(g, f))(n)
        assert f2(n) != compose(h, compose(g, f))(n)
        assert f1(n) != compose(h, compose(f, g))(n)
        assert f2(n) != compose(h, compose(f, g))(n)
        # but compose should obey associative law.
        assert f1(n) == f2(n)


def test_flip():
    f = lambda a, b: a - b

    ns = [(2, 1), (1, 2), (0, 1), (1, 0)]
    for a, b in ns:
        assert f(a, b) != flip(f)(a, b)
        assert flip(f)(a, b) == flip(f)(a, b)
        assert flip(f)(a, b) != flip(flip(f))(a, b)
        assert flip(flip(f))(a, b) == f(a, b)
