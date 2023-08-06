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

import os
import filepos as tFilepos
import texceptions
import abc


class TemplateOutputStream(object):
    """
    A really simple not-quite stream-like object that just supports a write and close
    method.

    I can't really remember why I needed a new class...I think I needed a standard interface
    that I could back with an FD integer, instead of a stream like object. Or something.
    Mostly, I wanted to make sure I wasn't relying on anything other than write and
    maybe close.
    """

    @abc.abstractmethod
    def write(self, data):
        pass

    @abc.abstractmethod
    def close(self):
        pass

class TemplateStreamOutputStream(TemplateOutputStream):
    def __init__(self, stream):
        self.__stream = stream

    def write(self, data):
        try:
            self.__stream.write(data)
        except IOError, e:
            raise texceptions.TemplateIOException(e, None)
        
    def close(self):
        try:
            self.__stream.close()
        except IOError, e:
            raise texceptions.TemplateIOException(e, None)
        

class TemplateFDOutputStream(TemplateOutputStream):
    def __init__(self, fd):
        self.__fd = fd

    def write(self, data):
        try:
            os.write(self.__fd, data)
        except OSError, e:
            raise texceptions.TemplateIOException(e, None)

    def close(self):
        try:
            os.close(self.__fd)
        except OSError, e:
            raise texceptions.TemplateIOException(e, None)


class BufferedTemplateOutputStream(TemplateOutputStream):
    """
    Implements the same interface as `TemplateOutputStream`, but isn't backed by a file,
    it just buffers everything that's written.
    """
    def __init__(self):
        self.__buffered = ""

    def write(self, data):
        self.__buffered += data

    def close(self):
        pass

    def str(self):
        return self.__buffered



class TemplateInputStream(object):
    def __init__(self, istream, name=None):
        self.__istream = istream
        self.__name = name
        if name is None:
            self.__name = "<input-stream>"

        self.__linelengths = []
        self.__pos = 0
        self.__buffer = ""
        self.__eoi = False

    def read(self, limit):
        data = self.__buffer[:limit]
        self.__buffer = self.__buffer[limit:]
        remaining = limit - len(data)
        if remaining > 0 and not self.__eoi:
            assert(len(self.__buffer) == 0), len(self.__buffer)
            self.__buffer = self.__istream.readline()
            linelength = len(self.__buffer)
            if linelength == 0:
                self.__eoi = True
            else:
                if len(self.__linelengths) == 0:
                    self.__linelengths = [linelength]
                else:
                    self.__linelengths.append(self.__linelengths[-1] + linelength)

                data += self.__buffer[:remaining]
                self.__buffer = self.__buffer[remaining:]

        assert(len(data) <= limit), (len(data), limit)
        self.__pos += len(data)
        return data

    def unget(self, string):
        self.__pos -= len(string)
        self.__buffer = string + self.__buffer

    def tell(self):
        return self.__pos
            
    def getPosition(self, pos=None):
        if pos is None:
            pos = self.__pos

        lines = len(self.__linelengths)

        #TODO: More likely to be near the end, so search backwards.
        i = 0
        for i in xrange(lines):
            if pos < self.__linelengths[i]:
                break
        sol = 0
        if i > 0:
            sol = self.__linelengths[i-1]
        offset = pos - sol
        return tFilepos.Filepos(self.__name, i+1, offset + 1)


