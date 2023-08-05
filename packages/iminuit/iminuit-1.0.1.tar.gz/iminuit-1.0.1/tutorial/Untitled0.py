# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

print u'สวัสดี'

# <codecell>

import multiprocessing as mp
def f(x):
    print 'hello',x
pool = [mp.Process(target=f,args=(i,)) for i in range(10)]
for p in pool: p.start()
for p in pool: p.join()

# <codecell>


