import pkg_resources
import logging

#logging.basicConfig(level=logging.ERROR)

try:
    version = pkg_resources.require("rtools")[0].version
except:
    version = "unknown"

logging.info("Importing rtools %s." % version)
logging.info("==========================")

# need pylab for that module, which is optional
try:
    import colormap
    from colormap import *
    raise ImportError
except ImportError, e:
    logging.warning("colormap module will not work (could not import a package. pylab maybe ?)")

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

