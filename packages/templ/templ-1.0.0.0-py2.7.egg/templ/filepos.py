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

A simple utility class for identifying a position in a while.
"""

import collections

class Filepos(collections.namedtuple("FileposTuple", "filename line offset")):
    def __init__(self, filename, line=None, offset=None):
        super(Filepos, self).__init__(filename, line, offset)
        
    def __str__(self):
        return self.toString()

    def toString(self, preposition="in"):
        form = ""

        if self.filename is not None:
            if len(preposition) > 0:
                preposition = "%s " % (preposition)

            form += "{preposition}\"{filename}\""

            if self.line is not None:
                form += " on line {lineno}"

                if self.offset is not None:
                    form += " (col {offset})"

        return form.format(
            preposition=preposition,
            filename = self.filename,
            lineno = self.line,
            offset = self.offset
        )


class CommandLineFilepos(Filepos):
    @classmethod
    def new(cls, argnumber):
        return cls(None, None, argnumber)

    def __init__(self, filename=None, line=None, offset=None):
        super(CommandLineFilepos, self).__init__("<program-args>", 0, offset)
        self.__argnumber = offset

    def toString(self, preposition="in"):
        return "in program argument number %d" % self.__argnumber


class WrapFilepos(Filepos):
    @classmethod
    def wrap(cls, filepos):
        if filepos is None:
            return cls(None, None, None)
        elif not isinstance(filepos, Filepos):
            raise TypeError("can only wrap another Filepos, not a %s" % type(filepos))
        filename, line, offset = filepos[:3]
        return cls(filename, line, offset)

class IncludedFilepos(WrapFilepos):
    @classmethod
    def new(cls, filepos, includedFrom):
        fp = cls.wrap(filepos)
        fp.__includedFrom = includedFrom
        return fp

    def toString(self, preposition="in"):
        string = super(IncludedFilepos, self).toString(preposition)
        string += ", included %s" % self.__includedFrom.toString("from")
        return string


class NearFilepos(WrapFilepos):
    def toString(self, preposition="in"):
        form = ""

        if self.filename is not None:
            if len(preposition) > 0:
                preposition = "%s " % (preposition)

            form += "{preposition}\"{filename}\""

            if self.line is not None:
                form += " near line {lineno}"

                if self.offset is not None:
                    form += " (col {offset})"

        return form.format(
            preposition=preposition,
            filename = self.filename,
            lineno = self.line,
            offset = self.offset
        )


