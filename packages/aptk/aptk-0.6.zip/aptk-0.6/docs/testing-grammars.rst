Testing of aPTK Grammars
========================

.. highlight:: aptk

Another feature of aPTK is, that you can define your grammar-rule
testcases right in your grammar::

    :grammar AddGrammar1

    <addition> @- <term> "+" <term>
    <term>     #= \d+
    <ws>       := \s*

So far our grammar, now here follow the tests:

1. Test, if addition matches some 
   term::

      <addition> ~~ "5 + 4"

2. Test, if addition matches some term and produces some special
   syntax-tree::

      <addition> ~~ "5 + 4" -> addition( term( '5' ), term( '4' ) )

3. Test, if addition produces right 
   AST::

      <addition> ~~ "5 + 5" --> [5, 5]
   
   In this case default :py:class:`ParseActions` have been used.  To use
   a different parse-action class you can specify it between the "-" and
   "->", for the above you could also write explicitely::

      :parse-actions ParseActions aptk.actions.ParseActions

      <addition> =~ "5 + 5" -ParseActions-> [5, 5]

4. Assert that addition does not match 
   something::

      <addition> !~ "5- 4"


