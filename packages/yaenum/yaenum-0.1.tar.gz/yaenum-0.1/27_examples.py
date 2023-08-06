#!/usr/bin/python3

from yaenum27 import Enum, BitMaskEnum, UniqueEnum, enum

class Color(BitMaskEnum):
    black  = enum('midnight', '#000', value=0)
    red    = enum('sunset',   '#001', value=1)
    green  = enum('emerald',  '#010', value=2)
    blue   = enum('sky',      '#100', value=4)

    def __init__(yo, value):
        "value, args and kws are saved as value, _args and _kws"
        yo.desc, yo.code = yo._args

    def describe(yo, noun):
        return "%s %s" % (yo.desc, noun)

print Color
print Color.green
print repr(Color.green)
print Color.green.describe('glow')

print "Enum.create('IceCream', 'chocolate vanilla strawberry') -->   ", Enum.create('IceCream', 'chocolate vanilla strawberry')  #return class discarded
Enum.create('IceCream', 'chocolate vanilla strawberry', register=globals())  #class stuffed into globals
print "IceCream -->   ", IceCream
print "IceCream.strawberry -->", IceCream.strawberry, repr(IceCream.strawberry)

import sys
Enum.create('MoreIceCream', 'cherry rockyroad coconut', type=IceCream, register=sys.modules)   # can even subclass this way
from MoreIceCream import *
print "cherry -->   ", cherry
print
