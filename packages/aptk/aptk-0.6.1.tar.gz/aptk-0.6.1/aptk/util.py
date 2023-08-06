#
# Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
# Published under New BSD License, see LICENSE.txt for details.
#

class MyMetaClass(type):
    def __repr__(cls): return cls.__name__

class Undef:
    '''A Symbolic class different from `None` for use as default value in 
    a function, if `None` could be passed as value.
    '''
    __metaclass__ = MyMetaClass

