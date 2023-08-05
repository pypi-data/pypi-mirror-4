from rtools.package import *


def test_install_package():
    url = "http://www.ebi.ac.uk/saezrodriguez/cno/downloads/MEIGOR_0.99.3_svn2719.tar.gz"
    install_packages(url)


def _test_biocLite():
    biocLite("CellNOptR")

def test_Rpackage():

    r = RPackage("base")
    r.version
    r.load()


    # load a non-existing package 
    # if does not exist, no error returned on purpose. only logging. so that one can try to import optional packages zitout errors if one is missing.
    r = RPackage("based")
    assert r.package == None

    # load a package that has not the required version
    # again, if does not exist, no error returned on purpose. only logging. so that one can try to import optional packages zitout errors if one is missing.
    r = RPackage("base", require="10000.0")
    assert r.package == None

