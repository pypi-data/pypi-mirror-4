#
# Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
# Published under New BSD License, see LICENSE.txt for details.
#


from aptk import compile, generate_testsuite, GrammarType
from types import ModuleType
from unittest import TestSuite
import os, sys, inspect
import logging 

log = logging.getLogger('aptk.test')

def collect_doc_strings(x, modname):
    s = ''
    if hasattr(x, '__module__'):
        if x.__module__ != modname: return s

    if hasattr(x, '__doc__'): 
        if x.__doc__: s += x.__doc__

    if hasattr(x, '__dict__'):
        for d in x.__dict__.keys():
            if d.startswith('__'): continue
            if inspect.ismodule(x.__dict__[d]): continue
            y = x.__dict__[d]

            # grammars are individually tested
            if isinstance(y, GrammarType): continue

            s += collect_doc_strings(x.__dict__[d], modname)
    return s

def doctests(filename, suite, test_patterns):
    with open(filename, 'rb') as f:
        grammars = compile(f, type='sphinx', filename=filename)
        for n,g in grammars.items():
            generate_testsuite(g, suite, test_patterns)

def stringtests(string, filename, suite, test_patterns):
    grammars = compile(string, type='sphinx', filename=filename)
    for n,g in grammars.items():
        generate_testsuite(g, suite, test_patterns)

def load_tests(loader, tests, pattern):
  try:
    root = os.path.join(os.path.dirname(__file__), '..')
    files = [ os.path.join(root, 'README.txt') ]

    suite = TestSuite()

    from __main__ import test_patterns

    #if hasattr(loader, 'test_patterns'):
        #test_patterns = loader.test_patterns
    #else:
        #test_patterns = None

    sys.path.insert(0, os.path.join(root, 'examples'))
    sys.path.insert(0, os.path.join(root))
    # python examples
    for d, ds, fs in os.walk(os.path.join(root, 'examples')):
        for f in fs:
            if not f.endswith('.py'): continue
            module = f[:-3]
            #import rpdb2 ; rpdb2.setbreak()
            exec "import %s"%module in globals()

            m = globals()[module]

            for g in dir(m):
                g = getattr(m, g)
                if isinstance(g, GrammarType):
                    generate_testsuite(g, suite, test_patterns)

    # test __doc__ strings:

    for d, ds, fs in os.walk(os.path.join(root, 'aptk')):
        #import rpdb2 ; rpdb2.setbreak()
        G = globals()
        for f in fs:
            if not f.endswith('.py'): continue
            module = f[:-3]
            aptk_mod = 'aptk.'+module
            exec "import %s"%aptk_mod in G
            m = getattr(G['aptk'], module)
            stringtests(collect_doc_strings(m, aptk_mod), f, suite, test_patterns)

            # here test (top-level) grammars of this module
            for g in dir(m):
                g = getattr(m, g)
                if isinstance(g, GrammarType):
                    generate_testsuite(g, suite, test_patterns)


    # rst examples    
    for d, ds, fs in os.walk(os.path.join(root, 'docs')):
        for f in fs:
            if not f.endswith('.rst'): continue
            doctests(os.path.join(d, f), suite, test_patterns)

    # other files
    for f in files:
        doctests(f, suite, test_patterns)

    return suite
  except:
    import traceback
    log.error("error parsing %s: %s" % (f, ''.join(traceback.format_exc())))

    return suite

if __name__ == '__main__':
    from unittest import main
    main()
