#
# Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
# Published under New BSD License, see LICENSE.txt for details.
#


import unittest, sys, re

from aptk import BaseGrammar, Grammar, compile, parse

def create_grammar_test(inp, outp):
    def _test_method(self):
        G = compile(inp).values()[0]
        self.assertEquals( repr(G), outp, 
            "Not Equal:\n>>>>>>>\n%s\n=======\n%s<<<<<<<"%(repr(G), outp))
    return _test_method

def create_parser_test(inp, s, outp):
    def _test_method(self):
        G = compile(inp).values()[0]
        #G = BaseGrammar(inp).compile()
        #G = compile(inp)
        m = parse(s, G)
        self.assertEquals( repr(m), outp, 
            "Not Equal:\n>>>>>>>\n%s\n=======\n%s<<<<<<<"%(repr(m), outp))
    return _test_method


GRAMMAR_TESTS = r'''
=== regex_01
    :grammar regex_01 extends aptk.BaseGrammar
    START := hello\x20world
---
    regex_01(
      START = Regex('hello\\x20world'), # START
    )
...

=== sequence_01
    :grammar sequence_01 extends aptk.BaseGrammar
    START := A B C
---
    sequence_01(
      START = Sequence([ Regex('A'), Regex('B'), Regex('C') ]), # START
    )
...


=== sequence_02
    :grammar sequence_02 extends aptk.BaseGrammar
    START := <indent> [^\s][^\n]*\n ((?m)^$<=indent>[^\s][^\n]*\n)*
    # comment
    indent := [\x20\t]*
---
    sequence_02(
      START = Sequence([ Capturing('indent'), Regex('[^\\s][^\\n]*\\n'), Regex('((?m)^$<=indent>[^\\s][^\\n]*\\n)*') ]), # START
      indent = Regex('[\\x20\\t]*'),
    )
...

=== rules_01
    :grammar rules_01 extends aptk.BaseGrammar

    first  = A
    second = [abc]
    third  = [^some]more(?:complex)(?:to|ken)
    fourth = \x20
    fifth  = \n

    START := <capturing> <.non-capturing>
    capturing := some-regex{4,12}
    non-capturing := {first}?
                   | {second}*
                   | {third}+
                   | {fourth}{,4}{fifth}{3,}
    some-rule := <one>{4,12} <two>{,3} <three>{4,}
    one       := a
    two       := b
    three     := b
--- 
    rules_01(
      START = Sequence([ Capturing('capturing'), NonCapturing('non-capturing') ]), # START
      capturing = Regex('some-regex{4,12}'),
      non-capturing = Alternative([ Regex('A?'), Regex('[abc]*'), Regex('(?:[^some]more(?:complex)(?:to|ken))+'), Regex('\\x20{,4}\\n{3,}') ]),
      one = Regex('a'),
      some-rule = Sequence([ Quantified((Capturing('one'), 4, 12)), Quantified((Capturing('two'), 0, 3)), Quantified((Capturing('three'), 4, None)) ]),
      three = Regex('b'),
      two = Regex('b'),
      _TOKENS_ = {
        'second': '[abc]'
        'fifth': '\\n'
        'fourth': '\\x20'
        'third': '[^some]more(?:complex)(?:to|ken)'
        'first': 'A'
      },
    )
...

=== test_01
    :grammar test_01 extends aptk.BaseGrammar
    first = a+
    {first} ~~ "aaa"  -> mob
    rule := value
    <rule> ~~ "value" -> x
    <rule> !~ "foo"   -> y
---
    test_01(
      rule = Regex('value'), # START
      _TOKENS_ = {
        'first': 'a+'
      },
      _TESTS_ = [
        TokenTest( 'first', '~~', None, 'aaa', 'mob' )
        RuleTest( 'rule', '~~', None, 'value', 'x' )
        RuleTest( 'rule', '!~', None, 'foo', 'y' )
      ],
    )
...


'''

PARSER_TESTS = r'''
=== parse_01
    :grammar G
    START := hello\x20world
--- hello world x
--- START( 'hello world' )
...

Following test shall illustrate references

=== parse_02
    :grammar G
    START  := <indent> <line> [ (?m)^$<=indent> <line> ]*
    line   := [^\s][^\n]*\n
    indent := [\x20\t]*
---
        This
        is indented
--- START( indent( '    ' ), line( 'This\n' ), line( 'is indented\n' ) )
...

'''



def create_tests(suite, testcases, testcreator):
    i = None

    from __main__ import test_patterns

    for line in testcases.splitlines(1):
        if line.startswith('=== '):
            test = [ line[4:].strip() ]
            i = 1 ; continue
        if line.startswith('---'):
            i += 1 ;
            if line != '---\n':
                test.append(line[4:].strip())
            continue
        if line.startswith('...'):
            i = None
            if test_patterns is not None:
                for p in test_patterns:
                    if re.search(p, test[0]):
                        suite.addTest(testcreator(*test))
            else:
                suite.addTest(testcreator(*test))

            continue
        if i is not None:
            if i == len(test):
                test.append("")
            test[i] += line[4:]

def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()

    class GrammarTestFixture(unittest.TestCase):
      def __init__(self, name, input, expected):
        unittest.TestCase.__init__(self)
        self.name = name
        self.input = input
        self.expected = expected

      def shortDescription(self):
        return self.name

      def runTest(self):
        inp = self.input
        outp = self.expected
        G = compile(inp).values()[0]
        self.assertEquals( repr(G), outp, 
            "Not Equal:\n>>>>>>>\n%s\n=======\n%s<<<<<<<"%(repr(G), outp))

    class ParserTestFixture(GrammarTestFixture):
      def __init__(self, name, input, s, expected):
          GrammarTestFixture.__init__(self, name, input, expected)
          self.s = s

      def runTest(self):
        inp = self.input
        outp = self.expected
        G = compile(inp).values()[0]
        #G = BaseGrammar(inp).compile()
        #G = compile(inp)
        m = parse(self.s, G)
        self.assertEquals( repr(m), outp, 
            "Not Equal:\n>>>>>>>\n%s\n=======\n%s<<<<<<<"%(repr(m), outp))

    create_tests(suite, GRAMMAR_TESTS, GrammarTestFixture)
    create_tests(suite, PARSER_TESTS, ParserTestFixture)
    return suite

if __name__ == '__main__':
    from unittest import main
    main()       

        
