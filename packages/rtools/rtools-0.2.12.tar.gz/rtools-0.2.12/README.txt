The package **rtools** provides utilities that are of general usage
for developing software that use the RPy2 package. This is not a replacement of
RPy2 but rather an addon to simplify the life of developers
who are using R packages from Python. 

::

    # check version of the R package 'base'
    import rtools
    rbase = rtools.RPackage('base')
    rbase.version

See `<http://packages.python.org/rtools/>`_ for more examples.

