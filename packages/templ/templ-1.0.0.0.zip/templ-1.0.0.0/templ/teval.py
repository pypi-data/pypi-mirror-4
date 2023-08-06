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

Functions and types of evaluating expressions.

Expressions, including lists, are *evaluated*. Symbols are self-evaluating. Empty lists eval to NULL.
For non empty lists, the first element is *resolved* to an executable. Executables are self-resolving,
Strings are resolved by looking them up in the stack. Finally, the resolved tag is *executed*.
"""

import ttypes
import texec
import tstreams
import texceptions


def resolveExecutable(val, stack):
    """
    Given a TType value, gets an Executable object it represents, for intance, if the first
    value in a list-expression evaluated to the given val, what Executable would it be?
    Returns (name, exe).
    """
    if isinstance(val, ttypes.String):
        exe = stack.lookup(val)
        if exe is None:
            raise texceptions.NoSuchSymbolException(str(val), val.filepos)
        elif not isinstance(exe, texec.Executable):
            raise texceptions.TemplateTypeException("Invalid tag \"%s\"." % val, val.filepos, texec.Executable, exe)
        else:
            exe.filepos = val.filepos
            return (val, exe)

    elif isinstance(val, texec.Executable):
        return (str(val), val)

    else:
        raise texceptions.TemplateTypeException("Invalid tag \"%s\". Must be a String or Executable." % val, val.filepos, got=val)
    

def evalExpression(expr, ostream, stack):
    if not isinstance(ostream, tstreams.TemplateOutputStream):
        raise TypeError("Invalid output stream in use: must use a TemplateOutputStream, not a %s" % type(ostream))

    #Strings are self evaluating.
    if isinstance(expr, ttypes.String):
        return expr

    #Lists are evaluated as expressions.
    elif isinstance(expr, ttypes.List):
        #An empty list acts as an empty string.
        if len(expr) == 0:
            return ttypes.String("", filepos=expr.filepos)

        name = evalExpression(expr[0], ostream, stack)
        name, exe = resolveExecutable(name, stack)

        assert(expr.filepos is not None)
        assert(len(expr) == 1 or (expr[1].filepos is not None))
        exe.filepos = expr.filepos
        res = callExecutable(name, exe, expr[1:], ostream, stack)
        assert(isinstance(res, ttypes.TType)), repr(res)
        return res

    elif isinstance(expr, texec.Executable):
        #FIXME: Implement this
        raise texceptions.InternalError("Sorry, not implemented yet.", expr.filepos)

    else:
        if isinstance(expr, ttypes.TType):
            fp = expr.filepos
        else:
            fp = None
        raise texceptions.TemplateTypeException(
            "Invalid expression for evaluation: %r. Must be a String, List, or Executable." % (expr),
            fp, got=expr
        )
        
        
def callExecutable(name, exe, args, ostream, stack):
    stackDepth = stack.depth()
    if isinstance(exe, texec.TOperator):
        res = exe(str(name), args, ostream, stack)
    elif isinstance(exe, texec.TFunction):
        xargs = []
        for e in args:
            arg = evalExpression(e, ostream, stack)
            assert(isinstance(arg, ttypes.TType))
            xargs.append(arg)
        xargs = ttypes.List(xargs)
        res = exe(str(name), xargs, ostream, stack)
    elif isinstance(exe, texec.TMacro):
        subst = exe(str(name), ttypes.List(args), ostream, stack)
        assert(isinstance(subst, ttypes.TType))
        subst.fillInFilepos(exe.filepos)
        try:
            res = evalExpression(subst, ostream, stack)
        except texceptions.TemplateException, e:
            if stack.depth() != stackDepth:
                raise texceptions.InternalError("Macro did not restore stack: \"%s\"." % (name), exe.filepos)
            raise texceptions.TemplateMacroError(e, exe.filepos, name)
    else:
        raise texceptions.InternalError("Unhandled Executable class %s" % type(exe), exe.filepos)

    if stack.depth() != stackDepth:
        raise texec.InternalError("Executable did not restore stack (%d, %d): \"%s\"." % (stackDepth, stack.depth(), name), exe.filepos)
    return res



