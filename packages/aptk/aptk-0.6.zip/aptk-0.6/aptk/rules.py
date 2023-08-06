#
# Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
# Published under New BSD License, see LICENSE.txt for details.
#

import re, sys, logging, time

from .util import Undef

try:
   from ctxvar import ctxget, ctx, Here, Undef
except:
   # this is for documentation
   pass

LOG_LEVEL_DEBUG = logging.DEBUG
log = logging.getLogger('aptk')
#log.setLevel(logging.ERROR)
#log.setLevel(logging.DEBUG)

PatternType = type(re.compile(''))

from .match_object import *

class NotMatched(Exception): pass

class Recursive: pass

class NonTerminal: pass


class Rule:
    '''Base class for all grammar rules.

    Objects from this class are callable.  If called there will be called
    method ``match`` with parser object as parameter.  Each Rule descendent
    has to implement its own ``match`` method.
    '''

    is_terminal  = None
    is_sigspace  = None
    recursive = None
    called       = []
    is_setting_up = False
    _start_time = 0

    def __init__(self, backtrack=True):
        self.backtrack = backtrack

    def __call__(self, P, s, start, end=None):
        '''Do debug logging for debugging grammars and call ``match`` method.

        Parameters:
            P:
                Parser object.

        Returns:
            MatchObject object.
        '''
        log_level = log.level
        if log_level <= LOG_LEVEL_DEBUG:
            self._start_time = time.time()
            self.log_debug("__called__ %s", self)

        # if current rule at same position in input is already in rule call stack, 
        # this rule fails
#        _id = (id(self), ctxget('*POS*', 0))
#        _callstack = ctx('*CALLSTACK*')
#        if _id in _callstack:
#           raise StopIteration()
#
#        ctx('*CALLSTACK*', _callstack + (_id,))
#   
        iterator = enumerate(self.possible_matches(P, s, start, end), 1)

        i = 0
        while True:
            r = Undef
            try:
                if log_level <= LOG_LEVEL_DEBUG:
                    parent = ctxget('*RULE*', '')
#                    data = self.data
#                    if isinstance(data, PatternType): data = data.pattern

                    p = start
                    self.log_debug("%30.30s %20.20s", self, repr(s[p:p+15]), indicator = '{{{ %02d'%i)

                i,r = iterator.next()

            except:
                log.debug("got exc", exc_info=1) 
                raise

            finally:
                if log_level <= LOG_LEVEL_DEBUG:
#                    data = self.data
#                    if isinstance(data, PatternType): data = data.pattern
                    self.log_debug("%30.30s => %s", self, repr(r), 
                        indicator = '}}} %02d'%i)

            if r is Undef: raise StopIteration

            yield r

        
    def log_debug(self, msg, *args, **kargs):
        '''print out a debug message.

        Parameters:
            - `msg` - a format string
            - all other parameters are parameters for format string
            - `indicator` - a special named paramter, which defaults to "...".
              This is internally used for indicating where a rule starts
              and ends.
        '''
        indi = kargs.get('indicator', '...')
        msg = msg % args
        if log.level <= LOG_LEVEL_DEBUG:
            parent = ctxget('*RULE*', '')
            log.debug("%s%s: %-20s %.6fs %s %s", self.__class__.__name__[:5], self.backtrack and "(b)" or "(r)", '('+parent[:18]+')', time.time()-self._start_time, indi, msg)

    def __repr__(self):
        data = self.data
        if isinstance(data, tuple):
            if data[1] == None: data = data[0]
        if isinstance(data, PatternType): data = data.pattern
        if isinstance(data, list): data = "[ "+', '.join([repr(d) for d in data]) + " ]"
        else: data = repr(data)
        return self.__class__.__name__ + "(" + data + ")"

    def setup(self, G, called):
        if self.is_setting_up: return

        try:
            self.is_setting_up = True

            self.rule_setup(G, called)
        finally:
            self.is_setting_up = False


    def rule_setup(self, G, calling):
        pass

    def possible_matches(self, P, s, start=0, end=None):
        r = self.match(P, s, start, end)
        if r is not None:
            yield r

    def match(self, P, s, start=0, end=None):
        '''default match, calls possible_matches and returns first 
        possible value.

        please note that you have to implement either possible_matches 
        or match in derived classes.
        '''
     
        for m in self.possible_matches(P, s, start=start, end=end):
            return m
        return None

class CustomRule(Rule):

    def __init__(self, data=None):
        self.data = data
        Rule.__init__(self, backtrack=True)

    def possible_matches(self, P, s, start=0, end=None):
        r = self.match(P, s, start, end)
        if r is not None:
            yield r


class Terminal(Rule):
    '''Terminal rules derive from this.'''

    is_terminal  = True
    recursive = None

    def __init__(self):
        Rule.__init__(self, backtrack=False)

    def possible_matches(self, P, s, start=0, end=None):
        r = self.match(P, s, start, end)
        if r is not None:
            yield r


class String(Terminal):
    '''Match a string.

    Example::
        string := "string"

    '''

    def __init__(self, string):
        Terminal.__init__(self)
        self.data = string
        self.slen = len(string)

    def __str__(self):
        return repr(self.data)

    def rfind(self, P, s, start=0, end=None):
        p = s.rfind(self.data, start, end)
        if p < 0: return None
        return MatchObject(start=p, end=p+self.slen, string=s, lexems=[])

    def match(self, P, s, start=0, end=None):
        if s.startswith(self.data, start, end):
            return MatchObject(start=start, end=start+self.slen, string=s)
           
        return None


class Sequence(Rule):
    '''Match a sequence of rules.

    This rule matches if all elements of the sequence match.

    Example::
        sequence := <first> <second> <third>

    Each lexem will be made available as a context var (prefixed
    with "="), which can be accessed in a dynamic regex::

        sequence := <first> a_regex_including_$<=first>

    If <first> matched "foo", then second rule would try to match
    "a_regex_including_foo".
    '''
    
    def __init__(self, sequence, backtrack=True):
        Rule.__init__(self, backtrack=backtrack)
        self.data = sequence

    def __str__(self):
        return " ".join([str(x) for x in self.data])

    def possible_matches(self, P, s, start, end):
        start_pos = start
        seq = self.data
        seqlen = len(seq)

        #if self.recursive:
            #
            #for i,r in enumerate(seq):
                #if self.recursive in r.called:
                    ## this  is the recursive rule
#
                #else:
                    # this is callable
                
        def create_match(k, pos, result, end):
            def match_ctx(mob):
                  if isinstance(mob, Lexem):
                    my_result = [mob]

                  else:
                    my_result = mob.lexems

                  if isinstance(mob, Lexem):
                    ctx('='+mob.name, str(mob))

                  for L in mob:
                    ctx('='+L.name, str(L))

                  match = create_match(k+1, mob.end, result + my_result, end)

                  for m in match:
                    yield m

            if k >= seqlen:
                yield MatchObject(end=pos, lexems=result, start=start_pos, string=s)

            else:
                if self.recursive in seq[k].called:
                    # this is the recursive rule, so find first terminal
                    # after recursive rule, and find last possible match
                    # in input. this marks the end of the recursive rule call.
                    #
                    rec_end = None
                    #la_start = None
#                    la_count = 2 # has to be at least 2 for sigspace rules
                    #la_i = 0
                    for j in xrange(k+1, len(seq)):
                        if not isinstance(seq[j], Rule): continue
                        if seq[j].is_sigspace: continue

                        if seq[j].is_terminal:
                            m = seq[j].rfind(P, s, pos, end)
                            if not m: raise StopIteration()

                           # if la_start is not None:
                           #     if la_start != m.start: raise StopIteration()
                           #     la_start = m.end

                            rec_end = m.start
                            break

                       # else:
                       #     break

                    self.log_debug("seq[%s]: %s", k, seq[k])

                    matches = seq[k](P, s, pos, rec_end)

                    for mob in matches:
                        self.log_debug("mob: %s", mob)

                        for r in match_ctx(mob):
                            yield r

                        self.log_debug("try next possible seq[%s]: %s", k, seq[k])

                else:
                    self.log_debug("seq[%s]: %s", k, seq[k])
                    matches = seq[k](P, s, pos, end)
                    for mob in matches:
                        self.log_debug("mob: %s", mob)

                        for r in match_ctx(mob):
                            yield r

                        self.log_debug("try next possible seq[%s]: %s", k, seq[k])


                    #except NotMatched:
                    #    if not self.backtrack:
                    #        raise StopIteration
                    #    continue

        for result in create_match(0, start_pos, [], end):
            yield result
            if not self.backtrack: break

    def rule_setup(self, G, calling):
        called = []
        is_terminal  = True
        for r in self.data:
            r.setup(G, calling)
            for c in r.called:
                if c not in called: called.append(c)
            is_terminal = is_terminal and r.is_terminal
        self.called = called

    def rfind(self, P, s, start=0, end=None):
        assert self.is_terminal

        seq = self.data

        while True:
            r = seq[0].rfind(P, s, start, end)
            if not r: return None

            # we only need the first match
            for m in self.possible_matches(P, s, r.start, end):
                return m

            end = r.start
        
    def match(self, P):
        result = []
        #pos = ctx("*POS*", Here)
        ctx("*CURRENT*", result)

        for i, rule in enumerate(self.data):
            lexed = {}

            mob = rule(P)

            if mob is None or isinstance(mob, StopParsing):
                return mob

            if isinstance(mob, Lexem):
                ctx('='+mob.name, str(mob))

            for L in mob:
                ctx('='+L.name, str(L))

            #ctx("*POS*", mob.end)

            if isinstance(mob, Lexem):
                result.append(mob)
            else:
                result.extend(mob) # iterate over lexems

        mob = MatchObject(end=ctx('*POS*'), lexems=result, start=pos)

        return mob

class Quantified(Rule):
    '''Match a rule multiple times.

    This rule matches, if quantification constraints are met.

    ============ =====================================
     Quantifier   Meaning
    ============ =====================================
     RULE*        Match RULE zero or more times
     RULE+        Match RULE one  or more times
     RULE?        Match RULE zero or one time
     RULE{A,B}    Match RULE at least A times, 
                  but no more than B times.

                  If you leave out A it defaults to 0
                  (``{,B}``), if you leave out B it
                  defaults to "more times": RULE{1,}
                  is equivalent to RULE+
    ============ =====================================
    '''
    def __init__(self, rule, quantifier, backtrack=True):
        Rule.__init__(self, backtrack=backtrack)
        if quantifier == '?':
            min, max = 0, 1
        elif quantifier == '*':
            min, max = 0, None
        elif quantifier == '+':
            min, max = 1, None
        
        elif ',' in quantifier: # {1,2}
            min, max = [ x and int(x) or 0 
                         for x in quantifier[1:-1].split(',') ]
            if max == 0: max = None
 
        else: # {1}
            i = int(quantifier[1:-1])
            min, max = i, i

        self.data = (rule, min, max)

    def __str__(self):
        d, min, max = self.data
        return str(d)+'{'+repr(min)+","+repr(max)+"}"

    def rfind(self, P, s, start=0, end=None):
        rule = self.data[0] # take quantification into account?
        for x in rule.rfind(P, s, start, end): yield x

    def possible_matches(self, P, s, start=0, end=None):
        rule, min, max = self.data

        # no backtracking yet

        i = 0

        start_pos = start
        result = []

        while True:
            # here we always are only interested in the first match
            matched = False

            for mob in rule(P, s, start, end):
                i += 1
                if isinstance(mob, Lexem):
                    result.append(mob)
                else:
                    result.extend(mob)

                matched = True
                start = mob.end

                break

            if max is not None:
                if i == max: break

            if not matched: break

        self.log_debug("result (%s): %s", i, result)
        if i >= min:
            self.log_debug("possible_matches (%s)", i)
            yield MatchObject(end=start, lexems=result, start=start_pos, string=s)
        else:
            self.log_debug("no possible_matches (%s)", i)

    def rule_setup(self, G, calling):
        called = []
        is_terminal  = True

        r = self.data[0]
        r.setup(G, calling)

        for c in r.called:
            if c not in called: called.append(c)
        self.is_terminal = r.is_terminal
        self.called = called
        
    def match(self, P):
        rule, min, max = self.data

        pos = ctx('*POS*', Here)
        i = 0
        result = []
        ctx('*CURRENT*', result)
        while True:
            mob = rule(P)
            p = ctx('*POS*')

            if mob is None or isinstance(mob, StopParsing):
                if i >= min:
                    mob = MatchObject(end=ctx('*POS*'), lexems=result, 
                              start=pos, string=s)
                else:
                    mob = None

                return mob
            else:
                i += 1
                ctx('*POS*', mob.end)

                if isinstance(mob, Lexem):
                    result.append(mob)
                else:
                    result.extend(mob)

                if max is not None:
                    if i == max:
                        mob = MatchObject(start=pos, end=ctx('*POS*'), 
                            lexems=result)
                        return mob

class Calling(Rule):

    def rule_setup(self, G, calling):
        name = self.data[0]

        if name in calling:
            self.recursive = name

            return

        called = [ name ]

        r = getattr(G, name)

        if isinstance(r, Rule):
            r.setup(G, calling + called)
            for c in r.called:
                if c not in called: called.append(c)

            self.is_terminal = r.is_terminal
        else:
            # custom rule, what to do?
            self.is_terminal = False

        self.called = called

    def match_rule(self, P, s, start=0, end=None):
        rule = self.data
        args = None
        if isinstance(rule, tuple):
            rule, args = rule

        ctx('*RULE*', rule)
        if args is None:
            mob = getattr(P.grammar, rule)(P, s, start, end)
        else:
            mob = getattr(P.grammar, rule)(P, s, start, end, args)

        if isinstance(mob, MatchObject):
            yield mob
        elif mob is None:
            pass
        else:
            for result in mob: yield result

    def rfind(self, P, s, start=0, end=None):
        name = self.data[0]
        r = getattr(P.grammar, name)
        if isinstance(r, Rule):
            return r.rfind(P, s, start, end)
        return None

class Capturing(Calling):
    '''Do a named capture.

    This matches a rule and transforms resulting MatchObject into a named
    Lexem.

    Example::
        foo := <name>
        name := some_regex
    '''

    def __init__(self, name, args=None, backtrack=True):
        Calling.__init__(self, backtrack=backtrack)
        self.data = name, args

    def __str__(self):
        name, args = self.data
        if args is None:
            return "<"+name+">"
        else:
            return "<"+name+"{ "+' '.join([str(x) for x in args])+"}>"

    def possible_matches(self, P, s, start=0, end=None):
        name = self.data[0]

        for mob in self.match_rule(P, s, start, end):
            self.log_debug("capture: %s, %s", name, mob)

            if isinstance(mob, Lexem):
                mob = MatchObject(mob=mob, lexems=[mob])

            yield P.lex(mob, name)

            if not self.backtrack: break
        self.log_debug("done capture: %s", name)


class NonCapturing(Calling):
    '''Match a rule without capturing results.

    Example::
        foo := <.name>
        name := some_regex

    '''
    def __init__(self, rule, args=None, backtrack=True):
        Calling.__init__(self, backtrack=backtrack)
        self.data = (rule, args)

    def __str__(self):
        name, args = self.data
        if args is None:
            return "<."+name+">"
        else:
            return "<."+name+"{ "+' '.join([str(x) for x in args])+"}>"

    def possible_matches(self, P, s, start=0, end=None):
        for mob in self.match_rule(P, s, start, end):
            yield mob
            if not self.backtrack: break



class Alternative(Rule):
    '''Match alternative rules.

    This matches if the first alternative matches and returns its result.

    Example::
        foo := first | second

    '''

    def __init__(self, alternatives, backtrack=True):
        Rule.__init__(self, backtrack=backtrack)
        self.data = alternatives

    def __str__(self):
        return " | ".join([str(x) for x in self.data])

    def rfind(self, P, s, start=0, end=None):
        assert self.is_terminal
        result = None
        for a in self.data:
            m = a.rfind(P, s, start, end)
            if m is None: continue
            if not result:
                result = m ; continue

            if m.start > result.start: result = m.start

        return result
        

    def possible_matches(self, P, s, start=0, end=None):
        '''yield possible matches'''

        self.log_debug("next alt: %s", self)
        matched = False
        for i,alt in enumerate(self.data):
            #self.log_debug("try %s: %s" % (i, alt))
            matches = alt(P, s, start, end) 

            for mob in matches:
                matched = True
                self.log_debug("got %s", mob)
                yield mob
                if not self.backtrack: break
                if isinstance(alt, Terminal): break

            #self.log_debug("done %s: %s" % (i, alt))
            if matched and not self.backtrack: break

    def rule_setup(self, G, calling):
        called = []

        is_terminal  = True
        for r in self.data:

            r.setup(G, calling)
            for c in r.called:
                if c not in called: called.append(c)
            is_terminal = is_terminal and r.is_terminal

        self.called = called
                

CTXVAR_RE = re.compile(r'\$<[^>]*>')
class Regex(Terminal):
    '''match a regex.

    '''
    def __init__(self, regex):
        Terminal.__init__(self)
        if isinstance(regex, basestring):
            if '$<' not in regex:
                regex = re.compile(regex)

        self.data = regex

    def __str__(self):
        r = self.data
        if not isinstance(r, basestring):
            r = r.pattern
        return "/"+r+"/"

    def rfind(self, P, s, start=0, end=None):
        args = [ s, start ]
        if end is not None: args.append(end)

        m = [x for x in self.regex().finditer(*args)][-1]
        if m is None: return m
        return MatchObject(match=m, lexems=[])
        
    def regex(self):
        regex = self.data
        if not isinstance(regex, basestring):
            return regex
        else:
            regex = CTXVAR_RE.sub(
                lambda m: re.escape(str(ctx(m.group(0)[2:-1]))), regex)

            self.log_debug("%30.30s (dyn)", repr(regex))

            return re.compile(regex)

    def match(self, P, s, start=0, end=None):
        p = start

        args = [ s, start ]
        if end is not None: args.append(end)

        m = self.regex().match(*args)

        if m is None: return m

        d = m.groupdict()

        lexems = []
        if d:
            items = m.re.groupindex.items()
            keys = [x[0] for x in sorted(items, key=lambda y: y[1])]
            for k in keys: 
                name = k
                v = d[k]
                if (
                    name.startswith('N_') or 
                    name.startswith('Q_')
                   ):
                    astmap = {'N_': '_number', 'Q_': '_quoted'}
                    x = name[:2]
                    name = name[2:]

                    if name not in self.ACTIONS:
                        self.ACTIONS[name] = astmap[x]

                mob = MatchObject(string=s, start=m.start(k), end=m.end(k))

                lexems.append(P.lex(mob, name))
                    
        return MatchObject(match=m, lexems=lexems)

