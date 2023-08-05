
# Redirect path
import os
cdir = os.path.dirname(__file__)
pdir = os.path.join(cdir, "../../data")
pdir = os.path.abspath(pdir)

__path__ = [pdir] + __path__[:]

from cellnopt.data.__init__ import *
del cdir
del pdir
