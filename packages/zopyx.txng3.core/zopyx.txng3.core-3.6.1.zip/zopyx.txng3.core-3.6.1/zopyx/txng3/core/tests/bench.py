###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

# perform some BTrees benchmark for union, difference and intersection

import time
from random import choice
from BTrees.IIBTree import IISet, union, intersection, difference

def make_choice(data, per):
    data_len = len(data)
    return [choice(data) for i in range(0, data_len*float(per)/100.0)]


for max in (500, 2500, 5000, 10000, 25000, 50000, 100000):
    data = range(max)

    for p1,p2 in ((25,25), (25,50), (25,75), (25,100), (50,50), (50,75), (50,100), (75,75), (75,100), (100,100)):
        
        d1 = IISet(make_choice(data, p1))
        d2 = IISet(make_choice(data, p2))

        ts = time.time()
        union(d1, d2)
        tu = time.time() - ts

        ts = time.time()
        intersection(d1, d2)
        ti = time.time() - ts

        ts = time.time()
        difference(d1, d2)
        td = time.time() - ts
        
        print '%6d %3d:%3d  %6.6f  %6.6f %6.6f' % (max, p1, p2, tu, ti, td)


