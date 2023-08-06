.. A Parse Toolkit documentation master file, created by
   sphinx-quickstart on Fri Jul 20 01:58:19 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. highlight:: py

aPTK - A Parse Toolkit
======================

aPTK is a Parse Toolkit.  It is useful to write documented grammars similar
to BNF grammar language.

.. highlight:: py

.. .. role:: rule(code)
   :language: aptk
   :class: highlight

.. highlight:: py

Typically you would use it like this::

    from aptk import *

    class AdditionGrammar(Grammar):
        '''This is the grammar of a simple addition.

        <addition> := <operand> <.ws> "+" <.ws> <operand>
        <ws>       := \s*
        <operand>  := \d+
        '''

    class AdditionActions(ParseActions):
        def make_operand(self, p, lexem):
            return int(str(lexem))
            
        def make_addition(self, p, lexem):
            return lexem[0].ast + lexem[1].ast

    tree = parse("5 + 4", AdditionGrammar)
    result = ast("5 + 4", AdditionGrammar, AdditionActions)

The most interesting on the grammars derived from :py:class:`BaseGrammar`
is that they are compiled at compile-time of your python module. This is 
possible due to some python voodoo with metaclasses in :py:mod:`grammar`.

.. toctree::
   :maxdepth: 2

   tutorial
   grammar-syntax
   testing-grammars
   api
   module-reference

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

