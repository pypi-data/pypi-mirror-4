threadmap
=========

:Author: Y.Okamura

Multi thread map

Example
-------

>>> import threadmap
>>> import time
>>> def testfun(a):
...     print 'start', a
...     time.sleep(1)
...     print 'finish', a
...     return a**2
... 
>>> tm = threadmap.ThreadMap()
>>> tm.map(testfun, range(10))

License
-------

GNU General Public License v3 or later
