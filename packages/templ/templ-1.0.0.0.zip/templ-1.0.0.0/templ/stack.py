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

import collections
import ttypes

class Scope(dict):
    """
    A scope is just a simple dictionary of TType values, used for tracking variables in a particular
    scope.
    """
    def __init__(self, d=None, **kwargs):
        super(Scope, self).__init__()
        self.__locked = []

        if isinstance(d, collections.Mapping):
            for k, v in d.items():
                self[k] = v

        for k, v in kwargs.items():
            self[k] = v
            

    def __setitem__(self, key, val):
        try:
            key = ttypes.String(key)
        except TypeError:
            raise TypeError("Invalid key, requires a String, received a %s" % type(key))
        if not isinstance(val, ttypes.TType):
            raise TypeError("Invalid value, requires a TType, received a %s" % type(val))
        if key in self.__locked:
            raise KeyError("Key is locked, and cannot be modified: %s" % key)
        super(Scope, self).__setitem__(key, val)

    def lock(self, key):
        try:
            key = ttypes.String(key)
        except TypeError:
            raise TypeError("Invalid key, requires a String, received a %s" % type(key))
        if key in self.__locked:
            raise KeyError("Key is already locked: %s" % key)
        self.__locked.append(key)

    def unlock(self, key):
        try:
            key = ttypes.String(key)
        except TypeError:
            raise TypeError("Invalid key, requires a String, received a %s" % type(key))
        if key not in self.__locked:
            raise KeyError("Key is not locked, cannot be unlocked: %s" % key)
        self.__locked.remove(key)

    def islocked(self, key):
        try:
            key = ttypes.String(key)
        except TypeError:
            raise TypeError("Invalid key, requires a String, received a %s" % type(key))
        return key in self.__locked

class Stack(collections.Sequence):
    """
    The Stack is a simple list of Scopes, with the deepest/most-recent scope at the highest
    index. The list has the interface of an *immutable* sequence, plus the push and pop
    methods so you can add and remove scopes.
    """
    def __init__(self, scope=None):
        super(Stack, self).__init__()
        self.__list = collections.deque()
        if scope is None:
            self.__list.append(Scope())
        elif isinstance(scope, Scope):
            self.__list.append(scope)
        elif isinstance(scope, collections.Mapping):
            self.__list.append(Scope(scope))
        else:
            raise TypeError("Scope must be a Scope object.")


    def push(self):
        """
        Creates and returns a new empty scope to the end of the stack.
        """
        scope = Scope()
        self.__list.append(scope)
        return scope

    def pop(self):
        """
        Removes the bottom scope from the stack.
        """
        if len(self.__list) < 2:
            raise Exception("Cannot pop global scope.")
        self.__list.pop()

    def find(self, symbol):
        """
        Returns the index into the stack of the deepest (highest index) scope in which the specified
        key is defined. Returns None if there is no such key defined in the stack.
        """
        try:
            symbol = ttypes.String(symbol)
        except TypeError:
            raise TypeError("Invalid name: can only lookup Strings, not %s" % (type(symbol)))

        #Search from the deepest level (high index), and unroll higher.
        for i in reversed(range(len(self.__list))):
            if symbol in self.__list[i]:
                return i
        return None

    def lookup(self, symbol):
        """
        Retreives the value associated with the given key in the closest scope
        in which it is defined, None if it is not defined.
        """
        try:
            symbol = ttypes.String(symbol)
        except TypeError:
            raise TypeError("Invalid name: can only lookup Strings, not %s" % (type(symbol)))

        i = self.find(symbol)
        if i is None:
            return None
        else:
            val = self.__list[i][symbol]
            assert(isinstance(val, ttypes.TType)), repr(val)
            return val

    def exists(self, symbol):
        """
        checks if the specified symbol exists anywhere in the stack.
        """
        return self.find(symbol) is not None

    def localExists(self, symbol):
        """
        Determines if the specified symbol is defined in the deepest scope.
        """
        return symbol in self.__list[-1]

    def set(self, symbol, val):
        """
        If the named symbol exists in anywhere in the stack, it's value is set to val.
        Otherwise, a new variable is alloced in the deepest scope and and set to val.
        """
        idx = self.find(symbol)
        if idx is None:
            #Doesn't exist yet.
            idx = -1
        self.__list[idx][symbol] = val

    def new(self, symbol, val):
        """
        Allocates a new variable in the deepest scope, sets it's value to val. If it already
        exists in that scope, raises a KeyError. Use localExists to test in advance.
        """
        if symbol in self.__list[-1]:
            raise KeyError("Local variable already exists: %s" % symbol)
        self.__list[-1][symbol] = val
            

    def local(self):
        """
        Returns the current deepest scope.
        """
        return self.__list[-1]

    def depth(self):
        """
        An alias for __len__, returns the number of scopes currently in the stack.
        """
        return len(self.__list)
            
    # Sequence
    def __getitem__(self, idx):
        return self.__list[idx]

    # Sized
    def __len__(self):
        return len(self.__list)


    
    
