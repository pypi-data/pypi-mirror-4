# -*- python -*-
#
#  This file is part of the cnolab package
#
#  Copyright (c) 2011-2012 - EBI - EMBL
#
#  File author(s): Thomas Cokelaer (cokelaer@ebi.ac.uk)
#
#  Distributed under the GPL License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  ModelData website: http://www.ebi.ac.uk/~cokelaer/cnolab
#
##############################################################################
# $Id: tools.py 2193 2012-08-22 21:39:17Z cokelaer $
"""Utilities for cnolab.wrapper

:author: Thomas Cokelaer <cokelaer@ebi.ac.uk>
:license: Copyright (c) 2012. GPL

"""
__author__ = """\n""".join(['Thomas Cokelaer <cokelaer@ebi.ac.uk'])
__all__ = ['RPackage']

import logging
import os
import rpy2
from rpy2 import robjects
from rpy2.robjects import rinterface
from rpy2.robjects.packages import importr
#from rpy2.robjects import r
from distutils.version import StrictVersion
 
from error import Rwarning, RRuntimeError


import_error = """RTOOLS: could not import R package %s. Try to install it. If you have the source file, you can try to type:

    R CMD INSTALL package_name.tar.gz

or if it is available on BioConductor, type:

    source("http://bioconductor.org/biocLite.R")
    biocLite("package_name.tar.gz")

 """ 


class RPackage(object):
    """simple class to import a R package and get metainfo

    ::

        from rtools.package import RPackage
        r = RPackage("CellNOptR")
        r.version
        r.package

    # no error returned but only info and error based on logging module.
    """
    def __init__(self, name, require="0.0"):
        """

        :param str name: name of a R package installed on your system
        :param str require: the minimal version required. Use valid string
            format such as "1.0.0" or "1.0" 
        """
        self.name = name
        self.package = None
        self.require = require
        self.load()

    def load(self):
        """Load the package.

        First, try to load the package. If unsuccessful, return an error 
        RRuntimeError. If successful, check that the version required is large
        enough. If not, return an error with the logging module. The reason for
        not returning an error is that several packages may need to be imported, some of
        them are optional. So, we do not want an error.

        The level of error/verbosity is also related to your logging setup. 

        """
        Rwarning(False)
        try:
            package = importr(self.name)
            if StrictVersion(self.version) >= StrictVersion(self.require):
                self.package = package
                logging.info("R package %s loaded." % self.name)
            else:
                Rwarning(True)
                logging.error("could not import %s" % self.name)
                logging.info("Found %s (version %s) but version %s required." % (self.name, self.version, self.require))
                logging.info(import_error % self.name)
                #raise ImportError("Found %s (version %s) but version %s required." % (self.name, self.version, self.require))
        except RRuntimeError:
            logging.error("could not import %s" % self.name)
            logging.info(import_error % self.name)
            #raise ImportError("Could not import R package (%s)." % self.name)
        Rwarning(True)

    def _get_version(self):
        v = robjects.r("""packageVersion("%s")""" % (self.name))[0]
        v = [str(x) for x in v]
        return ".".join(v)
    version = property(_get_version)



