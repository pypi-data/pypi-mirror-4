#
# Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
# Published under New BSD License, see LICENSE.txt for details.
#

"""
aptk - API
==========

This is the major interface for the user. Usually you will only::

  from aptk import *

And then define your grammar, maybe parse-actions. This could
for example look like this::

  class AdditionGrammar(Grammar):
      r'''Parses addition-expressions.

      .. highlight aptk

      sum :- <number> "+" <sum> | <number>

      :parse-actions aptk.Sum

      <sum> ~~ 5 + 3 -Sum-> 8
      '''

  class Sum(ParseActions):
      def sum(self, P, lex):
          return sum([ x.ast for x in lex ])

For parsing a string, you can use :py:func:`parse`::

  parse_tree = parse("4 + 2", AdditionGrammar, Sum)

For convenience there is also a function :py:func:`ast`, which returns
abstract syntax-tree of a node::

  result = ast(parse_tree)

For convienece you can shortcut this with::

  result = ast("4 + 2", AdditionGrammar, Sum)


"""

from .grammar import BaseGrammar, Grammar, compile, GrammarType
from .grammar_compiler import GrammarCompiler, GrammarError
from .grammar_tester import generate_testsuite, test
from .actions import *
from .parser  import *
from .__version__ import __version__

def parse(s, grammar, actions=None, rule=None):
    '''parse `s` with given grammar and apply actions to produced lexems.'''
    P = Parser(grammar, actions)
    mob = P.parse(s, rule=rule)
    return mob

def ast(s, grammar=None, actions=None, rule=None):
    '''return ast of s if has one, else, parse s using grammar and actions and return it then'''

    if isinstance(s, MatchObject):
        return s.ast
    return parse(s, grammar, actions=actions, rule=rule).ast

__all__ = [ 'ParseActions', 'Grammar', 'parse', 'ast' ]
