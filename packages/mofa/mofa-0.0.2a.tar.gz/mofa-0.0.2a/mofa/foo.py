
import multiprocessing

class foo(object):

    def __init__(self,x=2):

        M = multiprocessing.Pool(2)
        self.x = x
        self.y = 3
        M(self.__call__,[(x,self.y) for x in range(20)])

    def __call__(x,y):
        print x,x*y

if __name__=='__main__':
    f = foo()
