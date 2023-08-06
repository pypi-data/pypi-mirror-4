#
# Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
# Published under New BSD License, see LICENSE.txt for details.
#
r"""

.. grammar off

.. maybe use GrammarGrammar as example for defining a grammar.
   
   In the following there will be explained how the syntax of a grammar is.
   It is explained on a grammar describing the syntax of the grammar itself.
   Maybe there are done few things more complicated than it could be done, but
   then it is for the reason to describe a grammar language feature.

aPTK Grammar Syntax
===================

.. highlight:: aptk

Syntax of aPTK Grammars are oriented on BNF and a bit on Perl6 grammars.

A grammar consists of production rules and statements.  Statements 
influence parsing and/or interpretation of the parsed.  Optionally you may
add assertions, to prove, that your rules meet your expectations.


General
-------

All rules and statements have to start on same indentation level. If you
want to continue a rule or statement on next line, you can do so by
indenting next line a bit more than the line, where your rule or statement
started::

  :grammar grammar

  grammar := [ <statement> 
             | <production-rule>
             | <test-assertion>
             ]*

  ws      := \s+

Lines abore define new grammar named "grammar" and define first rule,
the default entry point of the grammar.
     
Statements
----------

A statement is a line, which starts with a ":".  There are following
statements supported:

.. _statement-grammar:

:rule:`:grammar <name> [ extends [ <grammar-name> ]+ ]?`
    Define a new grammar named `<name>`, which extends grammars `<grammar-name>`. 
    If you do not pass `<grammar-name>`, it defaults to :py:class:`Grammar`

    This statement is available in contexts where you not have 
    predefined a grammar, as for example if you define your grammar as
    python class.

    Examples for :rule:`:grammar`::

        :grammar very-simple-grammar

        :grammar another-grammar extends very-simple-grammar

        :grammar x extends aptk.BaseGrammar


.. _statement-parse-actions:

:rule:`:parse-actions [ <name> <python-name> ]+`
    Define a ParseActions class (or module), which can be later used
    in tests (or simply referenced by its name, when creating a parser)::

        :parse-actions my_module.MyParseAction

    This statements imports parse-actions into your grammar, that you
    can make use of it in test assertions::

        <some-rule> ~~ "some string" -MyParseAction-> some ast


.. _statement-parse-action-map:

:rule:`:parse-action-map [ <name> <method-name> ]+`
    Map `<string>` to `<method-name>`, which is expected to exist in
    parse-actions passed to parser. After mapping `<string>` to 
    `<method-name>`, you can use `<string>=` as 
    operator in production rule, to assign a parse-action::

        :parse-action-map
            "foo" make_foo

        some-rule  foo= "some right-hand side"

    These parse-action-map become handy, if there is an action which is done 
    for more than one capture.


.. _statement-sigspace:

:rule:`:sigspace [ <non-terminal> | <terminal> ]`
    Set rule for significant whitespace.


.. _statement-sigspace:

:rule:`:args-of <custom-rule-name> [ [ <arg-flag> ]+ | <callable> ]`
    Specify how args of a complex custom rule are parsed::

        arg-flag := "string" | "capturing" | "non-capturing" | "regex" |
                       "raw" | "slashed-regex" | "char-class"

        callable := <module-name> "." <>


Production Rules
----------------

A production rule consists of a name, an operator, and a statement on the 
right hand side::

    production-rule := <token-def> | <rule-def>

    token-name := "{" <name> "}" | <name>
    rule-name  := "<" <name> ">" | <name>

You can have following operators::

This is the formal definition of production rules, here follow
detailed explanations with examples:

* :ref:`token-def`


.. _token-def:

Tokens
~~~~~~

Tokens are a special form of production rules::

    token-def  :-  <token-name> "=" <token-value>


:rule:`<token-name>`
    Can be any name. All characters except whitespace, with two limitations:

    * :rule:`<token-name>` must not start and end with a ":" or be enclosed by
      "{:" and ":}
    * :rule:`<token-name>` may be optionally be enclosed by "{" and "}" for better
      readability.

:rule:`<token-value>`
    :rule:`<token-value>` is interpreted as regular expression as described in :mod:`re`.

Tokens are simply macros where ``{<token-name>}`` is replaced by :rule:`<token-value>` such
that quantifications of tokens hold::

    foo1 = bar
    foo2 = [bar]
    foo3 = a
    foo4 = \n
    foo5 = [ bar ]*

    <some-rule-1> := here\x20is\x20{foo1}*
    <some-rule-2> := here\x20is\x20{foo2}*
    <some-rule-3> := here\x20is\x20{foo3}*
    <some-rule-4> := here\x20is\x20{foo4}*
    <some-rule-5> := here\x20is\x20{:foo1:}*
    <some-rule-6> := here\x20is\x20[{:foo1:}{:foo4:]]*
    <some-rule-7> := here\x20is\x20{foo5}

Token replacement creates following rules from this, before really parsing them::

    <some-rule-1> := here\x20is\x20(?:bar)*
    <some-rule-2> := here\x20is\x20[bar]*
    <some-rule-3> := here\x20is\x20a*
    <some-rule-4> := here\x20is\x20\n*
    <some-rule-5> := here\x20is\x20bar*
    <some-rule-6> := here\x20is\x20[bar\n]*
    <some-rule-7> := here\x20is\x20(?:(?:bar)*)

You see that tokens are used in a way that the quantification after the 
token always quantifies the entire token not like in :rule:`<some-rule-5>` where
simply the value of the token was substituted.

So you can also let your token be exanded with ``{:<token-name>:}`` syntax, 
which is simply expanding the value of tokens without taking care of 
grouping for clean quantifications.  This expansions are intended to be
used e.g. as character-classes (this is also the reason for the choice of
syntax), as seen in :rule:`<some-rule-6>`, but maybe there are other use cases.

In :rule:`<some-rule-7>` there is used :rule:`{foo5}` token. Where you see
a special notation of::

   foo5 = [ bar ]*

In tokens a "[" sorrounded by whitespace is replaced by "(?:" and a "]" surrounded
by whitespace or followed by a quantifier like "?", "*", "+" or "{a,b}" is replaced
by ")" and the optional quantifier.  This is for convenience and better readability
of the token rule. Do not confuse with::

   foo6 = [bar]*

Because::

   {foo5} ~~ barbar

   {foo6} ~~ brarab

   {foo5} !~ brarab


Rules
~~~~~

Formally rules are defined as this::

    rule-def     :- <rule-name> <operator> <alternatives>
    alternatives :- <sequence> [ {or} <sequence> ]
    sequence     :- [ <non-terminal> | <terminal> ]
    non-terminal := [ <capturing> | <non-capturing> 
                    | <sub-rule ] <quantification>?

    terminal     := <string> | <regex>

    quantification :=  "?" | "*" | "+" | "{" \d* "," \d* "}"

    operator := <token-op> | <backtracking-op> | <non-backtracking-op> 
              | <backtracking-sigspace-op> | <non-backtracking-sigspace-op> 



    token-op                     := "="
    backtracking-op              := ":" <parse-action> "="
    backtracking-sigspace-op     := ":" <parse-action> "-"
    non-backtracking-op          := <parse-action> "="
    non-backtracking-sigspace-op := <parse-action> "-"

    parse-action                 := ":" | [^=]+

A production rule has the form::

    :sigspace {ws}
    after-ws          = (?<=\s)
    before-ws         = (?=\s)
    or                = {after-ws} \| {before-ws}

    <production-rule> ::- <non-terminal> <rule-op> <alternatives>

    <alternatives>    ::- <sequence> [ {or} <sequence> ]*

    <sequence>        ::= [ <non-terminal> | <terminal> ]+

    <terminal>        ::= <string> | <regex>

    <non-terminal>    ::= [ <capturing> | <non-capturing> | <sub-rule> 
                          ] <quantification>?

    <quantification>  ::= "?" | "*" | "+" | "{" \d* "," \d* "}"

:rule:`<non-terminal>`
    May be enclosed by "<", ">" for beeing closer to BNF or better 
    readability, but this is not neccesserily needed.  So::

        <foo> ::= "bar"

    is equivalent to::

        foo   ::= "bar"

:rule:`<rule-op>`
    This is a tricky thing. Usually you will use ":=".  But you
    can use any :rule:`<parse-action>=` for it. See also :ref:`parse-actions`.

    There are more flavors of the `<rule-op>`, for specifying significant
    space and backtracking on failure:

    =========== =========================================================
      rule-op    description
    =========== =========================================================
        =        Specify a token, which can be used later as macro.
       :=        Normal rule.
       ::=       Backtracking rule.
       :foo=     Backtracking rule calling "foo" method from ParseActions
       foo=      Normal rule calling "foo" method from ParseActions
       :-        Normal rule using significant whitespace
       ::-       Backtracking rule using significant whitespace.
    =========== =========================================================

    In short:

    * a rule with a :rule:`<rule-op>` with a preceding ":", does 
      backtracking on failure.

    * a rule with a :rule:`<rule-op>` using a "-" instead of "=" has
      significant whitespace

:rule:`<string>`
    May be a double-quoted or a single-quoted string. Like::

        "foo" "foo\n" "foo\"" 'foo"bar"' 'bar\''

    This is a terminal in terms of grammars.

:rule:`<regex>`
    Anything, which is not anything else listed here is interpreted as
    regular expression like defined in :mod:`re`.

:rule:`<non-capturing>`
    From syntactical point of view it is a ":rule:`<.capturing>`" rule.  So 
    the same like a capturing rule, except you have a "." right behind the
    opening "<".

    No-capturing rules pass their captured children to the parental rule, 
    which combines the children of all non-capturing childrens to its own 
    list of children.

    Examples::

        <.simple-rule> <.rule-with-arg:foo> <.ext-rule{ here is more }>

:rule:`<capturing>`
    Capturing rule has three syntactical flavours::

        <ws>        ::= \s+

        <simple>    ::= "<" <non-terminal-name> ">"

        <with-arg>  ::= "<" <non-terminal-name> ":" <arg>  ">"

        <with-args> ::= "<" <non-terminal-name> "{" [ <.ws> <extarg> ]* <.ws> "}>"

        <arg>       ::= (?:\\\\|\\>|[^>])*

        <extarg>    ::= (?!\}>\s) (?!\}>$) [^\s]+

    Where `name` is the name of another non-terminal. The two extended versions
    of rule-calls are for invoking custom rules, which do more than simply 
    parsing sequencenses or alternatives.

    Please note for :rule:`<with-args>` rules:


Backtracking
------------

Explain here how backtracking works

Significant Whitespace
----------------------

Explain here how significant whitespace works.


Test Assertions
---------------


Assert, that your rules match
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to assert, that a rule matches a certain string you can add 
an assertion::

    <my-rule> ~~ "foo"


Assert, that your rules do not match
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to assert that a rule does not match some string you can add 
an assertion::

    <my-rule> !~ "foo"


Assert, that your rules produce some expected syntax tree
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to assert that a rule produces some syntax tree you can add
an assertion::

    <my-rule> ~~ "foo" -> my-rule("foo")


Token and exact match
~~~~~~~~~~~~~~~~~~~~~

Difference between `token match` and `exact match` is, that in `token
matches` whitespace is ignored and only non-whitespace tokens are compared.
In `exact match` there is compared complete string::

    <my-rule> ~~ "something" ->
        In token
            match only
             non-whitespace          tokens
         are considered for
                   comparison.

    <my-rule> =~ "something" --> "Must output exact this string"


Multiline input
~~~~~~~~~~~~~~~

You can specify multiline input (or expected output) by lines preceded by
"``| ``"::

    <my-rule> ~~
        | first line
        | second line
        |
        | And a line after an
        | empty line
        ->
        | Same for
        | expected output.
        




For testing your grammar you can setup test assertions for your rules::

    <my-rule> ~~ "foo"
    <my-rule> !~ "foo"
    <my-rule> ~~ "foo" -> my-rule("foo")
    <my-rule> =~ "foo" -> "foo"
    <my-rule> =~
        | a really
        | long, long
        | text.
        | 
        | with another paragraph
        -> here
           is what
           I expect
           to be the ast's output.

    <my-rule> =~ "foo" -MyParseActions-> [ 'f', 'o', 'o' ]

Formally test assertions are created with following syntax::

    <test-assertion> ::= <test-rule> <test-op> <string-to-match> [ <ast-op> <expected-output> ]?

    <test-rule> ::= "<" <non-terminal-name> ">"

    <test-op>   ::= (?P<token-match>~~)|(?P<not-match>!~)|(?P<equal-match>=~)

    <string-to-match>   ::= <quoted-string> | <multi-line-string>
    <multi-line-string> ::= [ \s* [ \|(?P<line>\n) | \|\s <line> ] ]+

    <ast-op>    ::= -> | -(?P<parse-actions-name>\w+)->

    <expected-output> ::= <quoted-string> | <multi-line-string> | <tokens>





"""

# vim: ft=rst
