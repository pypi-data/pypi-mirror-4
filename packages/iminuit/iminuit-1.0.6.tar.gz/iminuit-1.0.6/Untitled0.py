# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from iminuit import Minuit

# <codecell>

def f(x,y,z):
    return x**2+(y-x)**2+z**2

# <codecell>

m = Minuit(f)
m.migrad()

# <codecell>

m.print_matrix()

# <codecell>

x,y,s = m.mnprofile('y')

# <codecell>

plot(x,y)

# <codecell>

def f(x, y, z):
    return (x-1)**2 + (y-x)**2 + (z-2*x)**2

def make_mncontour():
    m = Minuit(f)
    m.migrad()
    m.draw_mncontour('x', 'y')
    plt.savefig('images/mncontour.png')

# <codecell>

make_mncontour()

# <codecell>

,

# <codecell>


