""" test tools module

Most of the tools in this module are tested indirectly in other modules.
"""
from rtools.tools import *

# test Rnames2attributes and rcode----------------------------

@Rnames2attributes   
def rcode2():
    res = rcode("list(a=c(1,2), b=1)")
    return res

@Rnames2attributes   
def rcode3():
    res = rcode("list(a=c(1,2), b=1)")
    # returns nothing on purpose

def test_rcode():
    res = rcode("list(a=c(1,2), b=1)")


def test_names2attributes():
    res = rcode2()
    res.a
    res.b
    res = rcode3()


# test manual tools ---------------------------------------------------------

def test_RManual():
    d = RManualToDocString("base", "abbreviate")
    d.get_docstring()

    buildDocString("base","summary")

    buildDocString("base","dummy")


#test convertor -------------------------------------------------------
# used by test_convertor
class Dummy():
    def __init__(self):
        pass

def test_convertor():
    c = RConvertor()
    c.convert(None)

    # test list of integers and IntVector
    rlist = c.convert([1,1,1])
    rlist2 = c.convert(rlist)

    # test FloatVector
    rlist = c.convert([1.,1.,1.])

    # test complexVector
    rlist = c.convert([1.j,1.,1.])

    # test strVector
    rlist = c.convert(["a","c","b"])

    # test boolVector
    rlist = c.convert([True, False])

    # test boolVector
    Dummy()
    try:
        c.convert([Dummy()])
        assert False
    except NotImplementedError:
        assert True

    # forcetype 
    rlist = c.convert([1.,1.,1.], forcetype=int)



















