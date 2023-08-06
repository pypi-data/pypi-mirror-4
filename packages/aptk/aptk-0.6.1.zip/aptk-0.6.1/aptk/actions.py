# vim: set fileencoding=utf-8
#
# Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
# Published under New BSD License, see LICENSE.txt for details.
#
r'''
aptk.actions - Parse Actions
============================

.. grammar off
.. highlight:: aptk

Parse Actions are used to create an abstract syntax tree from your parse
tree.

Parse Actions are expected to be attributes of the parse-actions object
passed to :py:class:`Parser`. This can be an object of a class derived
from :py:class:`ParseActions`, but can be also a module with a collection
of functions.


Parse-Action Callables
----------------------

A parse-action is called from parser with two parameters:

* `parser` - current :py:class:`Parser` object
* `lex` - current :py:class:`Lexem` object

Whatever the parse-action returns will be then written into the ``ast``
attribute of the :py:class:`Lexem` object.


Connecting Parse-Actions to Rules
---------------------------------

The parser calls a parse-action for each captured match object, which is
represented by a :py:class:`Lexem` object:

* If there is defined a parse-action in the matching rule, it is called. 
  In following rule there would be called parse-action "some_action", 
  if you captured something using :rule:`<some-rule>`::

     some-rule  some_action=  "some text"

  You can map shortcuts to actions::

     :parse-action-map
         "$" => other_action

     other-rule $= "other text"

  In this case there would be called parse-action "other_action", if you
  captured "other text" with :rule:`<other-rule>`.

* If there is not defined a parse-action in matching rule, it is tried to
  find following parse-actions if :rule:`<my_rule>` was matched:

  * ``my_rule``
  * ``make_my_rule``
  * ``got_my_rule``

* If no parse-action found, there is nothing done


Pairs
-----

Setting an ast to a pair `(name, result)`, where `name` is the rule's name
and `result` is result from parse-action, can be achieved with following 
syntax::

    paired  action=>  <some> <rule>

If you append a ">" to your operator and you define an action for your rule
the ast of the capture of :rule:`<paired>` will be the pair 
`(paired, «result of action()»)`.

.. highlight:: py

Example
-------

    >>> from aptk import *
    >>> 
    >>> class DashArithmeticGrammar(Grammar):
    ...    r"""Simple grammar for addition and substraction.
    ... 
    ...    dash_op    <= <sum> | <difference> | <number>
    ...    sum        := <number> "+" <dash_op>
    ...    difference := <number> "-" <dash_op>
    ...    """
    >>> 
    >>> class CalculatorActions(ParseActions):
    ...    r"""inherit number from ParseActions"""
    ...    def sum(self, p, lex):
    ...        return lex[0].ast + lex[1].ast
    ...    def difference(self, p, lex):
    ...        return lex[0].ast - lex[1].ast
    >>> 
    >>> ast("1 + 3 - 2", 
    ...     grammar = DashArithmeticGrammar, 
    ...     actions = CalculatorActions())
    2
    
'''


from .util import Undef
import logging, re
log = logging.getLogger("aptk.actions")

class ParseActions:
    def _list(self, lexems, filter=None):
        if filter:
            return [ l.ast for l in lexems if l.ast is not Undef and filter(l.ast) ]
        else:
            return [ l.ast for l in lexems if l.ast is not Undef ]

    def make_list(self, p, lex):
        return self._list(lex.lexems)

    def make_pair(self, name, method):
        return lambda p, lex: (name, getattr(self, method)(p, lex))

    def make_string(self, p, lex):
        return str(lex)

    def make_number(self, p, lex):
        try:
            return int(str(lex))
        except ValueError:
            return float(str(lex))

    def make_name(self, p, lex):
        return lex.name

    PARENS = { '<':'>', '(':')', '{':'}', '[':']' }
    def make_quoted(self, p, lex):
         ls = self._list(lex.lexems)
         if ls:
             return ''.join(ls)

         s = str(lex)
 #         log.error("_smart_string(s): %s", s)

         start = s[0]
         if start in self.PARENS:
             end = self.PARENS[start]
             s = re.sub(r'\\\\|\\%s|\\%s'%(start, end), 
                     lambda m: m.group(0)[1], s[1:-1])
         else:
             end = start
             s = re.sub(r'\\\\|\\'+end, lambda m: m.group(0)[1], s[1:-1])

 #        log.error("_smart_string(s): %s", s)

         return s

    def make_dict(self, p, lex):
        try:
            _l = self._list(lex)
            return dict(_l)
        except Exception, e:
            pass

    def make_inherit(self, p, lex):
        result = self._list(lex)
        if not result: return None
        return result[0]


