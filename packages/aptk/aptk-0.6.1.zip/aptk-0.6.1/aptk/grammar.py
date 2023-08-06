#
# Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
# Published under New BSD License, see LICENSE.txt for details.
#

from .grammar_compiler import GrammarCompiler

from .util import Undef
import re, sys, os, logging, time
from .rules import *

__all__ = ['BaseGrammar', 'Grammar', 'compile']

logging.basicConfig(stream=sys.stderr)


# see http://www.voidspace.org.uk/python/articles/metaclasses.shtml
# for inheritance of metaclasses
class GrammarType(type):
    '''Metaclass_ for grammars.

    This class creates Grammar classes by merging the data of all bases
    and compiling the grammar classes' docstring (if it is not the 
    :py:class:`BaseGrammar`).

    .. _Metaclass:
       http://www.voidspace.org.uk/python/articles/metaclasses.shtml

    '''
    def __new__(meta, class_name, bases, attributes):
        # merge parent's tokens and implicit actions
        if class_name != 'BaseGrammar':
            if not bases: bases = [Grammar]

        attrs = attributes.copy()

        attrs['_START_RULE_'] = None

        for a in ("_TOKENS_", "_ACTIONS_", "_PARSE_ACTION_MAP_", 
            "_EXPECTED_", "_ARGS_OF_", "_PARSE_ACTIONS_"):
            attrs[a] = d = {}
            for b in bases:
                if hasattr(b, a):
                    d.update(getattr(b, a))
            if a in attributes:
                d.update(attributes[a])

        # we do not inherit tests from other grammars
        attrs['_TESTS_'] = []

        for a in ('_SIGSPACE_RULE_',):
          if a not in attributes:
            a = '_SIGSPACE_RULE_'

            for b in bases:
                if hasattr(b, a):
                    attrs[a] = getattr(b, a)

        #if '__name__' not in attrs: attrs['__name__'] = class_name
        if '__doc__' not in attrs: attrs['__doc__'] = ''

        g = type.__new__(meta, class_name, tuple(bases), attrs)

        #g = type(class_name, bases, attrs)

        # for some reason g has not e.g. __repr__ defined in attrs

        #type.__init__(g, class_name, bases, attrs)

        if class_name != 'BaseGrammar':
            g = compile(g)

        return g

    def __repr__(self):
        result = self.__name__+"(\n"
        for x in sorted(dir(self)):
            if x.startswith('_'): continue
            y = getattr(self, x)
            if not isinstance(y, Rule):
                result += "# %s = <Method>\n" % x
            else:
                result += "  %s = %s," % (x, repr(y))
                if x == self._START_RULE_:
                    result += " # START\n"
                else:
                    result += "\n"

        if self._TOKENS_:
            result += '  _TOKENS_ = {\n'
            for k,v in self._TOKENS_.items():
                result += "    %s: %s\n" % (repr(k), repr(v))
            result += '  },\n'

        if self._TESTS_:
            result += '  _TESTS_ = [\n'
            for x in self._TESTS_:
                result += "    %s\n" % repr(x)
            result += '  ],\n'
                
        return result + ")\n"

 
 
class BaseGrammar:
    r'''Most basic grammar class.

    Usually you will rather use :py:class:`Grammar` instead of this for
    deriving you classes from.  If you really need a blank grammar, you
    can derive your grammar from this class.

    A Grammar class has following attributes:

    `__metaclass__`
        :py:class:`GrammarType` - the type of a grammar class

    `_TOKENS_`
        A dictionary of token-parsing regexes, which can be used
        with ``{name}`` for the smart value and ``{:name:}`` for the
        unchanged value.

        Smart value means that if you specify a token like::

            token = abcd

        You still can quantify the token without having strange
        effects:

            a-rule := foo{token}+

        Will be translated to::

            a-rule := foo(?:abcd)+

        The other way of access::

            b-rule := foo{:token:}+

        Will be translated to::

            b-rule := fooabcd+

        You can use the second form for example for defining character
        classes::

            word-chars = A-Za-z0-9_
            dash       = \-
            ident      = [{:word-chars:}{:dash:}]+

        The tokens are evaluated directly after a rule-part is read.

    `_ACTIONS_`
        This dictionary maps rule-names to action-names, which are
        methods in either ParseAction object passed to parser or
        in Grammar. This map is created from implicit parse-action 
        directives. Parse-actions are run on lexing a MatchObject
        and fill the `ast`-attribute of Lexem with life.

        Implicit parse-actions are specified by `_PARSE_ACTION_MAP_`.

    `_START_RULE_`
        Name of start-rule if no other given.
    '''

    #: :py:class:`GrammarType` - the type of a grammar class
    __metaclass__ = GrammarType  

    _TOKENS_      = {}
    '''
        A dictionary of token-parsing regexes, which can be used
        with ``{name}`` for the smart value and ``{:name:}`` for the
        unchanged value.

        Smart value means that if you specify a token like::

            token = abcd

        You still can quantify the token without having strange
        effects:

            a-rule := foo{token}+

        Will be translated to::

            a-rule := foo(?:abcd)+

        The other way of access::

            b-rule := foo{:token:}+

        Will be translated to::

            b-rule := fooabcd+

        You can use the second form for example for defining character
        classes::

            word-chars = A-Za-z0-9_
            dash       = \-
            ident      = [{:word-chars:}{:dash:}]+

        The tokens are evaluated directly after a rule-part is read.
    '''

    _ACTIONS_     = {} # implicit actions
    _TESTS_       = []
    _TMP_         = {} # (temporary) data (not inherited to subclasses)
    _NAME_        = None
    _START_RULE_  = None
    _INPUT_       = None
    _COMPILE_     = None
    _INCOMPLETE_  = False
    _SIGSPACE_    = False
    _BACKTRACK_    = True
    _SKIP_          = False
    _SKIP_BAK_      = None
    _SIGSPACE_RULE_ = ['<.ws>']
    _PARSE_ACTIONS_ = {}


    def __init__(self, s=None, **kargs):
        '''you may pass any keyword argument to override an attribute'''

        if (
            self.__class__ is BaseGrammar
            or self.__class__ is Grammar
           ):
                raise Exception("you must not instantiate %s directly" 
                    % self.__class__.__name__)

        if s is not None:
            self._INPUT_ = s

        self.__dict__.update(kargs)

    def __repr__(self):
        result = self.__class__.__name__+"(\n"
        for x in sorted(dir(self)):
            if x.startswith('_'): continue
            y = getattr(self, x)
            if not isinstance(y, Rule):
                result += "# %s = <Method>\n" % x
            else:
                result += "  %s = %s," % (x, repr(y))
                if x == self._START_RULE_:
                    result += " # START\n"
                else:
                    result += "\n"

        if self._TOKENS_:
            result += '  _TOKENS_ = {\n'
            for k,v in self._TOKENS_.items():
                result += "    %s: %s\n" % (repr(k), repr(v))
            result += '  },\n'

        if self._TESTS_:
            result += '  _TESTS_ = [\n'
            for x in self._TESTS_:
                result += "    %s\n" % repr(x)
            result += '  ],\n'
                
        return result + ")\n"

_GRAMMAR_NAMES = {}
def gen_grammar_name(grammar_factory):
    n = grammar_factory.__name__
    if n not in _GRAMMAR_NAMES:
        _GRAMMAR_NAMES[n] = 0
    _GRAMMAR_NAMES[n] += 1
    return "%s%02d" % (n, _GRAMMAR_NAMES[n])
 
# compile is needed by GrammarType for creating Grammar
def compile(input, type=None, name=None, extends=None, grammar=None, filename=None):
    r'''compile a grammar

    You can pass different inputs to this class, which has influence on
    return value.

    # `input` is grammar 
      class::

          class MyGrammar(Grammar):
              r"""This is my grammar class

              .. highlight:: aptk

              My grammar has following rule::

                  <foo> = "bar"
              """

      This is the way you usually invoke :py:func:`compile` with a 
      grammar class, because :py:func:`compile` is invoked by 
      :py:class:`GrammarType`.

    # Append whatever is defined in `input` to 
      `grammar`::

          class MyGrammar(Grammar):
              r"""Here are rules defined"""
 
          ...

          compile("here are more rules", grammar=MyGrammar)

      `input` may be either a file object (something having a read() method)
      or a string.

    # Create a new grammar named `name`, which extends grammars passed in
      iteratable `extends`. If you do not pass `extends`, then your grammar
      will extends :py:class:`Grammar`, extracting the rules from `input`.

    # Simply compile `input` to a list of grammars.

         list_of_grammars = compile("""
             :grammar first
             some := <rule>

             :grammar second
             another := <rule>
         """)

      `input` may be either a file object (something having a `read()` method)
      or a string.

    `Parameters`
        `input`
            Pass a grammar class, a string or whatever, which has a `read()`
            method, e.g. a file object.

        `type`
            Type of input, "sphinx" or "native".

        `name`
            Name of grammar, which shall be created and keep the rules given
            in `input`.

        `extends`
            If you pass a `name` you may pass `extends` as a list of names
            of grammars.

        `grammar`
            If you pass a grammar class, the input is added to this grammar 
            class.

        `filename`
            for informative purpose

    `Returns`
        A GrammarClass or (if no specific grammar given in some way) a list
        of grammar classes.
    '''
    do_compile = None

    if input.__class__ is GrammarType:
        do_compile = GrammarCompiler(grammar=input)
        assert name is None and extends is None and grammar is None
    else:
        if grammar is None:
            if name is not None:
                extends = [] if extends is None else extends
                grammar = GrammarType(name, extends, {})
        else:
            assert name is None and extends is None, \
                "pass either grammar or name and optionally extends"

        do_compile = GrammarCompiler(grammar=grammar, input=input)

    return do_compile(type=type, filename=filename)


class Grammar(BaseGrammar):
    r'''Default grammar with basic tokens and rules.

    .. highlight:: aptk

    This is the grammar, you will usually derive your grammars from.

    It provides most common tokens::
    
      SP   = \x20
      NL   = \r?\n
      LF   = \n
      CR   = \r
      CRLF = \r\n
      ws   = \s+
      ws?  = \s*
      N    = [^\n]
      HWS  = [\x20\t\v]
      LINE = [^\n]*\n

    And a general ActionMap, which lets you connect your grammar to 
    basic :py:class:`ParseActions`::

      :parse-action-map
          "$" make_string
          "@" make_list
          "%" make_dict
          "#" make_number
          "<" make_inherit
          ">" make_name
          "~" make_quoted

    And most common rules::

      ident     $= [A-Za-z_\-][\w\-]*
      number    #= [+-]?\d+(?:\.\d+)?
      integer   #= \d+
      dq-string ~= "(?:\\\\|\\[^\\]|[^"\\])*"
      sq-string ~= '(?:\\\\|\\[^\\]|[^'\\])*'
      ws        $= \b{ws}\b|{ws?}
      line      $= [^\n]*\n

    Making explicit the whitespace rule default from BaseGrammar::

      :sigspace <.ws>

    Define how args of BRANCH are parsed::

      :args-of BRANCH string capturing non-capturing regex

    Define operation precedence parser::

      :args-of  EXPR string capturing non-capturing raw 
                  => aptk.oprec.OperatorPrecedenceParser

    '''

    def BRANCH(P, args, s=None, start=None, end=None):
        '''lookahead and branch into some rule.

        Example::

            branched := <BRANCH{
                         "a"    <a-rule>
                         [bcd]  <bcd-rule>
                         a|b    <a-or-b-rule>
                         <default-rule>
                        }>

        If string to be matched startswith 
        '''

        default = None
        if len(args) % 2: default = args[-1]

        for i in range(0, len(args), 2):
            x = args[i]
            m = x.match(P, s, start, end)
            if m is not None:
                for m in args[i+1](P, s, start, end):
                    return m

        return None


# default grammar is Grammar
GrammarCompiler.grammar_factory = lambda s, *a, **k: GrammarType(*a, **k)

if 0:
  class OsSpecific:
    r'''Provides OS specific tokens according to os module

    Tokens::

        pardir  = %(pardir)s
        linesep = %(linesep)s
        curdir  = %(curdir)s
        sep     = %(sep)s
        altsep  = %(altsep)s
        extsep  = %(extsep)s

    ''' % dict( (a, re.escape(getattr(os, a))) for a in 
        "pardir linesep curdir sep altsep extsep".split() )
