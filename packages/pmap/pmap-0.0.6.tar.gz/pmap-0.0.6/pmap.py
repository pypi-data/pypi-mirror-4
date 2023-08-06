from threading import Thread, Semaphore

def mapper(f, arg, l, index, pool_semaphore):
        l[index]= f(arg)
        if pool_semaphore:
            pool_semaphore.release()

def pmap(f, l, limit = None):
    """A parallel version of map, that preserves ordering.
    Example:
    >>> pmap(lambda x: x*x, [1,2,3])
    [1, 4, 9]
    >>> import time
    >>> t1 = time.clock()
    >>> null = pmap(lambda x: time.sleep(1), range(10), 3)
    >>> time.clock() - t1 > 0.001
    True
    """
    if limit:
        pool_semaphore = Semaphore(limit)
    else:
        pool_semaphore = None

    pool=[]
    res = range(len(l))
    for i in range(len(l)):
        t = Thread(target = mapper, args = (f, l[i], res, i,
                                            pool_semaphore))
        pool.append(t)
        if limit:
            pool_semaphore.acquire()
        t.start()
    map (lambda x:x.join(), pool)
    return res
