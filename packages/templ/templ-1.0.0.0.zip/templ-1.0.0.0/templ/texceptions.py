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
"""

import filepos as tFilepos
import ttypes
import collections

class TemplateException(Exception):
    def __init__(self, message, filepos):
        super(TemplateException, self).__init__(message)
        self.__templValue = ttypes.String(str(message))
        self.__filepos = filepos
        if (filepos is not None) and (not isinstance(filepos, tFilepos.Filepos)):
            raise TypeError("Invalid filepos: %r" % filepos)

    @property
    def filepos(self):
        return self.__filepos

    @filepos.setter
    def filepos(self, filepos):
        if (filepos is not None) and (not isinstance(filepos, tFilepos.Filepos)):
            raise TypeError("Invalid filepos: %r" % filepos)
        self.__filepos = filepos

    @property
    def templValue(self):
        return self.__templValue

class TemplateIOException(TemplateException):
    def __str__(self):
        return "An I/O error occurred: %s" % (self.message)

class InternalError(TemplateException):
    def __str__(self):
        return "Sorry, an internal error has occurred: %s" % self.message


class TemplateMacroError(TemplateException):
    def __init__(self, exception, filepos, macroName):
        super(TemplateMacroError, self).__init__(exception, filepos)
        self.macro = macroName

    def __str__(self):
        if hasattr(self.message, "filepos"):
            if self.message.filepos is None:
                fp = "at <unknown location>"
            else:
                fp = str(self.message.filepos)
        else:
            fp = "at <unknown location>"
        return "Error occured evaluating macro \"%s\" %s: %s" % (self.macro, fp, self.message)

class TemplateUserExecError(TemplateException):
    def __init__(self, exception, filepos, functionName, definedAtFilepos):
        assert(isinstance(exception, TemplateException)), type(exception)
        super(TemplateUserExecError, self).__init__(exception, filepos)
        self.definedAtFilepos = definedAtFilepos
        self.function = functionName
        self.cause = exception

    def __str__(self):
        if self.definedAtFilepos is None:
            fp = "at <unknown location>"
        else:
            fp = self.definedAtFilepos.toString("at")
        return "Error occured evaluating user-executable \"%s\", defined %s: %s" % (
            self.function, fp, self.message)

class TemplateValueError(TemplateException):
    def __init__(self, message, filepos, got = None):
        super(TemplateValueError, self).__init__(message, filepos)
        self.got = got

    def __str__(self):
        string = self.message
        if self.got is not None:
            string += " Received \"%s\"" % (self.got)
        return string

class TemplateKeyError(TemplateException):
    """
    For a bad key: one that doesn't exist and should or does exist and shouldn't, or is just generally malformed.
    If the key is the wrong type, generally prefer TemplateTypeException.
    """
    def __init__(self, message, filepos, key=None):
        self.key = key
        super(TemplateKeyError, self).__init__(message, filepos)

    def __str__(self):
        string = self.message
        if self.key is not None:
            string += " Received \"%s\"" % (self.key)
        return string

class NoSuchFieldException(TemplateKeyError):
    def __init__(self, key, filepos, message = None):
        if message is None:
            message = str(key)
        super(NoSuchFieldException, self).__init__(message, filepos, key)

    def __str__(self):
        return "No such field \"%s\"." % self.key

class NoSuchSymbolException(TemplateKeyError):
    def __init__(self, symbol, filepos, message = None):
        if message is None:
            message = str(symbol)
        super(NoSuchSymbolException, self).__init__(message, filepos, symbol)

    def __str__(self):
        return "No such symbol \"%s\"." % self.key


class TemplateIndexError(TemplateKeyError):
    """
    Generically for bad index values. If an index is out of bounds, use `TemplateIndexOutOfBoundsError`.
    """
    def __init__(self, message, filepos, key=None):
        super(TemplateIndexError, self).__init__(message, filepos, key)

class TemplateIndexOutOfBoundsError(TemplateIndexError):
    def __init__(self, message, filepos, min=None, max=None, idx=None):
        super(TemplateIndexOutOfBoundsError, self).__init__(message, filepos, idx)
        self.max = max
        self.min = min
        self.idx = idx

    def __str__(self):
        string = self.message
        if self.min is not None:
            string += " Minimum index is %d." % self.min
        if self.max is not None:
            string += " Maximum index is %d." % self.max
        if self.idx is not None:
            string += " Received index: %d." % self.idx
        return string

class TemplateSequenceIndexOutOfBoundsError(TemplateIndexOutOfBoundsError):
    def __init__(self, message, filepos, length=None, idx=None):
        super(TemplateSequenceIndexOutOfBoundsError, self).__init__(message, filepos, max=length, idx=idx)

    def __str__(self):
        string = self.message
        if self.max is not None:
            string += " Length is %d." % self.max
        if self.idx is not None:
            string += " Received index: %d." % self.idx
        return string
    


class WrongNumberArgsException(TemplateException):
    def __init__(self, message, filepos, got=None, exact=None, min=None, max=None):
        super(WrongNumberArgsException, self).__init__(message, filepos)

        self.got = got
        self.min = min
        self.max = max

        self.exact = None
        if exact is not None:
            if min is not None or max is not None:
                raise Exception("Conflicting arguments for exception.")
            elif not isinstance(exact, collections.Sequence):
                raise TypeError("Invalid type for 'exact'.")
            elif len(exact) == 0:
                raise ValueError("Invalid value for 'exact': require at least one value.")
            else:
                self.exact = exact

    def __str__(self):
        string = self.message
        if self.exact is not None:
            string += " Expected exactly "
            plural = "s"
            if len(self.exact) == 1:
                string += "%s" % (self.exact[0])
                if self.exact[0] == "1":
                    plural = ""
            else:
                initial = ", ".join(str(e) for e in self.exact[:-1])
                if len(self.exact) > 2:
                    initial += ","
                string += initial + (" or %s" % self.exact[-1])
            string += " argument" + plural + "."

        elif (self.min is not None) or (self.max is not None):
            string += " Expected "
            parts = []
            if self.min is not None:
                parts.append("at least %s" % self.min)
            if self.max is not None:
                parts.append("no more than %s" % self.max)

            string += " and ".join(parts) + " arguments."

        if self.got is not None:
            string += " Received %s argument" % self.got
            if self.got != "1":
                string += "s"
            
        string += "."
        return string
                

class TemplateTypeException(TemplateException):
    def __init__(self, message, filepos, exp=None, got=None):
        super(TemplateTypeException, self).__init__(message, filepos)

        if exp is None:
            self.__exp = None
        elif isinstance(exp, type):
            self.__exp = exp
        else:
            self.__exp = type(exp)

        self.__gotValue = None
        if got is None:
            self.__got = None
        elif isinstance(got, type):
            self.__got = got
        else:
            self.__gotValue = got
            self.__got = type(got)

    @property
    def expected(self):
        return self.__exp

    @property
    def got(self):
        return self.__got

    def __str__(self):
        string = self.message
        if self.__exp is not None:
            string += " Expected %s" % self.__exp
            if self.__got is None:
                string += "."
            else:
                string += ", not %s" % self.__got
                if self.__gotValue is not None:
                    string += " (%s)" % (str(self.__gotValue))
                string += "."
        elif self.__got is not None:
            string += " Received object of type %s" % (self.__got)
            if self.__gotValue is not None:
                string += " (%s)" % (str(self.__gotValue))
            string += "."

        return string
        
class NotAConsException(TemplateTypeException):
    def __init__(self, message, filepos, got=None):
        self.__value = got
        super(NotAConsException, self).__init__(message, filepos, None, got)

    @property
    def value(self):
        return self.__value

    def __str__(self):
        string = self.message
        string += " Expected a List of length 2."
        if self.got is not None:
            if isinstance(self.value, ttypes.List):
                string += " Received list of length %d." % len(self.value)
            else:
                string += " Received object of type %s." % type(self.value)

        return string

class TemplateUserException(TemplateException):
    def __init__(self, value, filepos):
        assert(isinstance(value, ttypes.TType))
        super(TemplateUserException, self).__init__(value, filepos)
        self.__templValue = value

    @property
    def templValue(self):
        return self.__templValue

    def __str__(self):
        return "Error Raised: " + str(self.message)

