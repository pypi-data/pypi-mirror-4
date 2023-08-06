#
# Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
# Published under New BSD License, see LICENSE.txt for details.
#

from aptk import compile, generate_testsuite, Grammar
from unittest import TestSuite
import os

class GrammarSigSpaceTest(Grammar):
    '''A grammar to test sigspace flag.

    Turn 
    '''


def load_tests(loader, tests, pattern):
    filename = os.path.join(os.path.dirname(__file__), '..', 'README.txt')
    with open(filename, 'rb') as f:
        grammars = compile(f,type='sphinx')

    suite = TestSuite()
    for n,g in grammars.items():
       generate_testsuite(g, suite)

    return suite

if 0:
    #from aptk import grammar_test_loader
    load_tests = grammar_test_loader( open(filename, 'rb'), 'foo.bar.Grammar', AnotherGrammar )

if __name__ == '__main__':
    from unittest import main
    main()
