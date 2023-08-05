

# need pylab for that module, which is optional
try:
    import colormap
    from colormap import *
except ImportError, e:
    import warnings
    warnings.warn("colormap module will not work (could not import a package. pylab maybe ?)")

import tools
from tools import *

import package
from package import *

import error
from error import *

import s4
from s4 import *

import plots
from plots import *

