
# Redirect path
import os
cdir = os.path.dirname(__file__)
pdir = os.path.join(cdir, "../../admin")
pdir = os.path.abspath(pdir)

__path__ = [pdir] + __path__[:]

from cellnopt.admin.__init__ import *
del cdir
del pdir
