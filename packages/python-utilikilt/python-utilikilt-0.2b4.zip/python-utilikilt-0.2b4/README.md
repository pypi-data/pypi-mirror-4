Python Utilikilt
================

Python Utilikilt is a collection of utility classes and functions.

Installation
------------

Run `pip install python-utilikilt`

Classes
-------

###MixIn
Monkey patches a classes with methods from a supplied class.

###Indexable
Takes a generator (or any iterator) and makes it indexable.

```python
from python_utils.classes import Indexable

def fib():
    a, b = 0, 1
    while 1:
        yield a
        a, b = b, a + b

fib = Indexable(fib())
fib[10]  #144
fib[5]  #13
fib[4:10:2] #[8, 21, 55]
```

Decorators
----------

###retry
Decorator for retrying a function if exception occurs.

###run_async
Decorator for running a function in a seperate thread.

###memoize
Decorator for caching the result of a function so subsequent calls are returned out of cache instead of re-running the function.

Iterators
---------

###isplitter
Takes an iterator and splits it into chunks of the specified size and yields the chunks.

```python
from python_utils.iterators import isplitter

for x in isplitter(xrange(1000), 100):
    print x #[0,...,99], [100,...,199]...[900,...,999]
```

###daterange
Iterates over a range of dates stepping daily, monthly, or yearly

```python
from datetime import date
from python_utils.iterators import daterange

for date in daterange(date('2012-05-01'),
                      date('2012-05-20')):
    print date #2012-05-02, 2012-05-03...2012-05-20

for date in daterange(date('2012-05-01'),
                      date('2012-10-01'),
                      frequency='monthly'):
    print date #2012-06-01, 2012-07-01...2012-10-01

for date in daterange(date('1999-05-01'),
                      date('2009-05-01'),
                      frequency='yearly'):
    print date #2000-05-01, 2001-05-01...2009-05-01
```
