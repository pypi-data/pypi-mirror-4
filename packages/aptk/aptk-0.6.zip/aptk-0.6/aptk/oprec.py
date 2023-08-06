#
# Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
# Published under New BSD License, see LICENSE.txt for details.
#
r'''

aptk.oprec - Operation Precedence Parser
========================================

.. highlight:: aptk

.. grammar off

Operation precedence parsers are intended to parse expressions, where 
never is a sequence of non-terminals.  Usually 
you will use it to parse (mathematical) expressions.

You can invoke OperationPrecedenceParser into your grammar by using::

  :args-of OPTABLE string capturing non-capturing raw
           => aptk.oprec.OperatorPrecedenceParser

Then you can create rules like this::

  my_rule_name1 := <OPTABLE{
                      :rule T <.term>
                      ...
                      }>

  my_rule_name2 := <OPTABLE{
                      :rule T <.term2>
                      :rule W ""
                      :rule E
                      ...
                      }>

Every ``OPTABLE`` invokation creates a new rule.


.. grammar on

In any :py:class:`Grammar`-descending grammar this is already done for you
and operation precedence is accessible via rule ``EXPR``::

   :grammar operation-precedence-parser-tests

   expr  := <EXPR{
              :flags with-ops

              :op L E+E
          }>

You have to define a :rule:`<term>`, such that a term, which is the only 
non-terminal-rule in expressions, can be parsed::

   term       := <number> | <ident>

Expression above parses for example following expressions::

   <expr> ~~ 5 + 5 
          -> expr( E+E( number( '5' ), op( '+' ), number( '5' ) ) )

   <expr> ~~ 1 + 2 + 3 
          -> expr( E+E( 
               E+E(
                 number( '1' ), 
                 op( '+' ),
                 number( '2' ) 
               ),
               op( '+' ),
               number( '3' )
             ) )

You see in parse trees of expressions above, that the operator is also
lexed (as "op").  This is triggered by flag :rule:`with-ops`.  If you
leave out this flag, operators are not lexed, as you see in further
examples::

   expr2 :- <EXPR{
              :op L E+E
              :op L E-E  = E+E
              :op L E*E  > E+E
              :op L E/E  = E*E
              :op L E**E > E*E
              :op L E++  > E**E
              :op R ++E  = E++
              :op R (E)  > E++
          }>

First example where operator precedence table is used::

   <expr2> ~~ 5 + 5 * 4 
           -> expr2( E+E(
                 number( '5' ), 
                 E*E( number( '5' ), number( '4' ) ) 
              ) )

A more complex example::

   <expr2> ~~ 5**2 + 4**2/3**1 * 2 + 1 
           ->  expr2( E+E(
                  E+E(
                    E**E( number( '5' ), number( '2' ) ), 
                    E*E(
                      E/E(
                        E**E( number( '4' ), number( '2' ) ),
                        E**E( number( '3' ), number( '1' ) )
                      ),
                      number( '2' )
                    )
                  ),
                  number( '1' )
               ) )

Here you see how whitespace has influence on tokenizer::

   <expr2> ~~ 1*3+++++1 
           -> expr2( E+E( 
                E*E( number( '1' ), E++( E++( number( '3' ) ) ) ), 
                number( '1' ) 
              ) )

   <expr2> ~~ 1*3++ + ++1 
           -> expr2( E+E(
               E*E( number( '1' ), E++( number( '3' ) ) ),
               ++E( number( '1' ) )
           ) )

   <expr2> ~~ 1*3+++(++1) 
           -> expr2( E+E( 
                E*E( number( '1' ), E++( number( '3' ) ) ), 
                (E)( ++E( number( '1' ) ) ) 
              ) )

   <expr2> ~~ (1*3)++
           -> expr2( E++(
                (E)(
                  E*E(
                    number( '1' ),
                    number( '3' )
                  )
                )
              ) )

Here you see how operator precedence has influence on interpretation of
a term ``++1--``::

   prepostest1 := <EXPR{
                  :op L ++E
                  :op L E-- > ++E
                 }>

   <prepostest1> ~~ ++1-- -> prepostest1( ++E( E--( number( '1' ) ) ) )

   prepostest2 := <EXPR{
                  :op L ++E
                  :op L E-- < ++E
                 }>

   <prepostest2> ~~ ++1-- -> prepostest2( E--( ++E( number( '1' ) ) ) )

   postcirc1   :- <EXPR{
                     :op R E(E)
                     :op R E,E < E(E)
                  }>

   <postcirc1> ~~  sum(1, 2) 
               -> postcirc1( E(E)(
                    E,E(
                      number( '1' ),
                      number( '2' ) 
                    )
                  ) )

   <postcirc1> ~~  sum(1, 2, 3, 4)
               -> postcirc1( E(E)(
                    E,E(
                      number( '1' ),
                      E,E(
                        number( '2' ),
                        E,E(
                          number( '3' ),
                          number( '4' )
                        )
                      )
                    )
                  ) )

.. grammar off

            <expression> ::= <EXPR{
                                :rule E <.expression>
                                :rule W <.ws>

                                :op L E==E         : equality
                                :op L E!=E = E==E  : inequality
                                :op L E+E  < E==E  : add
                                :op L E-E  = E+E   : substr
                                :op L E*E  < E+E   : mult
                                :op L E/E  = E*E
                                :op L (E)  < E*E
                                :op R -E   = (E)
                                }> 
                           | <number>
                           | <ident>

Typical operator association you find here:

* http://msdn.microsoft.com/en-us/library/126fe14k.aspx
* http://en.cppreference.com/w/cpp/language/operator_precedence

.. grammar on

'''

# TODO lexing operators should be able to turn off

from .rules import CustomRule, Rule, String, Regex
from .grammar_compiler import GrammarError
from .match_object import MatchObject
import re, logging

log = logging.getLogger('aptk.oprec')

class PeekIterator:
    def __init__(self, generator):
        self.generator = generator
        self._peek = []
        self._stopped = False

    def _do_peek(self):
        try:
            if not self._stopped:
                self._peek.append(self.generator.next())
        except StopIteration:
            self._stopped = True

    def peek(self, steps=1):
        while len(self._peek) < steps and not self._stopped:
            self._do_peek()

        if len(self._peek) < steps:
            return StopIteration

        return self._peek[steps-1]

    def next(self):
        if not self._peek: 
            self._do_peek()
        if not self._peek:
            raise StopIteration()
        return self._peek.pop(0)

class OperatorPrecedenceParser(CustomRule):

    backtrack = False

    def __init__(self, compiler, name, args, backtrack=False):
        CustomRule.__init__(self, data=args)

        self.compiler = compiler
        self.sigspace_rule = list(compiler.grammar._SIGSPACE_RULE_)
        self.sigspace = compiler.grammar._SIGSPACE_
        self.name = name
        self.args = args
        self.backtrack = backtrack
        self.parse_args(args)



    def parse_args(self, args):
        compiler = self.compiler

        self.aliases    = aliases    = {}
        #self.precedence = precedence = {'<': [], '=': {}, '>': []} 

        self.precedence = precedence = [ ] # a list of lists, from tightest to loosest
        prec_map  = {}
          # <: 0 is loosest, max is tightest
          # >: 0 is tightest, max is loosest
          # =: a, b where a has same precedence like b

        self.left_assoc = left_assoc = {}
        self.rules      = rules      = {}
        self.flags      = flags      = {}

        i = 0
        # parse args
        while i < len(args):
            if args[i] == ':rule':
                alias, rule = args[i+1], args[i+2]
                aliases[alias] = compiler.sequence(rule)
                i += 3
                continue

            if args[i] == ':flags':
                i += 1
                while i < len(args):
                    if args[i].startswith(':'): break
                    flags[args[i]] = 1
                    i += 1
                continue

            elif args[i] == ':op':
                assoc, rule = args[i+1], args[i+2]
                if assoc == 'L': left_assoc[rule] = True
                else: left_assoc[rule] = False

                rules[rule] = rule

                i += 3
                if i >=len(args):
                    assert not precedence, "precedence rule expected"
                    rule_class = [ rule ]
                    precedence.append(rule_class)
                    prec_map[rule] = rule_class
                    break

                if args[i] == ':op':
                    assert not precedence, "precedence rule expected"
                    rule_class = [ rule ]
                    precedence.append(rule_class)
                    prec_map[rule] = rule_class
                else:
                    if args[i] not in '=<>':
                        assert not precedence, "precedence rule expected"
                        rule_class = [ rule ]
                        precedence.append(rule_class)
                        prec_map[rule] = rule_class
                    else:
                        assert precedence, "precedence list is not seeded"
                        x = args[i]
                        other = args[i+1]
                        if x == '>': # tighter than my binding is higher than others
                            assert other in precedence[0], '%s is not at tail of precedence list consider "=" rule' % other
                            rule_class = [ rule ]
                            precedence.insert(0, rule_class)
                            prec_map[rule] = rule_class
                        elif x == '<':
                            assert other in precedence[-1], '%s is not at head of precedence list consider "=" rule' % other
                            rule_class = [ rule ]
                            precedence.append(rule_class)
                            prec_map[rule] = rule_class
                        elif x == '=':
                            prec_map[other].append(rule)
                          
                    i += 2

                if len(args) > i:
                    if args[i] == ':':
                        rules[rule] = args[i+1]
                        i += 2

            else:
                raise SyntaxError("unexpected token %s" % args[i])

        if 'W' not in aliases:
            if not self.sigspace: aliases['W'] = None
            aliases['W'] = compiler.whitespace(self.sigspace_rule)

        if 'T' not in aliases: aliases['T'] = compiler.sequence(['<.term>'])
        if 'E' not in aliases: aliases['E'] = 'expression'

        self.prefix        = prefix        = {}   # unary
        self.infix         = infix         = {}   # binary
        self.postfix       = postfix       = {}   # unary
        self.precircumfix  = precircumfix  = {}   # binary
        self.circumfix     = circumfix     = {}   # unary
        self.postcircumfix = postcircumfix = {}   # binary
        self.ternary       = ternary       = {}   # ternary

        self.args0_ops = {}
        self.args1_ops = {}
        self.args2_ops = {}

        self.precedence_map = dict( 
            (k, i) for i,L in enumerate(reversed(precedence), 1) 
                   for k in L )

        # prepare operators
        operators = []
        for r in rules.keys():
             spec = re.split('('+'|'.join(aliases.keys())+')', r)
             opcnt = 0
             rucnt = 0
             ops = []
             for x in spec:
                 if not x: continue
                 if x not in aliases:
                     if x not in operators: operators.append(x)
                     opcnt += 1
                     ops.append(x)
                 else:
                     rucnt += 1

             #_r = r
             #for a in aliases:
                 #_r = _r.replace(a, ' '+aliases[a]+' ')

             if opcnt == 1: _id = ops[0]
             else: _id = tuple(ops)

             if spec[0] in operators:
                 self.args0_ops[ops[0]] = (r, ops)

                 if   opcnt == 1               : _name = 'prefix'
                 elif opcnt == 2 and rucnt == 2: _name = 'precircumfix'
                 elif opcnt == 2 and rucnt == 1: _name = 'circumfix'
                 else: raise GrammarError(compiler, "cannot handle %(spec)s", spec=spec)

             elif spec[2] in operators:
                 self.args1_ops[ops[0]] = (r, ops)

                 if   opcnt == 1 and rucnt == 1: _name = 'postfix'
                 elif opcnt == 2 and rucnt == 2: _name = 'postcircumfix'
                 elif opcnt == 2 and rucnt == 3: _name = 'ternary'
                 elif opcnt == 1 and rucnt == 2: _name = 'infix'
                 else: raise GrammarError(compiler, "cannot handle %(spec)s", spec=spec)

             #if rules[r] == r: rules[r] = _name
             #locals()[_name][frame[0]] = (r, ops, compiler.sequence(_r.split()))

             getattr(self, _name)[ops[0]] = (r, ops)

        # operators are sorted by length descending, such that an operator like "**"
        # is before "*"
        OPRE = Regex('|'.join([ re.escape(x) for x in sorted(operators, key=lambda a: -len(a)) ]))
        class Op(Rule):
            def match(self, P, s, start, end=None):
                mob = OPRE.match(P, s, start)
                if mob is None: return None
                return P.lex(mob=mob, name='op')
             
           #     P.lex(mob=mob, name='op')
        self.OPRE = Op()

    def tokenizer(self, P, s, start, end=None):
        aliases = self.aliases
        term, ws = aliases['T'], aliases['W']
        
        p = start
        while True:
            if ws is not None:
                mob = ws.match(P, s, p, end)
                if mob is not None: p = mob.end

            mob = self.OPRE.match(P, s, p, end)
            if mob is None:
                mob = term.match(P, s, p, end)
                if mob is None: break

            yield mob
            if mob is not None: p = mob.end

    def match(self, P, s, start, end=None):
        tokens = PeekIterator(self.tokenizer(P, s, start, end))
        next = tokens.next
        peek = tokens.peek

        prefix        = self.prefix 
        infix         = self.infix
        postfix       = self.postfix
        precircumfix  = self.precircumfix
        circumfix     = self.circumfix
        postcircumfix = self.postcircumfix
        ternary       = self.ternary
        rules         = self.rules
        left_assoc    = self.left_assoc
        args0_ops     = self.args0_ops
        args1_ops     = self.args1_ops

        precmap       = self.precedence_map

        with_ops = 'with-ops' in self.flags

        CLOSE_STACK = [ 'bottom' ]
        def _parse(args, min_precedence, nest=0, is_rhs=False):
            while 1:
                if len(args) == 0:  # this is either the start of expr or a rhs
                    mob = next()
                    if mob.name == 'op': # prefix, precircumfix, circumfix
                        op = mob
                        op_s = str(op)

                        if op_s == CLOSE_STACK[-1]:
                            return []

                        if 0:
                          if op_s in precircumfix:
                            rule, ops = precircumfix[op_s]
                            CLOSE_STACK.append(ops[1])
                            lhs = _parse([], 0, nest=nest+1, is_rhs=is_rhs)
                            CLOSE_STACK.pop()
                            op_close = next()
                            op_s = str(op_close)
                            
                            assert op_s == ops[1]
                            rhs = _parse([], precmap[rule], nest=nest, is_rhs=is_rhs)

                            if with_ops: _lexems = [ op ] + lhs + [ op_close ] + rhs
                            else: _lexems = lhs + rhs

                            mob = MatchObject(
                                start = lhs[0].start,
                                end = rhs[-1].end,
                                string = s,
                                lexems = _lexems)

                            args = [ P.lex(name = rules[rule], mob = mob) ]
                            continue

                        if op_s in circumfix:

                            rule, ops = circumfix[op_s]

                            CLOSE_STACK.append(ops[1])
                            arg = _parse([], 0, nest=nest+1, is_rhs=is_rhs)
                            CLOSE_STACK.pop()

                            op_close = next()
                            op_s = str(op_close)
                            
                            assert op_s == ops[1]

                            if with_ops: _lexems = [ op ] + arg + [op_close]
                            else: _lexems = arg

                            mob = MatchObject(
                                start = op.start,
                                end = op_close.end,
                                string = s,
                                lexems = _lexems)

                            #import rpdb2 ; rpdb2.setbreak()
                            args = [ P.lex(name = rules[rule], mob = mob) ]
                            continue

                        if op_s in prefix:
                            rule, ops = prefix[op_s]
                            op_prec = precmap[rule]

                            if is_rhs:
                                if op_prec <= min_precedence:
                                    if left_assoc[rule]: break
                                    if op_prec != min_precedence: break
                                   #if (
                                   #   not left_assoc[rule]
                                   #   and op_prec != min_precedence
                                   #):
                                   # break
                            else:
                                if op_prec < min_precedence: break

                            rhs = _parse([], op_prec, nest=nest, is_rhs=is_rhs)
                            
                            if with_ops: _lexems = [ op ] + rhs
                            else: _lexems = rhs

                            mob = MatchObject(
                                start = op.start,
                                end = rhs[-1].end,
                                string = s,
                                lexems = _lexems)

                            args = [ P.lex(name = rules[rule], mob = mob) ]
                            continue

                    else:   # infix, postfix, ternary
                      args = [ mob ]

                      if 0: # what do we do with ternary ops?
                        if op_s in ternary:
                            rule, ops = ternary[op_s]

                            CLOSE_STACK.append(ops[1])
                            lhs = _parse([], 0, nest=nest+1, is_rhs=is_rhs)
                            CLOSE_STACK.pop()

                            op_close = next()
                            op_s = str(op_close)
                            
                            assert op_s == ops[1]
                            rhs = _parse([], precmap[rule], nest=nest, is_rhs=is_rhs)

                            if with_ops: _lexems = [ mob, op ]
                            else: _lexems = [ mob ]

                            mob = MatchObject(
                                start = lhs[0].start,
                                end = rhs[-1].end,
                                string = s,
                                lexems = [ op ] + lhs + [ op_close ] + rhs)

                            args = [ P.lex(name = rules[rule], mob = mob) ]

                if len(args) == 2:
                     # ternary
                     pass

                if len(args) == 1: # infix at op, ... # this can be lhs or rhs
                    op = peek()
                    if op is StopIteration: break
                    if op.name != 'op': break
                    op_s = str(op)

                    if op_s == CLOSE_STACK[-1]:
                        break

                    rule, ops = args1_ops[op_s]

                    op_prec = precmap[rule]

                    if is_rhs:
                        if op_prec <= min_precedence:
                            if left_assoc[rule]: break
                            if op_prec != min_precedence: break
                            #if (
                                #not left_assoc[rule]
                                #and op_prec != min_precedence
                               #):
                                #break
                    else:
                        if op_prec < min_precedence: break

                    # consume operator
                    next()

                    if op_s in postfix:
                        if with_ops: _lexems = args + [ op ]
                        else: _lexems = args

                        mob = MatchObject(
                            start = args[0].start, end = op.end, string = s,
                            lexems = _lexems)

                        args = [ P.lex(name=rules[rule], mob=mob) ]
                        continue

                    if op_s in prefix:
                        rhs = _parse([], op_prec, nest=nest, is_rhs=is_rhs)
                            
                        if with_ops: _lexems = [ op ] + rhs
                        else: _lexems = rhs

                        mob = MatchObject(
                            start = op.start, end = rhs[-1].end, string = s,
                            lexems = _lexems)

                        args = [ P.lex(name = rules[rule], mob = mob) ]
                        continue

                    if op_s in infix:
                        rhs = _parse([], op_prec, nest, is_rhs=True)

                        if with_ops: _lexems = args + [ op ] + rhs
                        else: _lexems = args + rhs

                        lhs = MatchObject(
                            start = args[0].start,
                            string = s,
                            end = rhs[-1].end,
                            lexems = _lexems)

                        args = [ P.lex(name=rules[rule], mob=lhs) ]
                        continue

                    if op_s in postcircumfix:
                        CLOSE_STACK.append(ops[1])
                        arg = _parse([], 0, nest=nest+1, is_rhs=is_rhs)
                        CLOSE_STACK.pop()

                        op_close = next()
                        op_s = str(op_close)
                            
                        assert op_s == ops[1]

                        if with_ops: _lexems = [ op ] + arg + [op_close]
                        else: _lexems = arg

                        mob = MatchObject(
                                start = op.start,
                                end = op_close.end,
                                string = s,
                                lexems = _lexems)

                        #import rpdb2 ; rpdb2.setbreak()
                        args = [ P.lex(name = rules[rule], mob = mob) ]
                        continue

                    if op_s in ternary:
                        CLOSE_STACK.append(ops[1])
                        lhs = _parse([], 0, nest=nest+1, is_rhs=True)
                        CLOSE_STACK.pop()

                        op_close = next()
                        op_s = str(op_close)
                            
                        assert op_s == ops[1]
                        rhs = _parse([], precmap[rule], nest=nest, is_rhs=is_rhs)

                        if with_ops: _lexems = [ mob, op ]
                        else: _lexems = [ mob ]

                        mob = MatchObject(
                            start = lhs[0].start,
                            end = rhs[-1].end,
                            string = s,
                            lexems = [ op ] + lhs + [ op_close ] + rhs)

            return args
                    
        mob = _parse([], 0)
        return MatchObject(start=mob[0].start, end=mob[-1].end, string=s, lexems=mob)


# The pseudo-code for the algorithm is as follows. The parser starts at function parse_expression. Precedence levels are greater or equal to 0.
# 
# parse_expression ()
#     return parse_expression_1 (parse_primary (), 0)
# 
# parse_expression_1 (lhs, min_precedence)
#     while the next token is a binary operator whose precedence is >= min_precedence
#         op := next token
#         rhs := parse_primary ()
#         while the next token is a binary operator whose precedence is greater
#                  than op's, or a right-associative operator
#                  whose precedence is equal to op's
#             lookahead := next token
#             rhs := parse_expression_1 (rhs, lookahead's precedence)
#         lhs := the result of applying op with operands lhs and rhs
#     return lhs
 
  
