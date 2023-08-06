"""
Copyright 2013 Brian Mearns

This file is part of templ.

templ is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

templ is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with templ.  If not, see <http://www.gnu.org/licenses/>.

******************************************************************************

Template types: all values must be of one of these types.
"""
import abc
import types
import collections
import filepos as tFilepos


class MetaTType(abc.ABCMeta):
    """
    Quick summary of meta classes: Basically, they're just class factories. The class/type object
    itself will be an instance of this class if you put `__metaclass__ = MetaTType` in the class
    definition. That means the class object itself will have all of the functions defined in this
    class.

    Basically, our only reason for doing this is to override the __str__ representation of classes.
    """

    def __str__(cls):
        """
        Used for coercing instances of this Metaclass to a string. So for instance, if you
        have an instance object and you get it's type, and then print that type, it will
        use this to convert that type to a string.
        """
        return "T_%s" % cls.__name__

    #def __init__(cls, name, bases, dct):
    #    super(MetaTType, cls).__init__(name, bases, dct)



def abstractclass(cls):
    """
    A class decorator (Python 2.6+) that replaces the __init__ function in a class with one that throws
    an error. Therefore, instances of that class cannot be instantiated. Subclasses will need to implement
    __init__ themselves to avoid this. Or, they could use the concreteclass decorator for the same purpose.

    This preserves the existing __init__ method of the class in the name __super__, so you can still implement
    an base implementation here.
    """
    cls.__super__ = cls.__init__
    def __init__(self, *args, **kwargs):
        raise TypeError("%s is an abstract class and cannot be instantiated directly. Subclasses must implement the __init__ method." % (cls.__name__))

    cls.__init__ = __init__
    return cls
    
def concreteclass(cls):
    """
    Class decorator to make a class be a concrete class when it inherits from an <abstractclass>. You don't need to do this, it just
    adds a default __init__ method which delegates to the abstract classes init (renamed by abstractclass to __super__).
    """
    def __init__(self, *args, **kwargs):
        super(cls, self).__super__(*args, **kwargs)

    cls.__init__ = __init__
    return cls


@abstractclass
class TType(object):
    """
    The base class for all types of all values in template.

    A number of class methods are defined here, based on the concept of __acceptable_types__.
    This should be a class attribute which is a sequence of two-tuples. Each two tuple is of the form
    (types, convert) where types is either a type or a sequence of types (i.e., anything acceptable for
    the second argument of isinstance) and convert is a function of one argument which will coerce a
    value of that type into something acceptable. Acceptable is somewhat vague, but the basic idea is
    that it will be whatever type you use to store the value internally in the instance. At any rate,
    the returned value should be acceptable as an argument to the constructor.
    """

    __metaclass__ = MetaTType

    def __init__(self, filepos):
        self.__filepos = filepos

    @property
    def filepos(self):
        return self.__filepos

    @filepos.setter
    def filepos(self, pos):
        assert((pos is None) or isinstance(pos, tFilepos.Filepos))
        self.__filepos = pos

    def fillInFilepos(self, pos):
        """
        Recursively replaces "None" filepos attributes with the given position.
        """
        assert(isinstance(pos, tFilepos.Filepos))
        if self.filepos is None:
            self.__filepos = pos

    def __repr__(self):
        return "T" + self.reprVal()

    def reprVal(self):
        return str(id(self))

    @abc.abstractmethod
    def raw(self):
        """
        Return the "raw value" of the object as a type that matches the returned type of
        make_acceptable.
        """
        pass

    def __hash__(self):
        return hash(self.raw())

    def __eq__(self, other):
        try:
            other = self.make_acceptable(other)
        except TypeError:
            return False

        return self.raw() == other

    def __ne__(self, other):
        return not (self == other)


    @classmethod
    def make_acceptable(cls, other, filepos=None):
        """
        make_acceptable(cls, other):    Attempts to convert 'other' into a type that an instance of class
        'cls' can be built on, using the conversion functions in __acceptable_types__. If it is not acceptable,
        (no conversion found), raises a TypeError.
        """
        if issubclass(type(other), cls):
            return other.raw()
        for types, convert in cls.__acceptable_types__:
            if isinstance(other, types):
                return convert(other)
        raise TypeError("Cannot make type '%s' acceptable for %s." % (type(other).__name__, cls))

    @classmethod
    def coerce(cls, other, filepos):
        """
        coerce(cls, other):     Attempts to return an instance of class 'cls' corresponding to the value 'other'.
        If 'other' is already an instance of 'cls', it just returns it. Otherwise, it just passes it into the
        class constructor and assumes the constructor will use make_acceptable to either make it an acceptle
        type, or raise a TypeError.
        """
        if isinstance(other, cls):
            return other
        else:
            return cls(other, filepos)


passthru = lambda x : x


class Null(TType):
    __acceptable_types__ = (
        (types.NoneType, passthru),
    )

    def __init__(self, filepos=None):
        super(Null, self).__super__(filepos)

    def raw(self):
        return None

    def reprVal(self):
        return "NULL"

    def __str__(self):
        return "NULL"

    def __eq__(self, other):
        return isinstance(other, Null)

    def __neq__(self, other):
        return not self.__eq__(other)


class Return(TType):
    __acceptable_types__ = (
    )

    def __init__(self, value = None, filepos=None):
        super(Return, self).__super__(filepos)

        if value is None:
            self.__value = Null()
        elif not isinstance(value, TType):
            raise TypeError("Can only return TTypes.")
        else:
            self.__value = value

    def raw(self):
        return self.__value

    @property
    def value(self):
        return self.__value

    def __str__(self):
        return "<Ret:%s>" % str(self.__value)

    @classmethod
    def coerce(cls, other, filepos):
        raise TypeError("Cannot coerce to a Return Type.")
        

def boolToStr(b):
    if b:
        return "1"
    else:
        return "0"

class String(TType):

    __acceptable_types__ = (
        (types.StringTypes, passthru),
        (bool, boolToStr),  #Order is important here, don't let it come after int or long.
        (int, str),
        (long, str),
        (float, str),
        (types.NoneType, lambda s : ""),
    )

    class StringIterator(collections.Iterator):
        def __init__(self, string):
            self.__iter = iter(string)

        def next(self):
            return String(self.__iter.next())


    def __init__(self, string=None, filepos=None):
        super(String, self).__super__(filepos)
        self.__string = self.make_acceptable(string)

    def __hash__(self):
        return hash(self.__string)

    def __int__(self):
        return int(self.__string, 0)

    def __long__(self):
        return long(self.__string, 0)

    def __float__(self):
        return float(self.__string)


    def __str__(self):
        return self.__string

    def __len__(self):
        return len(self.__string)

    def __getitem__(self, idx):
        return String(self.__string[idx])

    def __iter__(self):
        return String.StringIterator(self.__string)

    def __reversed__(self):
        return String("".join(reversed(self.__string)))

    @property
    def str(self):
        return self.__string

    def raw(self):
        return self.__string

    def reprVal(self):
        return repr(self.__string)

    def __add__(self, other):
        return String(self.__string + String.make_acceptable(other))


class List(TType, collections.MutableSequence, collections.MutableSet):

    def __init__(self, seq=None, filepos=None):
        super(List, self).__super__(filepos)
        self.__list = self.make_acceptable(seq, filepos)

    @classmethod
    def make_acceptable(cls, other, filepos=None):
        """
        The list implementation will attempt to ue <ttypes.coerce> to force all
        items of the given sequence to appropriate TTypes, and return a list of
        them. If the given 'other' is not iterable, or any of it's items fail to
        be coerced to a TType, then a TypeError is raised.
        """
        if other is None:
            return tuple()
        elif isinstance(other, collections.Iterable):
            return tuple(coerce(item, filepos) for item in other)
        else:
            raise TypeError("Cannot coerce type '%s' to %s." % (type(other).__name__, cls))

    @property
    def list(self):
        return tuple(self.__list)

    def fillInFilepos(self, pos):
        super(List, self).fillInFilepos(pos)
        for item in self.__list:
            item.fillInFilepos(pos)

    def raw(self):
        return self.list

    def reprVal(self):
        return "[" + ",".join(repr(x) for x in self.__list) + "]"

    def __str__(self):
        return "[" + ", ".join(str(x) for x in self.__list) + "]"

    def __setitem__(self, idx, value):
        self.__list[idx] = coerce(value, self.filepos)

    def __delitem__(self, idx):
        del(self.__list[idx])

    def insert(self, idx, value):
        self.__list.insert(idx, coerce(value, self.filepos))

    def __getitem__(self, idx):
        return self.__list[idx]

    def __len__(self):
        return len(self.__list)

    def __iter__(self):
        return iter(self.__list)

    def __contains__(self, value):
        return coerce(value, self.filepos) in self.__list

    def count(self, value):
        return self.__list.count(coerce(value, self.filepos))

    def add(self, value):
        self.append(value)

    def discard(self, value):
        """
        Removes ALL instances of value from the list (not recursively, though).
        """
        value = coerce(value, self.filepos)
        try:
            while True:
                self.__list.remove(value)
        except ValueError:
            pass

    def __add__(self, value):
        """
        For some reason __sub__ and __iadd__ are both provided, but not __add__.
        Anyway, this is the same as extend, value should be a sequence, the returned
        value is a List is prefixed with self's elements, and suffixed with value's
        elements.
        """
        value = self.make_acceptable(value)
        return List(self.__list + value)


    def __eq__(self, other):
        """
        Redefined to compare recursively.
        """
        try:
            other = self.make_acceptable(other)
        except TypeError:
            return False

        length = len(other)
        l = self.__list
        if length != len(l):
            return False

        for i in range(length):
            if l[i] != other[i]:
                return False

        return True

class ExprList(List):
    def reprVal(self):
        return "*[" + ",".join(repr(x) for x in self.list) + "]"

    def __str__(self):
        return "*[" + ", ".join(str(x) for x in self.list) + "]"



def coerce(other, filepos=None):
    if isinstance(other, TType):
        return other

    for sub in TType.__subclasses__():
        try:
            val = sub.coerce(other, filepos)
            val.filepos = filepos
            return val
        except TypeError:
            pass

    raise TypeError("Cannot coerce a value of type '%s' to a TType." % (type(other).__name__))


