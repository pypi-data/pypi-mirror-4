#
# Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
# Published under New BSD License, see LICENSE.txt for details.
#
from .util import Undef
import re, sys, os, logging, time
from .rules import *
from .grammar_tester import TokenTest, RuleTest

__all__ = ['GrammarError', 'BaseGrammar', 'Grammar', 'compile']

class GrammarError(Exception):
    '''exception in grammar compilation.

    This exception is raised, if there is an error in grammar compilation.
    '''
    def __init__(self, grammar_compiler, msg, **kargs):
        self.grammar_compiler = grammar_compiler
        for k,v in kargs.items():
            setattr(self, k, v)

        self.line_no  = grammar_compiler.line_no
        self.filename = grammar_compiler.filename
        self.msg = msg
        log.debug("raised GrammarError: %s", msg)

    def __str__(self):
        return (self.msg + " in file %(filename)s, line %(line_no)s") % self.__dict__

logging.basicConfig(stream=sys.stderr)
log = logging.getLogger('aptk.grammar_compiler')
#log.setLevel(logging.DEBUG)

RE_BASE_INDENT     = re.compile(r"(?:(?:(?=>\s)[^\n])*\n)*(\s*)")

def native_rule_producer(lines):
    if isinstance(lines, basestring):
        lines = lines.splitlines(1)

    rule, indent = None, None
    need_indent = False

    line_no = 0
    for line in lines:
        line_no += 1
        if not line.strip(): continue

        if need_indent and not re.match("^\s", line):
            if rule is not None:
                yield (rule, line_no)
                rule = None

            ignoring = True

        if rule is None:
            rule = line
            indent = re.match("^\s*", line).group(0)
            continue

        if re.match("^\s*#", line): continue

        if re.match("^%(indent)s\s(?!\s*#)"%locals(), line):
            rule += line
            continue

        elif rule is not None:
            yield (rule, line_no)
            rule = line
            indent = re.match("^\s*", line).group(0)

    if rule is not None:
        yield (rule, line_no) 


def sphinx_rule_producer(lines):
    if isinstance(lines, basestring):
        lines = lines.splitlines(1)

    ignoring = True

    rule, indent = None, None
    need_indent = False

    do_grammar = True

    highlight_aptk = False

    line_no = 0
    for line in lines:
        line_no += 1
        line = line.rstrip()
        if not line: continue

        if need_indent and not re.match("^\s", line):
            if rule is not None:
                yield (rule, line_no)
                rule = None

            ignoring = True

        if ignoring:
            if line == '.. highlight:: aptk':
                highlight_aptk = True
                continue

            elif line.startswith('.. highlight::'):
                highlight_aptk = False
                continue

            elif line.startswith('.. grammar off'):
                do_grammar = False
                continue

            elif line.startswith('.. grammar on'):
                do_grammar = True
                continue

            elif not do_grammar:
                continue

            elif line == '.. code-block:: aptk':
                ignoring = False
                need_indent = True
                indent = None
                rule = None
                continue
                
            elif ( highlight_aptk
                 and line.endswith('::') 
                 and not line.startswith('.. ')
                ):
                ignoring = False
                need_indent = True
                indent = None
                rule = None
                continue
            else: continue

        if rule is None:
            rule = line+"\n"
            indent = re.match("^\s*", line).group(0)
            continue

        if re.match("^\s*#", line): continue

        if re.match("^%(indent)s\s(?!\s*#)"%locals(), line):
            rule += line+"\n"
            continue

        if not re.match("^%(indent)s"%locals(), line):
            if rule is not None:
                yield (rule, line_no)
                rule = None

            ignoring = True
            continue

        elif rule is not None:
            yield (rule, line_no)
            rule = line+"\n"
            indent = re.match("^\s*", line).group(0)

    if rule is not None:
        yield (rule, line_no) 

def remove_first_line(s):
    p = s.find('\n')
    if p < 0: return s
    return s[p:]

def remove_indent(s):
    base_indent = RE_BASE_INDENT.match(s).group(1)
    blen = len(base_indent)
    return ''.join([ line[blen:]+'\n' for line in s.splitlines(0) ])

class GrammarCompiler:
    rule_producer = {
        'native': native_rule_producer,
        'sphinx': sphinx_rule_producer
    }

    # regular expressions
    RE_TOKTOK       = re.compile(r'\{(?!\d+\})[^},\s]+\}')
    RE_TOKORG       = re.compile(r'\{:(?!\d+\})[^},\s]+?:\}')
    RE_NO_GROUP     = re.compile(r'(\\x[\dA-Fa-f]{2,4}|\\.|\[\^?[^\]]+\]|.)$')
    RE_COMPLEX_RULE = re.compile(r'<\w+{')
    RE_TRANSP_RULE  = re.compile(r'<\.[\w\-]+>')
    RE_NAMED_RULE   = re.compile(r'<[\w\-]+>')
    RE_ARG_RULE     = re.compile(r'<\.?\w+:(?:[^>\\]|\\\\|\\>)*>')
    RE_QUANT        = re.compile(r'\{\d*,\d*\}|\{\d+\}$')

    RE_DQ_STRING      = re.compile(r'"((?:\\\\|\\[^\\]|[^"\\]+)*)"')
    RE_SQ_STRING      = re.compile(r"'((?:\\\\|\\[^\\]|[^'\\]+)*)'")
    RE_DQ_STRING_ONLY = re.compile(r'"((?:\\\\|\\[^\\]|[^"\\]+)*)"$')
    RE_SQ_STRING_ONLY = re.compile(r"'((?:\\\\|\\[^\\]|[^'\\]+)*)'$")

    doc_string_filter = [ remove_first_line, remove_indent ]
    doc_string_type   = 'sphinx'
    string_type       = 'native'
    string_filter     = [ ]
    

    grammar_factory   = None

    QUANTIFIERS = '?*+'

    def __init__(self, grammar=None, input=None, doc_string_filter=None, 
        string_filter=None):

        '''pass grammar object, which shall be populated'''
        #self.EXPECTED_RULES = {}
        self.line_no = 0

        if grammar is not None:
            self.grammar = grammar
            self.grammar._COMPILE_ = self
        else:
            # we go into multigrammar mode
            self.grammars = {}

        self.is_doc_string = False

        if input is None:
            input = grammar.__doc__
            self.is_doc_string = True

        self.input = input

        if doc_string_filter is not None:
            self.doc_string_filter = doc_string_filter

        if string_filter is not None:
            self.string_filter = string_filter

    def _expect_rule(self, name):
        '''call this to expect a rule defined'''

        if not hasattr(self.grammar, name):
            self.grammar._EXPECTED_[name] = self.line_no

    def _defined_rule(self, name):
        '''call this to tel that rule has been defined'''

        if name in self.grammar._EXPECTED_:
            del self.grammar._EXPECTED_[name]

    def expand_tokens(self, s):
        '''expand tokens in given string'''

        TOKENS = self.grammar._TOKENS_
        RE_NO_GROUP = self.RE_NO_GROUP

        def _tok_expander(m):
            '''intension is to be able to write {foo}? for the TOKTOK'''
            t = TOKENS[m.group(0)[1:-1]]
            if RE_NO_GROUP.match(t):
                return t
            return '(?:'+t+')'

        try:
            s = self.RE_TOKORG.sub(lambda m: TOKENS[m.group(0)[2:-2]], s)
            s = self.RE_TOKTOK.sub(_tok_expander, s)
        except Exception, e:
            raise GrammarError(self,
                "error in expanding tokens in %(input)s: %(errmsg)s", input=s,
                errmsg=str(e))

        return s

    def token_definition(self, tokens):
        r'''handle token definition

        Example::

            token  = value
            token2 = some{token}\x20
            token3 = [ foo ]*
            token4 = (?: foo )*

        Where :rule:`{token3}` and :rule:`{token4}` are equivalent.

        '''
        if isinstance(tokens, basestring): tokens = [ tokens ]

        name  = tokens[0]

        _final = []
        for t in tokens[2:]:
            if   t == '[':
                _final.append('(?:')
                continue
            if t.startswith(']'):
                quantifier, tok = self.quantifier(t)
                if tok == ']':
                    _final.append(')'+t[1:])
                    continue
            _final.append(t)

        value = self.expand_tokens(''.join(_final))
        try:
            self.grammar._TOKENS_[name] = value
        except Exception, e:
            raise GrammarError(self,
                "could not compile {%(name)s} '%(value)s' to regex: "
                "'%(message)s'", 
                name=name, value=value, message=str(e))

    def rule_definition(self, tokens):
        '''handle rule definition

        Strictly speaking in backus-naur-form a rule looks like::

           <rule> ::= <first> <second> ...

        But you may be more sloppy like::

           rule  := <first> <second>

        '''
        if isinstance(tokens, basestring): tokens = [ tokens ]

        G = self.grammar
        PARSE_ACTION_MAP = G._PARSE_ACTION_MAP_

        sigspace = None
        if tokens[0] in (':sigspace', ':s'):
            sigspace = True
            tokens.pop(0)

        name, operator = tokens[:2]

        tokens = tokens[2:]

        if name.startswith('<') and name.endswith('>'):
            name = name[1:-1]

        if not tokens:  # empty rule, which will be filled by a inheriting grammar
            self._defined_rule(name)
            return

        pair = (operator[-1] == '>')
        if pair: operator = operator[:-1]

        if operator[-1] == '-':
            self.grammar._SIGSPACE_ = True
            operator = operator[:-1] + '='
        else:
            self.grammar._SIGSPACE_ = False

        if operator != ':=' and operator.startswith(':'):
            #if self.grammar._BACKTRACK_BAK_ is None:
                #self.grammar._BACKTRACK_BAK_ = self.grammar._BACKTRACK_
            self.grammar._BACKTRACK_ = True
            operator = operator[1:]
        else:
            self.grammar._BACKTRACK_ = False

        action = None

        op = operator[:-1]
        if op in PARSE_ACTION_MAP:
            action = PARSE_ACTION_MAP[op]
        elif op != ':':
            action = op

        if action:
            if pair:
                G._ACTIONS_[name] = (name, action)
            else:
                G._ACTIONS_[name] = action

        if G._START_RULE_ is None: G._START_RULE_ = name

        if hasattr(G, name):
            log.info(
                "at line %s: Grammar already has rule %s",
                self.line_no, repr(name))

        #if sigspace is not None:
            #old_sigspace = self.grammar._SIGSPACE_
            #self.grammar._SIGSPACE_ = True

        setattr(G, name, self.alternatives(tokens, 
            backtrack=self.grammar._BACKTRACK_, 
            sigspace=self.grammar._SIGSPACE_))

        #if sigspace is not None:
            #self.grammar._SIGSPACE_ = old_sigspace

        self._defined_rule(name)

    def test_definition(self, s):
        name, op, s = s.lstrip().split(None, 2)

        pos = 0
        if s.startswith('@'):
            pos, s = s.lstrip().split(None, 1)
            pos = int(pos[1:])

        RE_AST_TEST = re.compile('-(\w*)->|->')

        s = ''.join([line.strip()+"\n" for line in s.splitlines(0)])
        s = s.replace('\\\n', '')
        #s = re.sub(r"\n\\[\x20\t\v]*", " ", s)

        # TODO add position argument  foo ~~ @6 "..."
        parse_actions = None

        p = 0

        m = self.RE_DQ_STRING.match(s)
        if m:
           p = m.end()
           #input = re.sub(r'\\(\\|")', r'\1', m.group(1))
           input = m.group(1).decode('string_escape')
        else:
           m = self.RE_SQ_STRING.match(s)
           if m:
               p = m.end()
               #input = re.sub(r"\\(\\|')", r'\1', m.group(1))
               input = m.group(1).decode('string_escape')
           else:
               m = re.match(r'(?:\|[^\n]*\n)+', s)
               if m:
                   input = re.sub(r"(?m)^\|\x20?", "", m.group(0))
                   p = m.end()
               else:
                   m = RE_AST_TEST.search(s, p)
                   if m:
                       input = s[p:m.start()].strip()
                       p = m.start()
                   else:
                       input = s[p:].strip()
                       p = len(s)

                   #raise GrammarError(self,
                       #"test input (string) expected in %(string)s",
                       #string=s)

        expected = None

        p = s.find('-', p)
        if p >= 0:
          if s.startswith('->', p):
            parse_actions = None
            p += 2
          else:
            m = RE_AST_TEST.match(s, p)

            if not m:
                raise GrammarError(self,
                    "expected output expected in %(string)s",
                    string=s)

            parse_actions = m.group(1)

            p = m.end()

          s = s[p:].lstrip()

          m = self.RE_DQ_STRING_ONLY.match(s.rstrip())
          if m:
            log.error("m: %s", m.groups())
            #expected = re.sub(r'\\(\\|")', r'\1', m.group(1))
            expected = m.group(1).decode('string_escape')[1:-1]
          else:
            m = self.RE_SQ_STRING_ONLY.match(s.rstrip())
            if m:
               # expected = re.sub(r"\\(\\|')", r'\1', m.group(1))
                expected = m.group(1).decode('string_escape')[1:-1]
            else:
                m = re.match(r'(?:\|[^\n]*\n)+', s)
                if m:
                    expected = re.sub(r"(?m)^\|\x20?", "", m.group(0))
                else:
                    expected = s.strip()


        if name[0] == '{' and name[-1] == '}':
            test = TokenTest
            name = name[1:-1]

        elif name[0] == '<' and name[-1] == '>':
            test = RuleTest
            name = name[1:-1]

        else:
            test = RuleTest

        debug = self.grammar._TMP_.get('debugging', 0)
        if self.grammar._TMP_.get('debug', 0):
            debug = 1
            del self.grammar._TMP_['debug']

        self.grammar._TESTS_.append(test(name, 
            op, pos, input, parse_actions, expected,
            skip=self.grammar._SKIP_, debug=debug))

    def definition(self, s):
        '''handle token definition and rule definition'''
        tokens = s.strip().split()
        local_sigspace = True

        # TODO create nice error if not yet self.grammar set

        if tokens[0].startswith(':'):
            # maybe even switch grammar here to given grammar.
            # for now only set the name of current grammar

            if tokens[0] == ':grammar':
                assert hasattr(self, 'grammars'), \
                    ":grammar is not allowed in single grammar mode"

                if len(tokens) > 2:
                    assert tokens[2] == 'extends'

                name = tokens[1]

                if name not in self.grammars:
                    g = self.create_grammar(tokens[1], tokens[3:])
                    self.grammars[name] = g

                # switch grammar
                self.grammar = self.grammars[name]

            elif tokens[0] == ":parse-action-map":
                
                _name = None
                for t in tokens[1:]:
                    if _name is None:
                        _name = t
                        if len(_name) > 2 and _name.startswith('"') and _name.endswith('"'): _name = _name[1:-1]
                    elif t == '=>':
                        continue
                    else:
                        self.grammar._PARSE_ACTION_MAP_[_name] = t
                        _name = None

            elif tokens[0] == ':parse-actions':
                
                _name = None
                for t in tokens[1:]:
                    if _name is None:
                        _name = t
                    else:
                        pa = self.grammar._PARSE_ACTIONS_
                        x = {}
                        assert re.match("^\w+(\.\w+)+$", t), "%s is not valid" % t
                        mod, thing = t.rsplit('.', 1)
                        exec "from %s import %s" % (mod, thing) in x
                        if callable(x[thing]): pa[_name] = x[thing]()
                        else: pa[_name] = x[thing]

            elif tokens[0] == ":args-of":
                _name = tokens[1]
                _list = tokens[2:]

                postprocessor = None    # postprocessor may return a rule, 
                if len(_list) > 2 and _list[-2] == '=>':
                    postprocessor = _list[-1]
                    _list = _list[:-2]

                for e in _list:
                    assert e in ("string", "capturing", "non-capturing", 
                        "regex", "raw", "slashed-regex", "char-class"), "unknown args-class %s" % e

                self.grammar._ARGS_OF_[_name] = (_list, postprocessor)

            #elif tokens[0] == ':test':
                #_name = tokens[1]
                #self.grammar._TMP_['test'] = 


 #           elif tokens[0] == ":-sigspace":
 #               self.grammar._SIGSPACE_ = False
#
            elif tokens[0] == ":sigspace":
                #self.grammar._SIGSPACE_ = True

                if len(tokens) > 1:
                    self.grammar._SIGSPACE_RULE_ = tokens[1:]
#
#            elif tokens[0] in (":-backtrack", ":-backtracking"):
#                self.grammar._BACKTRACK_ = False
#
#            elif tokens[0] in (":+backtrack", ":+backtracking"):
#                self.grammar._BACKTRACK_ = True
#
            elif tokens[0] in (":debug",):
                self.grammar._TMP_['debug'] = 1

            elif tokens[0] in (":+debug",):
                self.grammar._TMP_['debugging'] = 1

            elif tokens[0] in (":-debug",):
                self.grammar._TMP_['debugging'] = 0

            elif tokens[0] in (":-skip",):
                self.gramamr._SKIP_ = False

            elif tokens[0] in (":+skip",):
                self.grammar._SKIP_ = " ".join(tokens[1:])
                if not self.grammar._SKIP_: self.grammar._SKIP_ = True

            elif tokens[0] == ':skip':
                if self.grammar._SKIP_BAK_ is None:
                    self.grammar._SKIP_BAK_ = self.grammar._SKIP_

                self.grammar._SKIP_ = " ".join(tokens[1:])
                if not self.grammar._SKIP_: self.grammar._SKIP_ = True

#            elif tokens[0].startswith(':s'):
#                tok = tokens[0]
#                if tok.startswith(':sigspace') or tok.startswith(':s'):
#                    if tok.startswith(':sigspace'):
#                        tok = tok[9:]
#                    else:
#                        tok = tok[2:]
#                    
#                    if self.grammar._SIGSPACE_BAK_ is None:
#                        self.grammar._SIGSPACE_BAK_ = self.grammar._SIGSPACE_
#                    self.grammar._SIGSPACE_ = True

#            elif tokens[0] in (":backtrack", ":b"):
#                if self.grammar._BACKTRACK_BAK_ is None:
#                    self.grammar._BACKTRACK_BAK_ = self.grammar._BACKTRACK_
#                self.grammar._BACKTRACK_ = True
#
#            elif tokens[0] in (":ratchet", ":r"):
#                if self.grammar._BACKTRACK_BAK_ is None:
#                    self.grammar._BACKTRACK_BAK_ = self.grammar._BACKTRACK_
#                self.grammar._BACKTRACK_ = False
#                  
        elif tokens[1] == '=': # Token (no sigspace applied)
            self.token_definition(tokens)

        elif tokens[1] in ('~', '!~', '~~', '=~'): # matching operator for implicit test
            self.test_definition(s)

        else: # :=, $=, @=, %=, ... (name)= -
            self.rule_definition(tokens)

            #if self.grammar._SIGSPACE_BAK_ is not None:
                #self.grammar._SIGSPACE_ = self.grammar._SIGSPACE_BAK_
                #self.grammar._SIGSPACE_BAK_ = None
 #
            #if self.grammar._BACKTRACK_BAK_ is not None:
                #self.grammar._BACKTRACK_ = self.grammar._BACKTRACK_BAK_
                #self.grammar._BACKTRACK_BAK_ = None



    def complex_rule(self, name, tokens, backtrack=False):
        '''handle complex rule

        Example::

             <foo{ first second third }>

             <.foo{ first second third }>
        '''
        args_of, postprocessor = self.grammar._ARGS_OF_.get(name, (['raw'], None))
        if not args_of: args_of = ['raw']

        if postprocessor is not None:
            m, c = postprocessor.rsplit('.', 1)
            x = {}
            exec "from %s import %s" % (m,c) in x
            postprocessor = x[c]

        rule = []
        while tokens:
            tok = tokens.pop(0)
            if tok.startswith('}>'):
                if len(tok) not in (2, 3):
                    raise GrammarError(self,
                       "unexpected token %(token)s", token=tok)
                quantifier, tok = self.quantifier(tok)
               # if tok[-1] in '?*+': quantifier = tok[-1] ; tok = tok[:-1]

                if postprocessor is None:
                    args = tuple(rule)
                else:
                    args = postprocessor(self, name, rule, backtrack=backtrack)

                if isinstance(args, Rule):
                    rule = args
                else:
                    rule = NonCapturing(name, args, backtrack=backtrack)

                if quantifier:
                    return Quantified(rule, quantifier, backtrack=backtrack)
                else:
                    return rule

            tok = self.expand_tokens(tok)

            for a in args_of:
                if a == 'string' and self.rule_string(rule, tok):
                    break
                elif a == 'capturing' and self.rule_capturing(rule, tok, backtrack=backtrack):
                    break
                elif (
                    a == 'non-capturing' \
                    and self.rule_non_capturing(rule, tok, backtrack=backtrack)
                    ): break
                elif a == 'slashed-regex' and tok[0] == "/" and tok[-1] == "/":
                    self.rule_regex(rule, tok[1:-1])
                    break
                    
                elif a == 'char-class' and tok[0] == "[" and tok[-1] == "]":
                    self.rule_regex(rule, tok)
                    break
 
                elif a == 'regex':
                    self.rule_regex(rule, tok)
                    break

                elif a == 'raw':
                    rule.append(tok)

        raise GrammarError(self, "unexpected end of token stream: expecting '}>'")

    def quantified(self, rule, quantifier, backtrack=False):
        '''return a quantified rule'''

        if quantifier:
            return Quantified(rule, quantifier, backtrack=backtrack)

        return rule

    def quantifier(self, tok):
        '''handle quantifier part of token'''

        quantifier = None
        if tok[-1] in self.QUANTIFIERS:
            quantifier = tok[-1] ; tok = tok[:-1]

        m = self.RE_QUANT.search(tok)
        if m:
            quantifier = tok[slice(*m.span())]
            tok = tok[:m.start()]

        return quantifier, tok

    def rule_non_capturing(self, rule, tok, backtrack=False):
        if not self.RE_TRANSP_RULE.match(tok): return False

        quantifier, tok = self.quantifier(tok)
                
        name = tok[2:-1]
        r = NonCapturing(name, backtrack=backtrack)
        rule.append(self.quantified(r, quantifier, backtrack=backtrack))

        self._expect_rule(name)

        return True

    def rule_capturing(self, rule, tok, backtrack=False):

        if not self.RE_NAMED_RULE.match(tok): return False

        quantifier, tok = self.quantifier(tok)
        name = tok[1:-1]

        rule.append(self.quantified(Capturing(name, backtrack=backtrack), quantifier, backtrack=backtrack))

        self._expect_rule(name)

        return True

    def rule_with_arg(self, rule, tok, backtrack=False):
        if not self.RE_ARG_RULE.match(tok): return False

        quantifier, tok = self.quantifier(tok)
        _name, _args = tok[1:-1].split(':', 1)
        _named = (_name[0] == '.')
        if _named: _name = _name[1:]
        _args = _args.replace('\\>', '>').replace('\\\\', '\\')
        _args = self.expand_tokens(_args)

        if len(_args)>1 and _args.startswith('/') and _args.endswith('/'):
            _args = re.compile(_args[1:-1])

        if _named:
            r = Capturing(_name, _args, backtrack = backtrack)
        else:
            r = NonCapturing(_name, _args, backtrack = backtrack)

        rule.append(self.quantified(r, quantifier, backtrack=backtrack))

        self._expect_rule(name)
        return True

    def rule_single_quoted_string(self, rule, tok, backtrack=None):
        if not self.RE_SQ_STRING.match(tok): return False

        s = re.sub(r"\\(\\|')", r'\1', tok[1:-1])
        rule.append(String(s.decode("string_escape")))

        return True
       
    def rule_double_quoted_string(self, rule, tok, backtrack=None):
        if not self.RE_DQ_STRING.match(tok): return False

        s = re.sub(r'\\(\\|")', r'\1', tok[1:-1])
        rule.append(String(s.decode('string_escape')))

        return True

    def rule_string(self, rule, tok, backtrack=False):
        if self.rule_single_quoted_string(rule, tok): return True
        if self.rule_double_quoted_string(rule, tok): return True
        return False

    def whitespace(self, tokens, backtrack=False):
        '''create a whitespace rule'''
        result = self.sequence(tokens, backtrack=backtrack, sigspace=False)
        return result

    def any_rule(self, rule, tok, tokens, backtrack=False):
        if self.RE_COMPLEX_RULE.match(tok):
            rule.append(self.complex_rule(tok[1:-1], tokens, backtrack))

        elif self.rule_non_capturing(rule, tok, backtrack):
            return

        elif self.rule_capturing(rule, tok, backtrack):
            return

        elif self.rule_with_arg(rule, tok, backtrack=backtrack):
            return

        elif self.rule_string(rule, tok):
            return

        else:
            r = self.expand_tokens(tok)

            try:
                rule.append(Regex(r))
            except Exception, e:
                raise GrammarError( self,
                    "Error compiling: %(token)s (expanded %(r)s): "
                    "%(errmsg)s", token=tok, r=r, errmsg=str(e))
            finally:
                pass
   
    def sequence(self, tokens, backtrack=None, sigspace=None):
        if sigspace is None:
            sigspace = self.grammar._SIGSPACE_
        if backtrack is None:
            sigspace = self.grammar._BACKTRACK_

        if isinstance(tokens, basestring): tokens = tokens.split()
        rule = []

        while tokens:
            tok = tokens.pop(0)

            quantifier = None
            if tok == '[':
                rule.append(self.alternatives(tokens, backtrack, sigspace))
                continue

            elif tok == '|' or tok.startswith(']'):
                quantifier, t = self.quantifier(tok)
                if t in "|]":
                    tokens.insert(0, tok) # push back token
                    break

            self.any_rule(rule, tok, tokens, backtrack)


        if len(rule) == 1:
            return rule[0]

        if sigspace:
            new_rule = []

            # sigspace is inserted after terminals or rules, which
            # end in a terminal
            #
            # in doubt insert sigspace
            def is_sigspace(_rule):
                if isinstance(_rule, Terminal): return True
                if isinstance(_rule, Rule):
                    if isinstance(_rule, Alternative):
                        r = True
                        for _r in _rule.data:
                            r = r and is_sigspace(_r)
                        return r
                    elif isinstance(_rule, (Capturing, NonCapturing)):
                        if _rule.data[1] is not None: return True
                        else:
                            if not hasattr(self.grammar, _rule.data[0]):
                                return True

                            return is_sigspace(getattr(self.grammar, _rule.data[0]))
                    else:
                        return is_sigspace(_rule.data)

            for r in rule:
                new_rule.append(r)

                if is_sigspace(new_rule[-1]):
                    self.any_rule(new_rule, self.grammar._SIGSPACE_RULE_[0],
                        self.grammar._SIGSPACE_RULE_[1:])
                    new_rule[-1].is_sigspace = True

            rule = new_rule

        return Sequence(rule, backtrack=backtrack)

    def rule(self, tokens, backtrack=False, sigspace=False):
        '''convenience call from outside'''

        result = self.sequence(tokens, backtrack=backtrack, sigspace=sigspace)
        assert not isinstance(result, Sequence)
        return result

    def alternatives(self, tokens, backtrack=False, sigspace=False):
        if isinstance(tokens, basestring): tokens = tokens.split()
        rule = []
        quantifier = None
        while tokens:
            rule.append(self.sequence(tokens, backtrack=backtrack, sigspace=sigspace))
            if tokens:
                tok = tokens.pop(0)
                if tok == '|': continue
                if tok.startswith(']'):
                    quantifier, t = self.quantifier(tok)
                    if t == ']': break

        if len(rule) == 1:
           rule = rule[0]
        else:
            rule = Alternative(rule, backtrack=backtrack)

        if quantifier:
            rule = Quantified(rule, quantifier, backtrack=backtrack)
        return rule

    def create_grammar(self, name, extends):
        bases = []
        for b in extends:
            if '.' in b:
                module, grammar = b.rsplit('.', 1)
                m = __import__(module, globals=globals(), fromlist=[grammar])
                bases.append(getattr(m, grammar))
            else:
                assert b in self.grammars, "unknown grammar %s" % b
                bases.append(self.grammars[b])
        return self.grammar_factory(name, bases, {})

    def setup(self, G):
        '''do some postprocessing

        it is intended to classify, if a rule is terminal or if a rule is
        recursive.

        '''

#        if 'ParseActions' not in G._PARSE_ACTIONS_:
#            from .actions import ParseActions
#            G._PARSE_ACTIONS_['ParseActions'] = ParseActions()

        for n in dir(G):
            if n.startswith('_') and n.endswith('_') and len(n) > 2: continue

            r = getattr(G, n)
            if isinstance(r, Rule):

                r.setup(G, [ ])

                if n in r.called:
                    r.recursive = n

    def __call__( self, input = None, rule = None, 
        doc_string_filter = None, string_filter = None,
        type = None, rule_producer = None, incomplete = None, grammar = None,
        filename = None
        ):

        if hasattr(self, 'grammar'):
            grammar = self.grammar

        if filename is None:
            if grammar is not None:
                if hasattr(grammar, '__module__'):
                    m = grammar.__module__
                    import sys
           
                    m = sys.modules[m]
                    if hasattr(m, '__file__'):
                        filename = m.__file__

            if filename is None: filename = '<unknown>'

        self.filename = filename

        #if grammar is None:
        #    grammar = self.grammar_factory()
        #    self.grammar = grammar
        #    self.grammar._COMPILE_ = self

        # make a string out of input
        if input is None:
            # default is to take inputs, passed on init
            input = self.input
            is_doc_string = self.is_doc_string

        if not isinstance(input, (basestring, file)):
            input = input.__doc__
            if incomplete is None and hasattr(input, '_INCOMPLETE_'):
                incomplete = input._INCOMPLETE_

            is_doc_string = self.is_doc_string

        if hasattr(input, 'read'):
        #if isinstance(input, file):
            input = input.read()

        # apply filter to string 
        if is_doc_string:
            if doc_string_filter is None:
                doc_string_filter = self.doc_string_filter

            if type is None:
                type = self.doc_string_type

            for f in doc_string_filter:
                input = f(input)

        else:
            if string_filter is None:
                string_filter = self.string_filter

            if type is None:
                type = self.string_type

            for f in string_filter:
                input = f(input)

        # if a rule is passed, call that rule with input as input
        if rule is not None:
            return getattr(self, rule)(input)

        if rule_producer is None:
            rule_producer = self.rule_producer[type.lower()]

        for rule, line_no in rule_producer(input):
            self.line_no = line_no
            log.debug("rule: %s", rule)
            self.definition(rule)

        if hasattr(self, 'grammars'):
            for n,g in self.grammars.items():
                if g._EXPECTED_:
                    raise GrammarError( self,
                        "following rules are expected, but not defined "
                        "in grammar %(grammar)s:\n" + 
                        ''.join([ "  %s at line %s\n" %(k,v) 
                        for k,v in g._EXPECTED_.items()]), grammar=n)
                log.debug("Grammar %s: %s", n, g)
                self.setup(g)
            return self.grammars

        if self.grammar._EXPECTED_:
            raise GrammarError( self,
                "following rules are expected, but not defined in grammar "
                "%s:\n" % self.grammar.__name__ +
                ''.join([ "  %s at line %s\n" %(k,v) 
                for k,v in self.grammar._EXPECTED_.items()])
            )

        self.setup(self.grammar)

        log.debug("Grammar %s: %s", self.grammar.__name__, self.grammar)
        return self.grammar

