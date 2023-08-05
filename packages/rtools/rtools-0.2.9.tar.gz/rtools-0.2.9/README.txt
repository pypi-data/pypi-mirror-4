The package **rtools** provides utilities that are of general usage
for developing software that use the RPy2 package. This is not a replacement of
RPy2 but rather an addon to simplify the life of developers
who are using R packages from Python. 

    # check version of the R package base that is installed on your system
    import rtools
    rbase = RPackage('base')
    rbase.version

See `<http://www.ebi.ac.uk/~cokelaer/rtools>`_ for more examples.

