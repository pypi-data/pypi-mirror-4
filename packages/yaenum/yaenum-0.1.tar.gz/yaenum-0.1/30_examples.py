#!/usr/bin/python3

from yaenum import Enum, BitMaskEnum, UniqueEnum, enum

class Color(Enum):
    "basic red/green/blue"
    black
    red
    green
    blue

print("Color -->   ", Color)
print("Color.green -->   ", Color.green)
print("Color(2) -->   ", Color(2))
print("Color('green') -->   ", Color('green'))
print("repr(Color.green) -->   ", repr(Color.green))
print()

class MoreColor(Color):
    "and some cyan/magenta/yellow"
    cyan
    magenta
    yellow

print("MoreColor -->   ", MoreColor)
print("MoreColor.red -->   ", MoreColor.red)
print("MoreColor(1) -->   ", MoreColor(1))
print("MoreColor('red') -->   ", MoreColor('red'))
print("repr(MoreColor.red) -->   ", repr(MoreColor.red))
print()

class Errors(Enum):
    missing
    closed
    corrupted
    modified

print("Errors -->   ", Errors)
print("Errors.closed -->   ", Errors.closed)
print("Errors(1) -->   ", Errors(1))
print("Errors('closed') -->   ", Errors('closed'))
print("repr(Errors.closed) -->   ", repr(Errors.closed))
print()

print("Color.red in Color -->   ", Color.red in Color)
print("MoreColor.magenta in MoreColor -->   ", MoreColor.magenta in MoreColor)
print("Color.red in MoreColor -->   ", Color.red in MoreColor)
print("Color.red == MoreColor.red -->   ", Color.red == MoreColor.red)
print()

print("(Errors.closed in MoreColor) -->   ", (Errors.closed in MoreColor))
print("(Errors.closed in Color) -->   ", (Errors.closed in Color))
print("(Errors.closed == Color.red) -->   ", (Errors.closed == Color.red))
print("(Errors.closed == MoreColor.red) -->   ", (Errors.closed == MoreColor.red))
print()

class Status(BitMaskEnum):
    has_memo
    binary
    increment
    unicoded

print("Status -->   ", Status)
print("for e in Status:")
for e in Status:
    print("    repr(e) -->   ", repr(e))
print("Status.binary | Status.increment -->   ", Status.binary | Status.increment)
print("Status(5) -->   ", Status(5))
print("Status('binary|increment') -->   ", Status('binary|increment'))
print("repr(Status(5)) -->   ", repr(Status(5)))
print()

class Position(UniqueEnum):
    LEFT
    RIGHT
    TOP
    BOTTOM

print("Position -->   ", Position)
print("Position.TOP -->   ", Position.TOP)
print("Position('top') -->   ", Position('top'))
print("Position('TOP') -->   ", Position('TOP'))
print("repr(Position.TOP) -->   ", repr(Position.TOP))
print()

print("Enum.create('IceCream', 'chocolate vanilla strawberry') -->   ", Enum.create('IceCream', 'chocolate vanilla strawberry'))  #return class discarded
Enum.create('IceCream', 'chocolate vanilla strawberry', register=globals())  #class stuffed into globals
print("IceCream -->   ", IceCream)

import sys
Enum.create('MoreIceCream', 'cherry rockyroad coconut', type=IceCream, register=sys.modules)   # can even subclass this way
from MoreIceCream import *
print("cherry -->   ", cherry)
print()

class Color(BitMaskEnum):
    black  = enum('midnight', '#000', value=0)
    red    = enum('sunset',   '#001')
    green  = enum('emerald',  '#010')
    blue   = enum('sky',      '#100')

    def __init__(yo, value):
        "value, *args and **kws are automatically saved on the instance as value, _args, and _kws"
        yo.desc, yo.code = yo._args

    def describe(yo, noun):
        return "%s %s" % (yo.desc, noun)

print(Color)
print(Color.green)
print(repr(Color.green))
print(Color.green.describe('glow'))
