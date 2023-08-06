from distutils.core import setup
from glob import glob
import os

#html_docs = glob('dbf/html/*')

long_desc="""
Yet Another Enumerator is an enum module that supports three different types of enumerations:  sequence enums (0, 1, 2, 3, etc.), base 2 bitmask enums (0, 1, 2, 4, 8, etc.), and string enums ('top','bottom','left','right', etc.).

Each Enumeration is its own class, with instances of that class being singletons.  Besides being a value, enum instances can also have their own behavior (use case, anyone?).

Creating an enum is as simple as:

    from yaenum import Enum, BitMaskEnum, UniqueEnum, enum

    Enum.create('Color', 'red green blue', export=globals())

or
    
    class Color(BitMaskEnum):       # python 3+ only
        black
        red
        green
        blue

and if that's too magical for you

    class Color(BitMaskEnum):
        black = enum()              # python 2: enum(value=0) etc.
        red   = enum()
        green = enum()
        blue  = enum()
"""

setup( name='yaenum',
       version= '0.1',
       license='BSD License',
       description='Enum module supporting sequence, bitmask, and string enumerations',
       long_description=long_desc,
       url='http://python.org/pypi/yaenum',
       py_modules=['yaenum', 'test_yaenum', 'yaenum27', '27_examples', '30_examples'],
       provides=['yaenum',],
       author='Ethan Furman',
       author_email='ethan@stoneleaf.us',
       classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Topic :: Database' ],
     )

