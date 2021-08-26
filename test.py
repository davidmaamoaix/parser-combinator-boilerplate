from parser_min import *


str_lit = join @ between(char('"'), char('"'), many(none_of('"\n')))
int_lit = compose(int, join) @ many1(digit)
json = fmap(curry(dict, 1))

@Parser
def obj(s):
    mid = sep(wwrap(entry), char(','))
    return json(between(char('{'), char('}'), mid)).p(s)

@Parser
def arr(s):
    return between(char('['), char(']'), sep(wwrap(value), char(','))).p(s)

value = int_lit | str_lit | obj | arr
entry = tup @ (str_lit << spaces << char(':')) * (spaces >> value)

main = wwrap(string("main()"))


print(obj.p('{  "123" : 123  ,  "test" : [2,{ "test" : {"b" :  "yay"} }] }'))
print(main.p('     main()    '))