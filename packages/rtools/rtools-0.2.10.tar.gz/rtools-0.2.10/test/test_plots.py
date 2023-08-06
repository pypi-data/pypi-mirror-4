from rtools import *
import os


def test_rplots_rcode():

    rp = Rplot(show=True, output="test.png")
    rp.rcode("plot(c(1,2))")
    os.remove("test.png")



def test_rplots_devices():


    for dev in ["png", "jpg", "bmp" ]:
        rp = Rplot(show=True, output="test.%s" % dev)
        rp.rcode("plot(c(1,2))")
        os.remove("test.%s" % dev)



def test_python_code():
    rp = Rplot(show=True, output="test.png")
    rp.rcode("plot(c(1,2))")

    rp = Rplot(show=True, output="test2.png")
    rp.pythoncode("python_func_example()")
    os.remove("test2.png")


