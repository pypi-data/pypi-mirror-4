#
# Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
# Published under New BSD License, see LICENSE.txt for details.
#


from .util import Undef

class MatchObject:
    '''Represents a match.

    An object of this class is created from a rule, if it matches.

    Attributes:
        `string`:
            string in which current match is located

        `start`:
            start of match in `string`

        `end`:
            end of match in `string`

        `lexems`:
            list of topmost lexems of sub-matches

    '''
    def __init__(self, mob=None, start=None, end=None, 
        string=None, data=None, lexems=None, match=None):
        '''Initialize MatchObject.

        You may initialize a MatchObject in one of the following ways:

        - `mob` - pass another match-object.  Its values will be copied
          into this match-object.

        - `match` - pass a match-object resulting from a regular expression
          match.

        - `manual` - i.e. pass `start`, `end`, `string`, `lexems` manually.

        ''' 

        if match is not None:
            if string is None: string = match.string
            if start  is None: start  = match.start()
            if end    is None: end    = match.end()
            if lexems is None: lexems = [x for x in match]

        elif mob is not None:
            if string is None: string = mob.string
            if start  is None: start  = mob.start
            if end    is None: end    = mob.end
            if lexems is None: lexems = [x for x in mob]
        else:
            #if string is None: string = ctx('*INPUT*')
            #if start  is None: start  = ctx('*POS*')
            #if end    is None: end    = start
            pass

        self._string = string
        self._start  = start
        self._end    = end
        self.data    = data

        if lexems is not None:
            self.lexems = lexems
        else:
            self.lexems = []

    def __setattr__(self, name, value):
        if name == 'start':
            self.set_start(value)
        if name == 'end':
            self.set_end(value)
        if name == 'string':
            self.set_string(value)
        else:
            self.__dict__[name] = value

    def __getattr__(self, name):
        if name == 'start':
            return self._start
        if name == 'string':
            return self._string
        if name == 'end':
            return self._end
        raise AttributeError(name)

    def __iter__(self):
        for x in self.lexems:
            yield x

    def set_start(self, value):
        y = self._start
        d = x-y
        self._start += d
        self._end   += d

        for l in self.lexems:
            l.start += d

    def set_end(self, value):
        self._end = value

    def set_string(self, s):
        self._string = s

        for l in self.lexems:
            l.string = s

    def __str__(self):
        return self._string[self._start:self._end]

    def repr_lexems(self):
        return ', '.join( repr(x) for x in self.lexems )

    def __repr__(self):
        if self.lexems:
            return "MOB( %s )" % self.repr_lexems()
        else:
            return "MOB( %s )" % repr(str(self))

class StopParsing(MatchObject):
    pass

class Lexem(MatchObject):
    def __init__(self, mob, name):
        MatchObject.__init__(self, mob=mob)
        self.name = name
        self.ast = Undef

    def __repr__(self):
        if self.lexems:
            return "%s( %s )" % (self.name, self.repr_lexems())
        else:
            return "%s( %s )" %  (self.name, repr(str(self)))


