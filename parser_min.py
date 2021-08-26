accum=lambda s,p:s.a[0](*p) if len(p)>=s.a[2] else Curry(s.a[0],p,s.a[2])
class Curry:
    __init__=lambda s,f,p,l=None:setattr(s,'a',
             [f,p,f.__code__.co_argcount if l is None else l])
    __call__=lambda s,*a:accum(s,[*s.a[1],*a])
curry=lambda x,l=None:x if isinstance(x,Curry) else Curry(x,[],l)
lift2A=curry(lambda f,fa,fb:f @ fa * fb)
flip=curry(lambda f,a,b:f(b,a))
fmap=curry(lambda f,a:f @ a)
add=curry(lambda a,b:a + b)
prepend=curry(lambda a,b:[a,*b])
compose=curry(lambda f,g:lambda x:f(g(x)))
eq=curry(lambda a,b:a == b)
const=curry(lambda a,_:a)
tup=curry(lambda a,b:(a,b))
join=curry(''.join,1)
debug=curry(print,1)
class Parser:
    __init__=lambda s,f:setattr(s,'p',f)
    __rmatmul__=lambda s,f:Parser(lambda x,s=s,f=f:[(r,curry(f)(v)) \
                for (r,v) in s.p(x)])
    _pure=classmethod(lambda cls,a:Parser(lambda s,a=a:[(s,a)]))
    __mul__=lambda s,a:Parser(lambda x,s=s,a=a:sum(([(ra,vf(va)) \
            for (ra,va) in a.p(rf)] for (rf,vf) in s.p(x)),[]))
    __lshift__=lambda s,o:lift2A(const)(s,o)
    __rshift__=lambda s,o:lift2A(flip(const))(s)(o)
    _empty=classmethod(lambda c:Parser(lambda s:[]))
    __or__=lambda s,o:Parser(lambda x,s=s,o=o:s.p(x)+o.p(x))
    _ret=classmethod(lambda c,a:pure(a))
    __xor__=lambda s,f:Parser(lambda x,s=s,f=f:sum((f(v).p(r) \
            for (r,v) in s.p(x)),[]))
def many(p):
    def inner(s):
        return sum(((lambda result:[(ro,[vo])] if not result else \
               [(ro,[vo])]+[(ri,[vo,*vi]) for (ri,vi) in result])\
               (inner(ro)) for (ro,vo) in p.p(s)),[])
    return Parser(inner)|pure([])
string=(lambda c:c(c))(lambda f:lambda s:pure('') \
       if not s else add@char(s[0])*f(f)(s[1:]))
empty=Parser._empty()
pure=Parser._pure
wild=Parser(lambda s:[] if not s else [(s[1:],s[0])])
pred=lambda p,w=wild:w^(lambda c:pure(c) if p(c) else empty)
char=lambda c:pred(eq(c))
any_of=lambda x:pred(lambda c:c in x)
none_of=lambda x:pred(lambda c:c not in x)
between=curry(lambda start,end,p:start>>p<<end)
many1=lambda p:p^(lambda x:many(p)^(lambda xs:pure([x,*xs])))
sep1=curry(lambda p,s:p^(lambda x:many(s>>p)^(lambda xs:pure([x,*xs]))))
sep=curry(lambda p,s:sep1(p,s)|pure([]))
spaces=many(any_of('\n\t '))
wwrap=lambda p:spaces>>p<<spaces
digit=any_of('1234567890')
end=Parser(lambda s:[('','')] if not s else [])