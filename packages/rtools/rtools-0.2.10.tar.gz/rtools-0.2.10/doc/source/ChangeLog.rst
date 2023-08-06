Whats' new, what has changed
================================


Revision 0.2
-------------------

* 0.2.10:
    * add proper logging in package module
    * package.install_package function can install source package, R source dircectory,
      CRAN package, URL tar ball
    * package.biocLite improvement
    * some cleanup in package.RPackage module
* 0.2.9: improve robustness of the setAttributes function that recursively set attributes
* 0.2.8:
	* add :func:`install_packages` function to install package from URL (or local)
	* Fix typo in __init__ that raise an error systematically
	* biocLite: add doc, and remove update by default 
* 0.2.7: add :func:`rtools.package.biocLite` function to install a package automatically.
* 0.2.6: make module colormap optional in the __init__ to prevent error  if pylab not installed.
* 0.2.4: add :mod:`rtools.plots` module.
* 0.2.3: add list into the convertor.
* 0.2.2: add simple S4Class in s4 module (+test+doc). Update tutorial to add rcode, Rpackage, S4class examples.
* 0.2.1: finalising documentation, and tests. Add rcode function in tools.
* 0.2.0: add :mod:`rtools.error` module, :mod:`rtools.package` modules

Revision 0.1
------------------- 

* 0.1.0: add Colormap class to convert R colormap to matplotlib colormap




