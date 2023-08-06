#!/usr/bin/python3
"""\
=========
Copyright
=========
    - Copyright: 2012 Ethan Furman -- All rights reserved.
    - Author: Ethan Furman
    - Version: 0.1
    - Contact: ethan@stoneleaf.us

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    - Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    - Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.

    - Neither the name of Ethan Furman nor the names of its contributors may
      be used to endorse or promote products derived from this software
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY Ethan Furman ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL Ethan Furman BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import unittest
from yaenum import Enum, BitMaskEnum, UniqueEnum, InvalidEnum, enum

class Test_Enum(unittest.TestCase):

    def test_magic_enum(yo):
        class Color(Enum):
            BLACK
            RED
            GREEN
            BLUE
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 4)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE], lst)
        for i, color in enumerate('BLACK RED GREEN BLUE'.split()):
            enum = Color(color)
            yo.assertEqual(enum.value, i)
            yo.assertEqual(enum._name, color)
            yo.assertIn(enum, Color)
            yo.assertEqual(lst.index(enum), i)
            yo.assertEqual(Color(i), i)
        class Color(Enum):
            BLACK
            RED
            GREEN = 7
            BLUE
            PURPLE
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 5)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE, Color.PURPLE], lst)
        for i, color in zip([0, 1, 7, 8, 9], 'BLACK RED GREEN BLUE PURPLE'.split()):
            enum = Color(color)
            yo.assertEqual(enum.value, i)
            yo.assertEqual(enum._name, color)
            yo.assertIn(enum, Color)
            yo.assertEqual(Color(i), i)

    def test_magic_flag(yo):
        class Color(BitMaskEnum):
            BLACK = 0
            RED
            GREEN
            BLUE
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 4, Color)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE], lst)
        for i, color in zip([0, 1, 2, 4], 'BLACK RED GREEN BLUE'.split()):
            enum = Color(color)
            yo.assertEqual(enum.value, i)
            yo.assertEqual(enum._name, color)
            yo.assertIn(enum, Color)
            yo.assertEqual(Color(i), i)
        class Color(BitMaskEnum):
            BLACK  = 0
            RED
            GREEN
            BLUE   = 3
            PURPLE
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 5, Color)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE, Color.PURPLE], lst)
        for i, color in zip([0, 1, 2, 3, 4], 'BLACK RED GREEN BLUE PURPLE'.split()):
            enum = Color(color)
            yo.assertEqual(enum.value, i)
            yo.assertEqual(enum._name, color)
            yo.assertIn(enum, Color)
            yo.assertEqual(Color(i), i)

    def test_magic_unique(yo):
        class Color(UniqueEnum):
            BLACK
            RED
            GREEN
            BLUE
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 4)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE], lst)
        for i, color in enumerate('black red green blue'.split()):
            enum = Color(color)
            yo.assertEqual(enum.value, color)
            yo.assertEqual(enum._name, color.upper())
            yo.assertIn(enum, Color)
            yo.assertEqual(lst.index(enum), i)
            yo.assertEqual(Color(color), color)
        class Color(UniqueEnum):
            BLACK
            RED
            GREEN = 'verde'
            BLUE
            PURPLE
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 5)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE, Color.PURPLE], lst)
        for i, color in enumerate('black red verde blue purple'.split()):
            enum = Color(color)
            yo.assertEqual(enum.value, color)
            yo.assertEqual(enum._name, 'GREEN' if color == 'verde' else color.upper())
            yo.assertIn(enum, Color)
            yo.assertEqual(lst.index(enum), i)
            yo.assertEqual(Color(color), color)

    def test_semi_magic_enum(yo):
        class Color(Enum):
            BLACK = enum('midnight')
            RED   = enum('blood')
            GREEN = enum('emerald')
            BLUE  = enum('sky')
            def __init__(yo, value):
                adj, = yo._args
                yo.adjective = adj
            def desc(yo):
                return 'the %s moon' % (yo.adjective,)
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 4)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE], lst)
        for i, color in enumerate('BLACK RED GREEN BLUE'.split()):
            e = Color(color)
            yo.assertEqual(e.value, i)
            yo.assertEqual(e._name, color)
            yo.assertIn(e, Color)
            yo.assertEqual(lst.index(e), i)
            yo.assertEqual(Color(i), i)
        for adj, e in zip(('midnight', 'blood', 'emerald', 'sky'), Color):
            yo.assertEqual(e.desc(), 'the %s moon' % adj)
        class Color(Enum):
            BLACK  = enum('midnight')
            RED    = enum('blood')
            GREEN  = enum('emerald', value=7)
            BLUE   = enum('sky')
            PURPLE = enum('people eater')
            def __init__(yo, value):
                adj ,= yo._args
                yo.adjective = adj
            def desc(yo):
                return 'the %s moon' % (yo.adjective,)
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 5)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE, Color.PURPLE], lst)
        for i, color in zip([0, 1, 7, 8, 9], 'BLACK RED GREEN BLUE PURPLE'.split()):
            e = Color(color)
            yo.assertEqual(e.value, i)
            yo.assertEqual(e._name, color)
            yo.assertIn(e, Color)
            yo.assertEqual(Color(i), i)
        for adj, e in zip(('midnight', 'blood', 'emerald', 'sky', 'people eater'), Color):
            yo.assertEqual(e.desc(), 'the %s moon' % adj)

    def test_semi_magic_flag(yo):
        class Color(BitMaskEnum):
            BLACK = enum('midnight', value=0)
            RED   = enum('blood')
            GREEN = enum('emerald')
            BLUE  = enum('sky')
            def __init__(yo, value):
                adj, = yo._args
                yo.adjective = adj
            def desc(yo):
                return 'the %s moon' % (yo.adjective,)
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 4)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE], lst)
        for i, color in zip((0, 1, 2, 4), 'BLACK RED GREEN BLUE'.split()):
            e = Color(color)
            yo.assertEqual(e.value, i)
            yo.assertEqual(e._name, color)
            yo.assertIn(e, Color)
            yo.assertEqual(Color(i), i)
        for adj, e in zip(('midnight', 'blood', 'emerald', 'sky'), Color):
            yo.assertEqual(e.desc(), 'the %s moon' % adj)
        class Color(Enum):
            BLACK  = enum('midnight', value=0)
            RED    = enum('blood')
            GREEN  = enum('emerald')
            BLUE   = enum('sky', value=3)
            PURPLE = enum('people eater')
            def __init__(yo, value):
                adj ,= yo._args
                yo.adjective = adj
            def desc(yo):
                return 'the %s moon' % (yo.adjective,)
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 5)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE, Color.PURPLE], lst)
        for i, color in zip([0, 1, 2, 3, 4], 'BLACK RED GREEN BLUE PURPLE'.split()):
            e = Color(color)
            yo.assertEqual(e.value, i)
            yo.assertEqual(e._name, color)
            yo.assertIn(e, Color)
            yo.assertEqual(Color(i), i)
        for adj, e in zip(('midnight', 'blood', 'emerald', 'sky', 'people eater'), Color):
            yo.assertEqual(e.desc(), 'the %s moon' % adj)

    def test_semi_magic_unique(yo):
        class Color(UniqueEnum):
            BLACK = enum('midnight')
            RED   = enum('blood')
            GREEN = enum('emerald')
            BLUE  = enum('sky')
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 4)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE], lst)
        for i, color in enumerate('black red green blue'.split()):
            e = Color(color)
            yo.assertEqual(e.value, color)
            yo.assertEqual(e._name, color.upper())
            yo.assertIn(e, Color)
            yo.assertEqual(lst.index(e), i)
            yo.assertEqual(Color(color), color)
        class Color(UniqueEnum):
            BLACK  = enum('midnight')
            RED    = enum('blood')
            GREEN  = enum('emerald', value='verde')
            BLUE   = enum('sky')
            PURPLE = enum('people-eater')
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 5)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE, Color.PURPLE], lst)
        for i, color in enumerate('black red verde blue purple'.split()):
            e = Color(color)
            yo.assertEqual(e.value, color)
            yo.assertEqual(e._name, 'GREEN' if color == 'verde' else color.upper())
            yo.assertIn(e, Color)
            yo.assertEqual(lst.index(e), i)
            yo.assertEqual(Color(color), color)

    def test_mundane_enum(yo):
        class Color(Enum):
            BLACK = enum('midnight', value=0)
            RED   = enum('blood', value=1)
            GREEN = enum('emerald', value=2)
            BLUE  = enum('sky', value=3)
            def __init__(yo, value):
                adj, = yo._args
                yo.adjective = adj
            def desc(yo):
                return 'the %s moon' % (yo.adjective,)
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 4)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE], lst)
        for i, color in enumerate('BLACK RED GREEN BLUE'.split()):
            e = Color(color)
            yo.assertEqual(e.value, i)
            yo.assertEqual(e._name, color)
            yo.assertIn(e, Color)
            yo.assertEqual(lst.index(e), i)
            yo.assertEqual(Color(i), i)
        for adj, e in zip(('midnight', 'blood', 'emerald', 'sky'), Color):
            yo.assertEqual(e.desc(), 'the %s moon' % adj)
        class Color(Enum):
            BLACK  = enum('midnight', value=0)
            RED    = enum('blood', value=1)
            GREEN  = enum('emerald', value=7)
            BLUE   = enum('sky', value=8)
            PURPLE = enum('people eater', value=9)
            def __init__(yo, value):
                adj ,= yo._args
                yo.adjective = adj
            def desc(yo):
                return 'the %s moon' % (yo.adjective,)
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 5)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE, Color.PURPLE], lst)
        for i, color in zip([0, 1, 7, 8, 9], 'BLACK RED GREEN BLUE PURPLE'.split()):
            e = Color(color)
            yo.assertEqual(e.value, i)
            yo.assertEqual(e._name, color)
            yo.assertIn(e, Color)
            yo.assertEqual(Color(i), i)
        for adj, e in zip(('midnight', 'blood', 'emerald', 'sky', 'people eater'), Color):
            yo.assertEqual(e.desc(), 'the %s moon' % adj)

    def test_mundane_flag(yo):
        class Color(BitMaskEnum):
            BLACK = enum('midnight', value=0)
            RED   = enum('blood', value=1)
            GREEN = enum('emerald', value=2)
            BLUE  = enum('sky', value=4)
            def __init__(yo, value):
                adj, = yo._args
                yo.adjective = adj
            def desc(yo):
                return 'the %s moon' % (yo.adjective,)
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 4)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE], lst)
        for i, color in zip((0, 1, 2, 4), 'BLACK RED GREEN BLUE'.split()):
            e = Color(color)
            yo.assertEqual(e.value, i)
            yo.assertEqual(e._name, color)
            yo.assertIn(e, Color)
            yo.assertEqual(Color(i), i)
        for adj, e in zip(('midnight', 'blood', 'emerald', 'sky'), Color):
            yo.assertEqual(e.desc(), 'the %s moon' % adj)
        class Color(Enum):
            BLACK  = enum('midnight', value=0)
            RED    = enum('blood', value=1)
            GREEN  = enum('emerald', value=2)
            BLUE   = enum('sky', value=3)
            PURPLE = enum('people eater', value=4)
            def __init__(yo, value):
                adj ,= yo._args
                yo.adjective = adj
            def desc(yo):
                return 'the %s moon' % (yo.adjective,)
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 5)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE, Color.PURPLE], lst)
        for i, color in zip([0, 1, 2, 3, 4], 'BLACK RED GREEN BLUE PURPLE'.split()):
            e = Color(color)
            yo.assertEqual(e.value, i)
            yo.assertEqual(e._name, color)
            yo.assertIn(e, Color)
            yo.assertEqual(Color(i), i)
        for adj, e in zip(('midnight', 'blood', 'emerald', 'sky', 'people eater'), Color):
            yo.assertEqual(e.desc(), 'the %s moon' % adj)

    def test_mundane_unique(yo):
        class Color(UniqueEnum):
            BLACK = enum('midnight', value='black')
            RED   = enum('blood', value='red')
            GREEN = enum('emerald', value='green')
            BLUE  = enum('sky', value='blue')
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 4)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE], lst)
        for i, color in enumerate('black red green blue'.split()):
            e = Color(color)
            yo.assertEqual(e.value, color)
            yo.assertEqual(e._name, color.upper())
            yo.assertIn(e, Color)
            yo.assertEqual(lst.index(e), i)
            yo.assertEqual(Color(color), color)
        class Color(UniqueEnum):
            BLACK  = enum('midnight', value='black')
            RED    = enum('blood', value='red')
            GREEN  = enum('emerald', value='verde')
            BLUE   = enum('sky', value='blue')
            PURPLE = enum('people-eater', value='purple')
        lst = list(Color)
        yo.assertEqual(len(lst), len(Color))
        yo.assertEqual(len(Color), 5)
        yo.assertEqual([Color.BLACK, Color.RED, Color.GREEN, Color.BLUE, Color.PURPLE], lst)
        for i, color in enumerate('black red verde blue purple'.split()):
            e = Color(color)
            yo.assertEqual(e.value, color)
            yo.assertEqual(e._name, 'GREEN' if color == 'verde' else color.upper())
            yo.assertIn(e, Color)
            yo.assertEqual(lst.index(e), i)
            yo.assertEqual(Color(color), color)

    def test_create_enum(yo):
        raise TypeError('need tests!')
    
    def test_exception(yo):
        with yo.assertRaises(TypeError):
            class Color(Enum):
                BLACK
                RED = enum('sunset', '001')
                GREEN
                BLUE
        with yo.assertRaises(NameError):
            class Color(Enum):
                BLACK = enum('midnight', '000')
                RED
                GREEN
                BLUE
        with yo.assertRaises(InvalidEnum):
            class Color(Enum):
                BLACK
                RED
                GREEN
                BLUE
                BLACK  = 0

#print(Color, '\n---------------\n', Color._enums, '\n', Color._enum_map, '\n', Color._enum_ids, '\n-------------\n')

"""
class RGB(BitMaskEnum):
    "Red Green Blue"
    BLACK   = enum('no color', '000')
    RED     = enum('blood', '001')
    GREEN   = enum('grass', '010')
    BLUE    = enum('sky', '100')

    def __init__(yo, desc, hexstr, value):
        yo.desc = desc
        yo.hexstr = hexstr

#print(RGB, '\n---------------\n', RGB._enums, '\n', RGB._enum_map, '\n', RGB._enum_ids, '\n-------------\n')

class MoreColor(Color):
    MAGENTA
    YELLOW
    CYAN
#print(MoreColor, '\n---------------\n', MoreColor._enums, '\n', MoreColor._enum_map, '\n', MoreColor._enum_ids, '\n-------------\n')

class DbfType(UniqueEnum):
    CLP
    DB3
    VFP
#print(DbfType, '\n---------------\n', DbfType._enums, '\n', DbfType._enum_map, '\n', DbfType._enum_ids, '\n-------------\n')

class SomeFlags(BitMaskEnum):
    ON_DISK
    HAS_MEMO
    LARGE_CHAR
    UNICODE
#print(SomeFlags, '\n---------------\n', SomeFlags._enums, '\n', SomeFlags._enum_map, '\n', SomeFlags._enum_ids, '\n-------------\n')

class Error(UniqueEnum):
    import sys
    THIS
    THAT
    THEOTHER
    if sys.platform:
        BLAH
#print(Error, '\n---------------\n', Error._enums, '\n', Error._enum_map, '\n', Error._enum_ids, '\n-------------\n')

#Enum.create('Errors', 'BLACK RED GREEN BLUE', namespace=globals())


#print(Color)
#print(DbfType)
#print(SomeFlags)
"""

if __name__ == '__main__':
    unittest.main()
