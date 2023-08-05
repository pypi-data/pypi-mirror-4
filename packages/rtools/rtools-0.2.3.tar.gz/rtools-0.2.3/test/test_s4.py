from rtools import *

def test_s4class():

    # need a proper R class from a base package
    robject = rcode("""setClass("Person", representation(name = "character", age ="numeric")); hadley <- new("Person", name = "Hadley", age = 31)""")
    S4Class(robject).age == 31
    S4Class(robject).name == "Hadley"
