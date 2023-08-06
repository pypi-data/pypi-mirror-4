from __future__ import division

from .convolve import *
from . import iraf_frame

from .version import *

try:
    import stsci.tools.tester
    def test(*args,**kwds):
        stsci.tools.tester.test(modname=__name__, *args, **kwds)
except ImportError:
    pass

