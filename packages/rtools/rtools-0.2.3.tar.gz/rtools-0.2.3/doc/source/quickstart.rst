.. _quickstart:

Quick Start
#################

.. contents::


Running R code
==================

This can be easily done using :func:`~rtools.tools.rcode` function::


    rcode("# whaterver R code ; a = data.frame(c(1,2,3,4), nrow=2)")


Build a matplotlib colormap similar to a R colormap
========================================================


Create a colormap to be used in matplotlib using :class:`~rtools.colormap.RColorMap`. See the code below for an example.


.. plot::
    :include-source:
    :width: 50%

    # build the matplotlib colormap from a R colormap
    from rtools import *
    rmap = RColorMap("heat")    # heat is a valid R colormap
    cmap = rmap.colormap()      # extract the matplotlib colormap

    # use the colormap
    A = np.array(range(100))
    A.shape = (10,10)
    plt.pcolor(A,cmap=cmap, vmin=0, vmax=100)
    plt.colorbar()
 

Wrapper around a S4 class
============================

Suppose, you have a S4 class in R and you want to access an attribute, first,
you need to know the slot name, and then call do_slot method.

The :class:`~rtools.s4.S4Class` class fetches all the slot names and creatse attributes so as to ease the manipulation of S4 object withini python. Consider the following class::


    robject = rcode("""setClass("Person", representation(name = "character", age="numeric")); 
        hadley <- new("Person", name = "Hadley", age = 31)""")


Then, you can use it as an input to the S4Class and access to the attributes as
follows::

    pobject = S4Class(robject)
    pobject.age == 31 # True
    pobject.name


Loading a R package
==============================


You can load a R package and therefore provide access to all its functionalities
using :class:`~rtools.package.RPackage` via the attribute `package`::


    from rtools import RPackage
    rbase = RPackage("base")
    rbase.version
    rbase.package.weekdays
