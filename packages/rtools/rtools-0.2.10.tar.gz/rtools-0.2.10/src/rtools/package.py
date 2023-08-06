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
# $Id: package.py 3 2013-01-25 17:01:27Z cokelaer $
"""Utilities for cnolab.wrapper

:author: Thomas Cokelaer <cokelaer@ebi.ac.uk>
:license: Copyright (c) 2012. GPL

"""
__author__ = """\n""".join(['Thomas Cokelaer <cokelaer@ebi.ac.uk'])
__all__ = ['RPackage', 'biocLite', 'install_packages']

import os
import rpy2
from rpy2 import robjects
from rpy2.robjects import rinterface
from rpy2.robjects.packages import importr
from distutils.version import StrictVersion
 
from error import Rwarning, RRuntimeError
from easydev import Logging

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



def install_packages(query, verbose=True):
    """Install a R package

    :param str query: It can be a valid URL to a R package (tar ball), a CRAN
        package, a path to a R package (tar ball), or simply the directory 
        containing a R package source.

    ::

        >>> rtools.install_packages("path_to_a_valid_Rpackage.tar.gz")
        >>> rtools.install_packages("http://URL_to_a_valid_Rpackage.tar.gz")
        >>> rtools.install_packages("hash") # a CRAN package
        >>> rtools.install_packages("path to a valid R package directory")


    """
    import tempfile
    import urllib2
    import os.path
    from tools import rcode


    filename = None

    # Is it a local file?
    if os.path.exists(query):
        filename = query[:]
    else:
        # if not, is it a valid URL
        try:
            data = urllib2.urlopen(query)
        except ValueError:
            #raise ValueError("Not a valid filename or URL. Maybe you want to use CRAN option to True")
            rcode("""install.packages("%s" )""" % query)
            return 

        # If so, let us download the data in a temp file
        # get new temp filename
        handle = tempfile.NamedTemporaryFile()

        # and save the downloaded data into it. 
        ff = open(handle.name, "w")
        ff.write(data.read())
        ff.close()
        filename = ff.name[:]

    if verbose == True:
        print("Installing %s from %s" % (query, filename))
    rcode("""install.packages("%s", repos=NULL)""" % filename)



def _BoolConvertor(arg):
    if arg == True:
        return "TRUE"
    elif arg == False:
        return "FALSE"
    else:
        raise ValueError

def biocLite(package=None, suppressUpdates=True):
    """Install a package bioconductor

    This function does not work like the R function. Only a few options are
    implmented so far. However, you can use rcode function directly if needed.

    :param str package: name of the bioconductor package to install. If None, no
        package is installed but installed packages are updated.
    :param bool suppressUpdates: updates the dependencies if needed (default is
        False)

    :return: True if update is required or the required package is installed and
        could be imported. False otherwise.

    ::

        >>> from rcode import biocLite
        >>> biocLite("CellNOptR")

    """
    from tools import rcode
    rcode("""source("http://bioconductor.org/biocLite.R");""") 

    # without a package, biocLite performs an update of the installed packages
    if package == None:
        rcode("""biocLite(suppressUpdates=%s) """ % (
            _BoolConvertor(suppressUpdates)))
    else:
        # if not found, no error is returned...
        rcode("""biocLite("%s", suppressUpdates=%s) """ % (
            package,
            _BoolConvertor(suppressUpdates)
        ))
        # ...so we need to check if it is installed
        try:
            importr(package)
        except Exception, e:
            return False
    return True



class RPackage(object):
    """simple class to import a R package and get metainfo

    ::

        from rtools.package import RPackage
        r = RPackage("CellNOptR")
        r.version
        r.package

    # no error returned but only info and error based on logging module.
    """
    def __init__(self, name, require="0.0", install=False, verbose=False):
        """.. rubric:: Constructor

        :param str name: name of a R package installed on your system
        :param str require: the minimal version required. Use valid string
            format such as "1.0.0" or "1.0" 

        The required package is loaded in the constructor. If not found in your
        system, and if install is set to True, it will try to install it from
        bioconductor web site. If not found, nothing happens but the
        :attr:`package` is None. If you want to install a package from source,
        use the install_packages function. 
        """
        self.name = name
        self.package = None
        self.require = require
        self.install = install
        self.logging = Logging("INFO")
        if verbose == True:
             self.logging.level = "INFO"
        else:
            self.logging.level = "ERROR"

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
                self.logging.info("R package %s loaded." % self.name)
            else:
                Rwarning(True)
                self.logging.info("Found %s (version %s) but version %s required." % (self.name, self.version, self.require))
                self.logging.info(import_error % self.name)
                if self.install == True:
                    self.logging.warning("installing %s " % self.name)
                    # installing from bioconductor
                    status = biocLite(self.name)
                    if status == False:
                        self.logging.error("Package %s could not be installed" % self.name)
                else:
                    self.logging.error("could not import %s" % self.name)
                #raise ImportError("Found %s (version %s) but version %s required." % (self.name, self.version, self.require))



        except RRuntimeError:
            print("------could not import the package")
            if self.install == True:
                Rwarning(True)
                self.logging.warning("installing %s " % self.name)
                biocLite(self.name)
                if status == False:
                    self.logging.error("Package %s could not be installed" % self.name)
                Rwarning(False)
            else:
                self.logging.error("could not import %s" % self.name)
                self.logging.info(import_error % self.name)
            #raise ImportError("Could not import R package (%s)." % self.name)
        Rwarning(True)

    def _get_version(self):
        v = robjects.r("""packageVersion("%s")""" % (self.name))[0]
        v = [str(x) for x in v]
        return ".".join(v)
    version = property(_get_version)



