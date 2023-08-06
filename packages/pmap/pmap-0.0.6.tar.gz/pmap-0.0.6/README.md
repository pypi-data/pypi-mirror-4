# PMAP

`pmap` is a multithreaded `map` functional operator that, differently from other implementations, _keeps the ordering_ of the input list.

Usage examples:


    In [1]: from pmap import pmap

    In [2]: pmap (lambda x:x*x, range(10))
    Out[2]: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]


