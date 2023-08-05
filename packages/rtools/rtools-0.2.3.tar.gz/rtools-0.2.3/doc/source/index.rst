

#############################
RTOOLS documentation
#############################

Overview and Installation
##############################

`rtools <http://pypi.python.org/pypi/rtools>`_  is a python package that provides utilities related to the R language. It is mostly built upon RPY2. It is attended to simplify life of developers who are using R packages from python.


**rtools** is used by the `cnolab.wrapper <http://pypi.python.org/pypi/cnolab.wrapper`_ to provide pytho interface to `cellnopt <http://www.cellnopt.org>`_ R packages and `pymeigo <http://pipi.python.org/pypi/pymeigo`_.


.. _installation:

Installation
===============


**rtools** is available on `PyPi <http://pypi.python.org/pypi/rtools>`_. The following command should install **rtools** and its dependencies automatically:: 

    easy_install rtools

or::

    pip install rtools


.. note:: to use *easy_install* or *pip* you may need root permission (under linux, use *sudo*)

.. note:: If you do not have root permission, you can also use a virtual
   environment with virtualenv::


        virtualenv tempdirectory
        cd tempdirectory
        source bin/activate
        easy_install rtools





User guide
##################


.. toctree::
    :maxdepth: 2
    :numbered:

    quickstart.rst


References
##################


.. toctree::
    :maxdepth: 2
    :numbered:

    references

