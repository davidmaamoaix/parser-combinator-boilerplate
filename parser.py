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
    def _ret(cls):
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
            result = self.p(s)

            return result if result else other.p(s)

        return inner

    @classmethod
    def _ret(cls):
        return pure(self)

    def __xor__(self, f): # bind

        def inner(s):
            return sum((f(v).p(r) for (r, v) in self.p(s)), [])

        return Parser(inner)


curry = lambda x: x if isinstance(x, Curry) else Curry(x)
lift2A = curry(lambda f, fa, fb: f @ fa * fb)
flip = curry(lambda f, a, b: f(b, a))
add = curry(lambda a, b: a + b)
eq = curry(lambda a, b: a == b)
const = curry(lambda a, _: a)

empty = Parser._empty()
pure = Parser._pure
wild = Parser(lambda s: [] if not s else [(s[1 :], s[0])])
pred = lambda p, w=wild: w ^ (lambda c: pure(c) if p(c) else empty)
char = lambda comp: pred(eq(comp))

def string(s):
    return pure('') if not s else add @ char(s[0]) * string(s[1 :])