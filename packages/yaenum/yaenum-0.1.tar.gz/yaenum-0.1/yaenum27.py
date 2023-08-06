"""\
copyright (c) 2013 by Ethan Furman
released under the 3-clause MIT license
"""

import sys
from math import floor, log

class InvalidEnum(Exception):
    pass


class EnumClassDict(object):
    """
    automatically assigns the next value for an enum name;
    enum names must be all caps
    """

    def __init__(yo):
        yo._magic = None
        yo._dict = {}

    def __getattr__(yo, name):
        return getattr(yo._dict, name)

    def __getitem__(yo, key):
        try:
            return yo._dict.__getitem__(key)
        except KeyError:
            if yo._magic is False:
                raise
            if (yo._type is None
            or key[:2] == key[-2:] == '__'):
                raise
            yo._magic = True
            if yo._type == 'unique':
                yo[key] = key.lower()
                return key
            elif yo._type in ('sequence','flag'):
                new_value = yo[key] = yo._value
                return new_value

    def __setitem__(yo, key, value):
        existing = yo._dict.get(key)
        if type(existing) is enum:
            raise InvalidEnum('Attempted to reuse key: %s' % key)
        if not key[:2] == key[-2:] == '__':
            old_value = None
            if isinstance(value, enum):
                if yo._magic is True:
                    raise TypeError("cannot use enum() once you've used magic!")
                yo._magic = False
                old_value = value
                if value.value is None:
                    value = yo._value
                else:
                    value = value.value
            if isinstance(value, int) and yo._type in ('sequence','flag'):
                yo._check_duplicate_value(value, key)
                yo._value = value
                yo._inc_value()
                yo._enums.append(key)
                value = enum(value=value)
            elif isinstance(value, str) and yo._type in ('unique', ):
                yo._enums.append(key)
                value = enum(value=value)
            if old_value is not None:
                value, old_value.value = old_value, value.value
        yo._dict[key] = value

    def _inc_value(yo):
        if yo._type == 'sequence':
            yo._value += 1
        else:
            if yo._value == 0:
                value = 1
            else:
                value = floor(log(yo._value, 2))
                value = 2 ** value
                value <<= 1
            yo._value = value

    def _check_duplicate_value(yo, new_value, key):
        for name, value in yo._dict.items():
            if value == new_value and name != key:
                raise ValueError('duplicate value for %s: %d' % (key, value))


class EnumType(type):

    @classmethod
    def __prepare__(metacls, cls, bases):
        classdict = EnumClassDict()
        classdict._type = None
        classdict._value = None
        classdict._enums = []
        classdict['enum'] = enum
        base, base_name, e_type, value = metacls._get_super_defaults(bases)
        if base_name is not None:
            classdict._type = e_type
            classdict._value = value
            for name, value in base._enum_map.items():
                classdict._enums.append(name)
                classdict[name] = value
            if classdict._type in ('sequence','flag'):
                if base._enum_map:
                    value = max([ e for e in base._enum_map.values()]) # if type(i) is int])
                    classdict._value = value
                    classdict._inc_value()
            classdict._magic = None     # reset as magic was set to False with the assignments above
        return classdict

    def __new__(metacls, cls, bases, classdict):
        #classdict = metacls.__prepare__(cls, bases, classdict)
        result = type.__new__(metacls, cls, bases, dict(classdict))
        if cls in ('Enum','BitMaskEnum','UniqueEnum'):
            setattr(result, '_enums', [])                # enums in value order
            setattr(result, '_enum_map', {})          # name:value map
            setattr(result, '_enum_ids', {})          # name:enum & value:enum map
            setattr(result,
                    '_type',
                    'unique' if cls == 'UniqueEnum' else
                    'sequence' if cls == 'Enum' else
                    'flag',
                    )
            return result
        base, base_name, e_type, e_value = metacls._get_super_defaults(bases)
        obj_type = {
                'Enum'        : int,
                'BitMaskEnum' : int,
                'UniqueEnum'  : str,
                }.get(base_name)
        enum_ids = {}
        enum_map = {}
        for name, e in classdict.items():
            if isinstance(e, result) and type(e) is not type(result):
                del classdict[name]
        for name, item in classdict.items():
            if type(item) is enum:
                value, args, kws = item
                enum_map[name] = value
                enum_obj = obj_type.__new__(result, value)
                enum_obj._name = name
                enum_obj._args = args
                enum_obj._kws = kws
                enum_obj.__init__(value)
                enum_ids[name] = enum_obj
                enum_ids[value] = enum_obj
                setattr(result, name, enum_obj)
        enums = sorted([e for e in set(enum_ids.values())])
        setattr(result, '_enums', enums)                # enums in value order
        setattr(result, '_enum_map', enum_map)          # name:value map
        setattr(result, '_enum_ids', enum_ids)          # name:enum & value:enum map
        setattr(result, '_type', e_type)
        if e_type == 'flag':
            low, high = enums[0].value, enums[-1].value
            if low:     # add an empty value
                enum_obj = obj_type.__new__(result, 0)
                enum_obj._name = 'none'
                enum_obj._args = tuple()
                enum_obj._kws = {}
                enum_ids['none'] = enum_obj
                enum_ids[0] = enum_obj
                enum_map['none'] = 0
                enums.insert(0, enum_obj)
            value = int(floor(log(high, 2)))
            value = 2 ** value
            value <<= 1
            setattr(result, '_max', value)
            for e in enums:
                e._composite = False        # one bit set, not many
        __all__ = sorted([(k, v) for (k, v) in enum_map.items()], key=lambda item: item[1])
        __all__ = [k for (k, v) in __all__]
        setattr(result, '__all__', __all__)
        return result

    def __iter__(cls):
        return iter(cls._enums[:])

    def __str__(cls):
        enums = []
        for e in cls._enums:
            enums.append((e._name, e.value))
        return "%s(%s)" % (
                cls.__name__,
                ', '.join('%s=%r' % (k, v) for k, v in enums)
                )

    @staticmethod
    def _get_super_defaults(bases):
        for base in bases:
            if base in (int, str):
                continue
            if issubclass(base, Enum):
                return base, 'Enum', 'sequence', 0
            elif issubclass(base, BitMaskEnum):
                return base, 'BitMaskEnum', 'flag', 1
            elif issubclass(base, UniqueEnum):
                return base, 'UniqueEnum', 'unique', None
                continue
        return None, None, None

    def create(cls, name, enums, type=None, register=None, export=None):
        metacls = cls.__class__
        if '.' in name:
            path, name = name.rsplit('.', 1)
        else:
            path = ''
        bases = (type, ) if type is not None else (cls, )
        classdict = metacls.__prepare__(name, bases)
        if isinstance(enums, str):
            enums = enums.replace(',',' ').split()
        for e in enums:
            classdict[e]
        result = metacls.__new__(metacls, name, bases, classdict)
        if register is not None:
            register[name] = result
        if export is not None:
            for e in result.__all__:
                export[e] = result._enum_ids[e]
        return result

    def export(cls, namespace=None):
        if namespace is None:
            namespace = cls.namespace


class enum(object):
    """
    helper for more rigorous enumerations
    """

    def __init__(yo, *args, **kws):
        """
        value, if passed, must be as a keyword argument
        """
        if 'value' in kws:
            value = kws.pop('value')
        else:
            value = None
        yo.value = value
        yo.args = args
        yo.kws = kws

    def __iter__(yo):
        return iter([yo.value, yo.args, yo.kws])
        
    def __repr__(yo):
        args = ', '.join(["%r" % a for a in yo.args])
        kws = ', '.join(['%r=%r' % (k, v) for k, v in yo.kws.items()])
        all_args = ', '.join([args, repr(yo.value), kws])
        return 'enum(%s)' % all_args


class Enum(int):
    "default Enum class, values start from 0"
    __metaclass__ = EnumType

    def __new__(cls, value, *args, **kws):
        try:
            enum = cls._enum_ids[value]
            if enum._args != args or enum._kws != kws:
                raise InvalidEnum("Enum %s cannot be redefined" % enum)
            return enum
        except KeyError:
            raise InvalidEnum("%s is not a valid %s" % (value, cls.__name__))

    def __init__(yo, *args, **kws):
        "override in subclass if anything needs to be done"

    def __repr__(yo):
        string = "'%s', " % yo._name
        if yo._args:
            string += ', '.join(["%r" % a for a in yo._args]) + ', '
        string += "value=%r" % yo.value
        if yo._kws:
            string += ", %s" %  ', '.join(["%s='%s'" % (k, v) for k, v in yo._kws.items()])
        return '%s(%s)' % (yo.__class__.__name__, string)

    def __str__(yo):
        return "%s.%s" % (yo.__class__.__name__, yo._name)

    def __hash__(yo):
        return int.__hash__(yo)

    def __eq__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return int(yo) == int(other)

    def __ne__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return int(yo) != int(other)

    def __le__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return int(yo) <= int(other)

    def __lt__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return int(yo) < int(other)

    def __ge__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return int(yo) >= int(other)

    def __gt__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return int(yo) > int(other)

    @property
    def value(yo):
        return int(yo)


class BitMaskEnum(int):
    "powers of two, with set semantics"
    __metaclass__ = EnumType

    def __new__(cls, value, *args, **kws):
        try:
            enum = cls._enum_ids[value]
            if (enum._args and enum._args != args
            or  enum._kws and enum._kws != kws):
                raise InvalidEnum("Enum %s cannot be redefined" % enum)
        except KeyError:
            if isinstance(value, int):
                if not -1 < value < cls._max:
                    raise InvalidEnum("%s is not a valid %s" % (value, cls.__name__))
            else:
                try:
                    names, value = value, 0
                    for name in names.split('|'):
                        enum = cls._enum_ids[name]
                        value += enum.value
                except:
                    raise InvalidEnum("%s is not valid for %s" % (names, cls.__name__))
            enum = int.__new__(cls, value)
            enum._composite = True
        return enum

    def __init__(yo, *args, **kws):
        "override in subclass if anything needs to be done"

    def __repr__(yo):
        if yo._composite:
            names = []
            for enum in yo._enums:
                if int(enum) & int(yo):
                    names.append(enum._name)
            string = "'%s', value=%r" % ('|'.join(names), yo.value)
        else:
            string = "'%s', " % yo._name
            if yo._args:
                string += ', '.join(["%r" % a for a in yo._args]) + ', '
            string += "value=%r" % yo.value
            if yo._kws:
                string += ", %s" %  ', '.join(["%s='%s'" % (k, v) for k, v in yo._kws.items()])
        return '%s(%s)' % (yo.__class__.__name__, string)

    def __str__(yo):
        composite = []
        for enum in yo._enums:
            if int(enum) & int(yo):
                composite.append(enum._name)
        return "%s.%s" % (yo.__class__.__name__, '|'.join(composite))

    def __hash__(yo):
        return int.__hash__(yo)

    def __eq__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return int(yo) == int(other)

    def __ne__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return int(yo) != int(other)

    def __le__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return int(yo) <= int(other)

    def __lt__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return int(yo) < int(other)

    def __ge__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return int(yo) >= int(other)

    def __gt__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return int(yo) > int(other)

    def __and__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return yo.__class__(int(yo) & int(other))

    def __invert__(yo):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return yo.__class__(int(yo).__invert__())

    def __lshift__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return yo.__class__(int(yo) << int(other))

    def __neg__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return yo.__class__(-int(yo))

    def __or__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return yo.__class__(int(yo) | int(other))

    def __pos__(yo):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return yo.__class__(+int(yo))

    def __rand__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return other & int(yo)

    def __rlshift__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return other << int(yo)

    def __ror__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return other | int(yo)

    def __rrshift__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return other >> int(yo)

    def __rshift__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return other >> int(yo)

    def __rxor__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return other ^ int(yo)

    def __xor__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return yo.__class__(int(yo) ^ int(other))

    @property
    def value(yo):
        return int(yo)


class UniqueEnum(str):
    "each enum is a str"
    __metaclass__ = EnumType

    def __new__(cls, value, *args, **kws):
        try:
            enum = cls._enum_ids[value]
            if enum._args != args or enum._kws != kws:
                raise InvalidEnum("Enum %s cannot be redefined" % enum)
            return enum
        except KeyError:
            raise InvalidEnum("%s is not a valid %s" % (value, cls.__name__))

    def __init__(yo, *args, **kws):
        "override in subclass if anything needs to be done"

    def __repr__(yo):
        string = "'%s', " % yo._name
        if yo._args:
            string += ', '.join(["%r" % a for a in yo._args]) +', '
        string += "value=%r" % yo.value
        if yo._kws:
            string += ", %s" %  ', '.join(["%s='%s'" % (k, v) for k, v in yo._kws.items()])
        return '%s(%s)' % (yo.__class__.__name__, string)

    def __str__(yo):
        return "%s.%s" % (yo.__class__.__name__, yo._name)

    def __hash__(yo):
        return str.__hash__(yo)

    def __eq__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return str(yo) == str(other)

    def __ne__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return str(yo) != str(other)

    def __le__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return str(yo) <= str(other)

    def __lt__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return str(yo) < str(other)

    def __ge__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return str(yo) >= str(other)

    def __gt__(yo, other):
        if not isinstance(other, yo.__class__):
            return NotImplemented
        return str(yo) > str(other)

    @property
    def value(yo):
        return str.__repr__(yo)[1:-1]


