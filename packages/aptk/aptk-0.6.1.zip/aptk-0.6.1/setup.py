from distutils.core import setup
from aptk.__version__ import release
import sys, os

#if sys.argv[1] == 'test':
#    sys.path.insert(0, os.path.dirname(__file__))
#    import aptk
#    r = aptk._test(aptk)
#    failed, attempted = r
#    if not failed:
#        sys.stdout.write("%s tests ok\n"%attempted)
 
#else:    
if 1:
    setup(
      name         = 'aptk',
      version      = release,
      packages     = ['aptk'],
      author       = 'Kay-Uwe (Kiwi) Lorenz',
      author_email = "kiwi@franka.dyndns.org",
      url          = 'http://aptk.readthedocs.org',
      description  = "A Parse Toolkit.  Create well documented grammars.",

      license = "New BSD License",
      )
