from rtools.package import *



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

