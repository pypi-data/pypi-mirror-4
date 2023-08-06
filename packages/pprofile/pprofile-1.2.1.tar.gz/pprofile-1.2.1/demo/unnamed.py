#!/usr/bin/env python
import time

foo = lambda: None
bar = lambda: time.sleep(1)

foo()
bar()

gen1 = (x for x in xrange(1000))
gen2 = (y for y in xrange(10))
for _ in gen1:
    pass
for _ in gen2:
    pass
