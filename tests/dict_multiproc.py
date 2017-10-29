from multiprocessing import Process, Manager
#https://stackoverflow.com/questions/6832554/python-multiprocessing-how-do-i-share-a-dict-among-multiple-processes?rq=1
def f(d):
    d[1] += '1'
    d['2'] += 2

if __name__ == '__main__':
    manager = Manager()

    d = manager.dict()
    d[1] = '1'
    d['2'] = 2

    p1 = Process(target=f, args=(d,))
    p2 = Process(target=f, args=(d,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()

    print d

#{1: '111', '2': 6}

