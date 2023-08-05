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
__all__ = ['RPackage', 'biocLite', 'install_packages']

import logging
import os
import rpy2
from rpy2 import robjects
from rpy2.robjects import rinterface
from rpy2.robjects.packages import importr
from distutils.version import StrictVersion
 
from error import Rwarning, RRuntimeError


import_error = """RTOOLS: could not import R package %s. 

If you have the source file, you can try to type:

    R CMD INSTALL package_name.tar.gz

in a R session. If it is a BioConductor package, type:

    source("http://bioconductor.org/biocLite.R")
    biocLite("package_name.tar.gz")

You can also install it from python::

	from rtools import biocLite
        biocLite("CellNOptR")

 """ 



def install_packages(url, verbose=True):
    """Install a R package from a tar.gz file (local or URL)

    :param str url: Should be a valid URL or filename



    """
    import tempfile
    import urllib2
    import os.path

    filename = None

    # Is it a local file? 
    if os.path.exists(url):
        filename = url[:]
    else:
        # if not, is it a valid URL
        data = urllib2.urlopen(url)

        # If so, let us download the data in a temp file
        # get new temp filename
        handle = tempfile.NamedTemporaryFile()

        # and save the downloaded data into it. 
        ff = open(handle.name, "w")
        ff.write(data.read())
        ff.close()
        filename = ff.name[:]

    from tools import rcode
    if verbose == True:
        print("Installing %s from %s" % (url, filename))

    rcode("""install.packages("%s", repos=NULL)""" % filename)



def _BoolConvertor(arg):
    if arg == True:
        return "TRUE"
    elif arg == False:
        return "FALSE"
    else:
        raise ValueError

def biocLite(package, suppressUpdates=True):
    """Install a package bioconductor

    This function does not work like the R function. Only a few options are
    implmented so far. However, you can use rcode function directly if needed.

    :param str package: name of the bioconductor package to install
    :param bool suppressUpdates: updates the dependencies if needed (default is
        False)


    ::

        >>> from rcode import biocLite
        >>> biocLite("CellNOptR")

    """
    from tools import rcode
    rcode("""source("http://bioconductor.org/biocLite.R");""") 
    rcode("""biocLite("%s", suppressUpdates=%s) """ % (
            package,
            _BoolConvertor(suppressUpdates)
        )
    )



class RPackage(object):
    """simple class to import a R package and get metainfo

    ::

        from rtools.package import RPackage
        r = RPackage("CellNOptR")
        r.version
        r.package

    # no error returned but only info and error based on logging module.
    """
    def __init__(self, name, require="0.0", install=False):
        """

        :param str name: name of a R package installed on your system
        :param str require: the minimal version required. Use valid string
            format such as "1.0.0" or "1.0" 
        """
        self.name = name
        self.package = None
        self.require = require
        self.install = install
        self.load()

    def load(self):
        """Load the package.

        First, try to load the package. If unsuccessful, return an error 
        RRuntimeError. If successful, check that the version required is large
        enough. If not, return an error with the logging module. The reason for
        not returning an error is that several packages may need to be imported, some of
        them are optional. So, we do not want an error.

        If the install attribute is True, then the missing packages are
        installed using biocLite

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
                logging.info("Found %s (version %s) but version %s required." % (self.name, self.version, self.require))
                logging.info(import_error % self.name)
                if self.install == True:
                    logging.warning("installing %s " % self.name)
                    biocLite(self.name)
                else:
                    logging.error("could not import %s" % self.name)
                #raise ImportError("Found %s (version %s) but version %s required." % (self.name, self.version, self.require))



        except RRuntimeError:
            if self.install == True:
                Rwarning(True)
                logging.warning("installing %s " % self.name)
                biocLite(self.name)
                Rwarning(False)
            else:
                logging.error("could not import %s" % self.name)
                logging.info(import_error % self.name)
            #raise ImportError("Could not import R package (%s)." % self.name)
        Rwarning(True)

    def _get_version(self):
        v = robjects.r("""packageVersion("%s")""" % (self.name))[0]
        v = [str(x) for x in v]
        return ".".join(v)
    version = property(_get_version)



