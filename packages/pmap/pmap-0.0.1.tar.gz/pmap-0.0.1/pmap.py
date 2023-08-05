from threading import Thread

def mapper(f, arg, l, index):
        l[index]= f(arg)

def pmap(f, l):
    pool=[]
    res = range(len(l))
    for i in range(len(l)):
        t = Thread(target = mapper, args = (f,l[i],res,i))
        pool.append(t)
        t.start()
    map (lambda x:x.join(),pool)
    return res
