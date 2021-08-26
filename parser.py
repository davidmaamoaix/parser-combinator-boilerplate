class Curry:

    def __init__(self, f, params=[], length=None):
        self.f = f
        self.len = f.__code__.co_argcount if length is None else length
        self.params = params

    def __call__(self, *a):
        p = [*self.params, *a]
        return self.f(*p) if len(p) >= self.len else Curry(self.f, p, self.len)


class Functor:

    def __rmatmul__(self, f): # fmap
        raise NotImplementedError


class Applicative(Functor):

    @classmethod
    def _pure(cls, a):
        if cls == Applicative:
            raise NotImplementedError

        return cls._pure(a)

    def __mul__(self, a): # apply
        raise NotImplementedError

    def __lshift__(self, other):
        return lift2A(const)(self)(other)

    def __rshift__(self, other):
        return lift2A(flip(const))(self)(other)


class Alternative(Applicative):

    @classmethod
    def _empty(cls):
        if cls == Alternative:
            raise NotImplementedError

        return cls._empty()

    def __or__(self, other):
        raise NotImplementedError


class Monad(Functor):

    @classmethod
    def _ret(cls, a):
        raise NotImplementedError

    def __xor__(self, f): # bind
        raise NotImplementedError


class Parser(Alternative, Monad):

    def __init__(self, f):
        self.p = f

    def __rmatmul__(self, f):

        def inner(s):
            return [(r, curry(f)(v)) for (r, v) in self.p(s)]

        return Parser(inner)

    @classmethod
    def _pure(cls, a):
        return Parser(lambda s, a=a: [(s, a)])

    def __mul__(self, a):

        def inner(s):
            return sum((
                [(ra, vf(va)) for (ra, va) in a.p(rf)]
                for (rf, vf) in self.p(s)), []
            )

        return Parser(inner)

    @classmethod
    def _empty(cls):
        return Parser(lambda s: [])

    def __or__(self, other):

        def inner(s):
            return self.p(s) + other.p(s)

        return Parser(inner)

    @classmethod
    def _ret(cls, a):
        return pure(a)

    def __xor__(self, f): # bind

        def inner(s):
            return sum((f(v).p(r) for (r, v) in self.p(s)), [])

        return Parser(inner)


def many(p):
    def inner(s):
        return sum((
            (lambda result:
                [(ro, [vo])] if not result else [(ro, [vo])] + [(ri, [vo, *vi])
                for (ri, vi) in result]
            )(inner(ro))
            for (ro, vo) in p.p(s)
        ), [])

    return Parser(inner) | pure([])


def string(s):
    return pure('') if not s else add @ char(s[0]) * string(s[1 :])


curry = lambda x, l=None: x if isinstance(x, Curry) else Curry(x, [], l)
lift2A = curry(lambda f, fa, fb: f @ fa * fb)
flip = curry(lambda f, a, b: f(b, a))
fmap = curry(lambda f, a: f @ a)
add = curry(lambda a, b: a + b)
prepend = curry(lambda a, b: [a, *b])
compose = curry(lambda f, g: lambda x: f(g(x)))
eq = curry(lambda a, b: a == b)
const = curry(lambda a, _: a)
tup = curry(lambda a, b: (a, b))
join = curry(''.join, 1)
debug = curry(print, 1)

empty = Parser._empty()
pure = Parser._pure
wild = Parser(lambda s: [] if not s else [(s[1 :], s[0])])
pred = lambda p, w=wild: w ^ (lambda c: pure(c) if p(c) else empty)
char = lambda comp: pred(eq(comp))
any_of = lambda x: pred(lambda c: c in x)
none_of = lambda x: pred(lambda c: c not in x)
between = curry(lambda start, end, p: start >> p << end)
many1 = lambda p: p ^ (lambda x: many(p) ^ (lambda xs: pure([x, *xs])))
sep1 = curry(
    lambda p, s: p ^ (lambda x: many(s >> p) ^ (lambda xs: pure([x, *xs])))
)
sep = curry(lambda p, s: sep1(p, s) | pure([]))
spaces = many(any_of('\n\t '))
wwrap = lambda p: spaces >> p << spaces
digit = any_of('1234567890')
end = Parser(lambda s: [('', '')] if not s else [])