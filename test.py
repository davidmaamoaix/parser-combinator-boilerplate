from parser import *


str_lit = join @ between(char('"'), char('"'), many(none_of('"\n')))
int_lit = compose(int, join) @ many1(digit)
entry = lambda: tup @ str_lit * (int_lit | str_lit | obj())
obj = lambda: between(char('{'), char('}'), sep(entry(), char(',')))


print(obj().p('{}'))