#
# Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
# Published under New BSD License, see LICENSE.txt for details.
#
from .parser import Parser
from .actions import ParseActions
from .match_object import MatchObject

import unittest, difflib, re
differ = difflib.Differ()

class GrammarTest:
    '''simple class to save testdata'''
    OP_MAP = {
        '~~': 'assertTokens',
        '!~': 'assertNotMatches',
        '=~': 'assertEquals',
    }

    def __init__(self, name, op, pos, input, actions, expected, skip=None, debug=False):
        self.name = name
        self.op = op
        self.actions = actions
        self.input = input
        self.expected = expected
        self.skip = skip
        self.debug = debug

    def __repr__(self):
        return self.__class__.__name__+\
            '( %(name)s, %(op)s, %(actions)s, %(input)s, %(expected)s )' % dict( (k,repr(v)) for k,v in self.__dict__.items())

    def check(self, output):
        getattr(self, self.OP_MAP[self.op])(output, self.expected)

    def assertTokens(self, input, expected):
        input = repr(input)
        if isinstance(input, basestring):
            in_tokens = input.split()
        if isinstance(expected, basestring):
            expected = expected.split()

        if expected is None:
            assert input, "input is not valid"
            return

        assert in_tokens == expected, ("\n" +
            '\n'.join(differ.compare(in_tokens, expected)) + "\n\n")
           
        #''.join(r)

        #for i, t in enumerate(in_tokens):
            #s = i - 5 
            #if s < 0: s = 0
#
            #assert t == expected[i], ("\n"
             #"input   : %s\n"
             #"input   : ... %s ...\n"
             #"expected: ... %s ...\n" % 
             #(input, ' '.join(in_tokens[s:i+3]), ' '.join(expected[s:i+3])))

    def assertEquals(self, input, expected):
        inp = str(input)
        exp = str(expected)

        assert str(input) == str(expected), ("\n"
            + '\n'.join(differ.compare(inp.splitlines(0), exp.splitlines(0)))
            + "\n\n")

    def assertNotMatches(self, input, expected):
        assert input is None, "matched! %s" % input

    def __call__(self, grammar):
        if self.debug:
            import logging
            l = logging.getLogger('aptk')
            level = l.level
            l.setLevel(logging.DEBUG)

        self.runTest(grammar)
            
        if self.debug:
            l.setLevel(level)
        

class GrammarTestCase(unittest.TestCase):
    '''A TestCase for Grammar'''

    def __init__(self, name, grammar_test, grammar):
        self.name = name
        self.grammar_test = grammar_test
        self.grammar = grammar
        unittest.TestCase.__init__(self)

    def shortDescription(self):
        return self.name

    def assertEquals(self, input, expected):
        assert input == expected

    def assertTokens(self, input, expected):
        assert input == expected.strip().split

    def runTest(self):
        if self.grammar_test.skip:
            reason = self.grammar_test.skip
            if not isinstance(reason, basestring) or not reason:
                reason = "no reason"
            raise unittest.SkipTest(reason)

        self.grammar_test(self.grammar)


class TokenTest(GrammarTest):
    '''name specifies a token'''

    def runTest(self, grammar):
        m = re.match(grammar._TOKENS_[self.name], self.input)
        if m is not None:
            mob = MatchObject(match=m)
        else:
            mob = None

        self.check(mob)


class RuleTest(GrammarTest):
    '''name specifies a rule'''

    def runTest(self, grammar):
        P = Parser(grammar, self.actions)
        mob = P.parse(self.input, rule=self.name)
        if self.actions is None:
            self.check(mob)
        else:
            self.check(mob.ast)

def generate_testsuite(grammar, suite=None, patterns=None):
    '''gets a grammar class and maybe a suite'''

    names = {}
    if suite is None:
        suite = unittest.TestSuite()
    for t in grammar._TESTS_:
        name = grammar.__name__ + '::' + t.name
        if name not in names: names[name] = 0
        names[name] += 1
        name = "%s:%02d" % (name, names[name])

        desc = t.input
        if '\n' in desc:
            desc = repr(desc)[:60]
            if len(desc) == 60: desc += "..."

        if patterns is not None:
           for p in patterns:
               if re.search(p, name):
                   suite.addTest(GrammarTestCase("%s %s %s" % (name, t.op, desc), t, grammar))
        else:
           suite.addTest(GrammarTestCase("%s %s %s" % (name, t.op, desc), t, grammar))

    return suite


def test(*grammar):
    suite = unittest.TestSuite()

    class grammar_test_main(unittest.main):
         def createTests(self):
             for g in grammar:
                 self.test = generate_testsuite(grammar=g, suite=suite)

    import sys
    argv = list(sys.argv)
    if '-d' in argv:
        import rules
        rules.log.setLevel(rules.LOG_LEVEL_DEBUG)
        argv.remove('-d')

    grammar_test_main(argv=argv)
             

    

#def generate_methods(grammar):
    #def _test_method(self):
        
    
