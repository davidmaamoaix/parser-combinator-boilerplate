from parser import *


str_lit = join @ between(char('"'), char('"'), many(none_of('"\n')))
int_lit = compose(int, join) @ many1(digit)
json = fmap(wrap_native(dict))

@Parser
def obj(s):
    mid = sep(wwrap(entry), char(','))
    return json(between(char('{'), char('}'), mid)).p(s)

value = int_lit | str_lit | obj
entry = tup @ (str_lit << spaces << char(':')) * (spaces >> value)


print(obj.p('{  "123" : 123  , "456": {}}'))