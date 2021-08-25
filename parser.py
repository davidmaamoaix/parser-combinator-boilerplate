def curry(func, length: int = None):
    length = func.__code__.co_argcount if length is None else length

    def closure(p=[]):
        def inner(*a):
            params = [*p, *a]
            return func(*params) if len(params) >= length else closure(params)

        return inner

    return closure()


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

    def __irshift__(self, f): # bind
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
            result = self.parse(s)

            return result if result else other.parse(s)

        return inner

    @classmethod
    def _ret(cls):
        return pure(self)

    def __irshift__(self, f): # bind

        def inner(s):
            return sum((f(v).parse(r) for (r, v) in self.parse(s)), [])

        return Parser(inner)


lift2A = curry(lambda f, fa, fb: f @ fa * fb)
flip = curry(lambda f, a, b: f(b, a))
const = lambda a, _: a
empty = lambda t: t._empty()
pure = lambda t: t._pure()
ret = lambda t: t._ret()

pred = lambda p: Parser(
    lambda s, p=p: [(s[1 :], s[0])] if s and p(s[0]) else []
)
char = lambda comp: pred(lambda c, comp=comp: c == comp)