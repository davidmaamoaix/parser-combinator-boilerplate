from parser import *


ab = char('a') >> char('b') >> char('c')

print(ab.p('abc'))