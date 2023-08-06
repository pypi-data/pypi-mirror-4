aptk - A Parse Toolkit
======================

This is a module for creating parsers from grammars.  aPTK targets to make
this in a very "documented" way.  So you can define the grammar in doc-string
of your grammar class or even in your reStructuredText documentation.

.. highlight:: aptk

A simple example of a greeting parser::

  :grammar GreetingGrammar

  <greeting>        := <greeting-clause> <.ws> <greeted>
  <ws>              := \s+
  <greeting-clause> := "hello" | "hi"
  <greeted>         := \w+

This will create a class named `GreetingGrammar`.  First rule in the 
grammar will be used as start-rule for a normal parsing.  Parsing a 
rule, will result in a ParseTree.  Here follows an example of rule
``<greeting>`` matching "hello world"::

  <greeting> ~~ "hello world"
             -> greeting(
                  greeting-clause( 'hello' ), 
                  greeted( 'world' ) 
                )

Actually what you see above is a test assertion for applying rule greeting
to string "hello world", what is expected to result in the parse-tree
displayed above.

But read more in `aptk's documentation`_.

.. _aptk's documentation: http://aptk.readthedocs.org

Download
--------

You can download this package from PyPI_.

.. _PyPI:: http://pypi.python.org/pypi/aptk#downloads

.. highlight:: bash

Or install it with easy_install::

    easy_install -U aptk
    
or get the the source from source code repository from bitbucket.org::

    $ hg clone https://bitbucket.org/klorenz/aptk


Building Documentation
----------------------

For building documentation you need sphinx, you can get it using::

    $ easy_install -U Sphinx

Then you can::

    $ cd docs
    $ make html
    $ firefox _build/html/index.html


License
-------

Licensed under New BSD License, see LICENSE.txt.


Release Notes
-------------

======= =================================================================
Version Notes
======= =================================================================
0.5.7   add comments

0.5.4   first tests for postcircumfix pass, more tests, cleaned code a bit

0.5.3   Added operation precedence parser. Pretty simple yet, but supports
        infix, postfix, prefix, circumfix operations. postcircumfix is
        also implemented but not tested at all others are partly tested.

0.5     Starting with version 0.5, which shall indicate, that there is 
        still a lot to do.

        Especially documentation is far from complete and it contains 
        some passages, which are already outdated.

        Next releases will focus on documentation and testing and adding 
        an operator precendence parser.

======= =================================================================
