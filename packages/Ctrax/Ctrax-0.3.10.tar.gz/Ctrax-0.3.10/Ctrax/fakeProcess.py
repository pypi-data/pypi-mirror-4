# fakeProcess.py
# a class which pretends to be a multiprocessing.Process or threading.Thread
# JAB 7/17/12

import time


def cpu_count(): return 1


class Process:
    def __init__( self ):
        self.pid = int( round( time.time() ) )

    def start( self ):
        self.run()

    def run( self ): pass

    def join( self ): pass


class Manager:
    def dict( self ): return dict()
