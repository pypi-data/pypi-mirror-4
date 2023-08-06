#!/usr/bin/python
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
import teval
import texec
import types
import ttypes
import texceptions
import tstreams
import stack as tStack
import io
import os
import filepos as tFilepos

#Needed for main
import tbuiltin
import sys
import errno
import version


TOKEN_EOI = 0
TOKEN_SPACE = 1
TOKEN_OCUR = 2
TOKEN_CCUR = 3
TOKEN_SLASH = 4
TOKEN_QUOTE = 5
TOKEN_TEXT = 6
TOKEN_COMMENT = 7
TOKEN_OEMBED = 8
TOKEN_CEMBED = 9


STMT_EOI = 0
STMT_TEXT = 1
STMT_LIST = 2
STMT_CEMBED = 3

#             LF    VT      FF      CR    CR+LF   NEL     LS        PS
LINEBREAKS = ("\n", "\x0B", "\x0C", "\r", "\r\n", "\x85", "\u2028", "\u2029")

        
class TemplateProcessingError(texceptions.TemplateException):
    def __init__(self, cause, filepos=None):
        super(TemplateProcessingError, self).__init__(cause, filepos)

    def __str__(self):
        if self.filepos is None:
            filepos = ""
        else:
            filepos = " " + str(self.filepos)
        return "Error%s: %s" % (filepos, self.message)

class TemplateSyntaxError(TemplateProcessingError):
    pass


def process(istream, ostream, scope=None, iname="<input-stream>", debug=False):
    stack = tStack.Stack(scope)
    processWithStack(istream, ostream, stack, iname, debug)

def processWithStack(istream, ostream, stack, iname="<input-stream>", debug=False):

    if not isinstance(istream, tstreams.TemplateInputStream):
        istream = tstreams.TemplateInputStream(istream, iname)

    try:
        while True:
            stmt, value, filepos = parse(istream)

            if stmt == STMT_EOI:
                return

            #In text mode (i.e., at the top level), CEMBED is meaningless. OEMBED is already returned by
            # the parser as TEXT.
            elif stmt in (STMT_TEXT, STMT_CEMBED) :
                assert(isinstance(value, (str, unicode))), type(value)
                try:
                    ostream.write(value.encode("utf-8"))
                except UnicodeDecodeError, e:
                    raise texceptions.TemplateException(str(e), filepos)

            elif stmt == STMT_LIST:
                #Evaluate it.
                res = teval.evalExpression(value, ostream, stack)
                assert(isinstance(res, ttypes.TType))

                #At the top level, NULL is an empty string.
                # This is necessary so that all we have to do is wrap something in {v ...} to supress
                # the output at the top level.
                if isinstance(res, ttypes.Null):
                    pass
                elif isinstance(res, ttypes.String):
                    ostream.write(res.str.encode("utf-8"))
                else:
                    raise texceptions.TemplateTypeException("Top level expression resulted in non-String value.", res.filepos, got=res)

    except texceptions.TemplateException, e:
        if debug:
            raise
        raise TemplateProcessingError(e, e.filepos)
        



def parse(istream):
    """
    Top level parser, handles both TEXT and LIST expressions (well, it delegates).
    """
    plaintext = None
    ptstart = None
    while True:
        token, text, filepos = lex(istream)

        if token == TOKEN_EOI:
            if plaintext is not None:
                #Strip final EOL.
                longestEol = 0
                #Need to find the longest EOL that it ends with. For instance, if it
                # ends in \r\n, it will match \n, but we need to remove 2 chars, not 1.
                for eol in LINEBREAKS:
                    if plaintext.endswith(eol) and len(eol) > longestEol:
                        longestEol = len(eol)
                if longestEol > 0:
                    plaintext = plaintext[:-longestEol]
                return (STMT_TEXT, plaintext, ptstart)
            else:
                return (STMT_EOI, None, filepos)

        #We're operating in TEXT mode, so most of these tokens have no special meaning.
        elif token in (TOKEN_TEXT, TOKEN_SPACE, TOKEN_CCUR, TOKEN_QUOTE, TOKEN_COMMENT, TOKEN_OEMBED):
            if plaintext is None:
                plaintext = ""
                ptstart = filepos
            plaintext += text

        elif token == TOKEN_CEMBED:
            #If we've buffered any text, return that first.
            if plaintext is not None:
                #And unget the CEMBED
                istream.unget(text)
                return (STMT_TEXT, plaintext, ptstart)
            else:
                return (STMT_CEMBED, text, filepos)

        #In text mode, we use slash to escape curly braces.
        elif token == TOKEN_SLASH:
            content = ""

            #See what it's escaping.
            token, text, dummy = lex(istream)

            #Slashes aren't needed or used to escape slashes, so if it's a slash followed by a slash,
            # then the first one wasn't an escape, it's just text. But now we've got another slash
            # that might be escaping...
            while token == TOKEN_SLASH:
                content += '\\'
                token, text, dummy = lex(istream)

            if token in (TOKEN_OCUR, TOKEN_CCUR):
                #Write the curly brace, it's been escaped.
                content += text

            #Otherwise, slash has no special meaning, treat it as text, so output both the slash
            # and the text.
            else:
                content += '\\' + text

            if plaintext is None:
                plaintext = ""
                ptstart = filepos
            plaintext += content


        #Start of an expression
        elif token == TOKEN_OCUR:
            if plaintext is not None:
                #Unget start of expression
                istream.unget(text)
                return (STMT_TEXT, plaintext, ptstart)
                
            expr = parseExpr(istream, filepos)
            assert(isinstance(expr, ttypes.List))
            return (STMT_LIST, expr, filepos)




def parseExpr(istream, filepos):
    """
    We've already read the opening curly brace, this has to parse the remainder of the expression
    up to an including the closing curly brace, and return a TType List it represents. Do NOT evaluate
    anything here, just build the expression tree.
    """
    elements = []
    myfilepos = filepos
    cur = None
    curstart = None
    while True:
        token, text, filepos = lex(istream)

        if token == TOKEN_EOI:
            raise TemplateSyntaxError("Input ended with expression unterminated.", myfilepos)

        #White space is a separator, otherwise ignored.
        elif token == TOKEN_SPACE:
            if cur is not None:
                elements.append(ttypes.String(cur, curstart))
                cur = None
                curstart = None

        #Slash has no special meaning here, it's just text.
        elif token in (TOKEN_TEXT, TOKEN_SLASH):
            if cur is None:
                cur = ""
                curstart = filepos
            cur += text

        #Quoted strings just count as text, appended to existing text.
        elif token == TOKEN_QUOTE:
            if cur is None:
                cur = ""
                curstart = filepos
            cur += parseStringLiteral(istream, filepos)

        # EOL comment, treated as whitespace.
        elif token == TOKEN_COMMENT:
            #Its also a punctuator, so if we were building a string, complete it.
            if cur is not None:
                elements.append(ttypes.String(cur, curstart))
                cur = None
                curstart = None

            comment = text
            while True:
                c = istream.read(1)
                if len(c) == 0:
                    raise TemplateSyntaxError("Input ended with expression unterminated.", myfilepos)

                comment += c
                if any(comment.endswith(lb) for lb in LINEBREAKS):
                    unget = True
                    #Found a linebreak. Now find the longest matching linebreak.
                    while any(comment.endswith(lb) for lb in LINEBREAKS):
                        c = istream.read(1)
                        if len(c) == 0:
                            unget = False
                            break
                        comment += c

                    #Unget the last char (the non-EOL char)
                    if unget:
                        istream.unget(comment[-1])
                        comment = comment[:-1]
                    break

        #Embedded template.
        elif token == TOKEN_OEMBED:
            #Its also a punctuator, so if we were building a string, complete it.
            if cur is not None:
                elements.append(ttypes.String(cur, curstart))
                cur = None
                curstart = None

            embedded = ["'"]
            embeddedStart = filepos

            #This puts us back at the top level, so start parsing at the top level.
            while True:
                stmt, value, filepos = parse(istream)

                if stmt == STMT_EOI:
                    raise TemplateSyntaxError("Input ended with expression unterminated.", myfilepos)

                elif stmt == STMT_TEXT:
                    embedded.append(ttypes.String(value, filepos))

                elif stmt == STMT_CEMBED:
                    break

                elif stmt == STMT_LIST:
                    assert(isinstance(value, ttypes.List))
                    embedded.append(value)

            elements.append(ttypes.List(embedded, embeddedStart))            

        elif token == TOKEN_CEMBED:
            raise TemplateSyntaxError("Input >>> in expression. This is a reserved token inside expressions, to use it as a string, it must be quoted.", myfilepos)

        elif token == TOKEN_CCUR:
            #End of expression.
            if cur is not None:
                elements.append(ttypes.String(cur, curstart))
            return ttypes.List(elements, myfilepos)

        elif token == TOKEN_OCUR:
            #Start of another expression.
            if cur is not None:
                elements.append(ttypes.String(cur, curstart))
                cur = None
                curstart = None

            expr = parseExpr(istream, filepos)
            assert(isinstance(expr, ttypes.List))
            elements.append(expr)

        else:
            raise AssertionError("Unknown token %d" % token)


def parseStringLiteral(istream, filepos):
    string = ""
    while True:
        c = istream.read(1)
        if len(c) == 0:
            raise TemplateSyntaxError("Input ended with string-literal unterminated.", filepos)

        elif c == '"':
            return string

        elif c == '\\':
            c = istream.read(1)
            if len(c) == 0:
                raise TemplateSyntaxError("Input ended with string-literal unterminated.", filepos)

            #Escape always just means "include the next character in the string."
            string += c

        else:
            string += c


def lex(istream):
    filepos = istream.getPosition()
    c = istream.read(1)

    if len(c) == 0:
        #Reached end of input.
        return (TOKEN_EOI, "", filepos)

    elif c.isspace():
        #Consume whitespace strings.
        space = c
        while True:
            c = istream.read(1)
            if len(c) == 0:
                break
            elif c.isspace():
                space += c
            else:
                #Unget.
                istream.unget(c)
                break
        return (TOKEN_SPACE, space, filepos)

    elif c == "{":
        return (TOKEN_OCUR, c, filepos)

    elif c == "}":
        return (TOKEN_CCUR, c, filepos)

    elif c == '\\':
        return (TOKEN_SLASH, c, filepos)

    elif c == '"':
        return (TOKEN_QUOTE, c, filepos)

    elif c == '%':
        return (TOKEN_COMMENT, c, filepos)

    elif c == '<':
        #Check for embed.
        text = '<'
        while True:
            c = istream.read(1)
            if len(c) == 0:
                #EOI, so it was not an embed, so just return it as text.
                return (TOKEN_TEXT, text, filepos)
            elif c == '<':
                text += c
                if text == "<<<":
                    #Embed!
                    return (TOKEN_OEMBED, text, filepos)
            else:
                #Non '<', so not an embed. Unget that last non-'<' char.
                istream.unget(c)
                #And it's just text.
                return (TOKEN_TEXT, text, filepos)

    elif c == '>':
        #Check for embed.
        text = '>'
        while True:
            c = istream.read(1)
            if len(c) == 0:
                #EOI, so it was not an embed, so just return it as text.
                return (TOKEN_TEXT, text, filepos)
            elif c == '>':
                text += c
                if text == ">>>":
                    #Embed!
                    return (TOKEN_CEMBED, text, filepos)
            else:
                #Non '>', so not an embed. Unget that last non-'>' char.
                istream.unget(c)
                #And it's just text.
                return (TOKEN_TEXT, text, filepos)

    else:
        #Plaintext char
        #Consume all.
        text = c
        while True:
            c = istream.read(1)
            if len(c) == 0:
                break
            elif c.isspace() or c in ('{', '}', '\\', '"', '%', '>'):
                #Unget.
                istream.unget(c)
                break
            else:
                text += c
        return (TOKEN_TEXT, text, filepos)
            



def printVersion(ostream):
    ostream.write("templ v{version} - {datestr}\n\n".format(version=version.string(), datestr=version.datestr()))

def printUsage(ostream, argv=sys.argv):
    ostream.write(
"""Usage: {PROG} [options] [TEMPLATE_FILE [OUTFILE]]
   or: {PROG} [options] - [OUTFILE]

""".format(PROG=argv[0]))


def printHelp(ostream, argv=sys.argv):
    printVersion(ostream)
    printUsage(ostream, argv)
    ostream.write(
"""Processes TEMPLATE_FILE through the templ processor, writing the output to
OUTFILE. In the second usage, the use of "-" as the TEMPLATE_FILE indicates
that the template should be read from STDIN. This is also the default if
TEMPLATE_FILE is not specified. Likewise, a dash can be used for OUTFILE to
indicate that output should be written to STDOUT, which is also the default if
OUTFILE is not given.

Options:
 -s, --set NAME [VALUE]         Adds a symbol named NAME to the global scope
                                with a String type value given by VALUE. If
                                VALUE is not given, a NULL value is used.

 -b, --binary                   Opens the input and output files in binary
                                mode, when possible. This is not possible for
                                standard streams (STDIN or STDOUT).

Misc Options:
 --debug                        Enable debug output.

 -V, --version                  Print the version string and exit.

 --usage                        Print a brief usage message and exit.

 --help                         Print this help menu.


Copyright {COPYRIGHT} Brian Mearns. Program licensed under GNU AGPLv3.

For more information about this product see:
            <https://bitbucket.org/bmearns/templ/>.
""".format(COPYRIGHT=version.COPYRIGHT)
    )


def main():

    templates = []
    infile = None
    outfile = None
    #Our initial scope.
    globs = texec.getGlobalScope()
    debug = False
    binary = False

    i = 1
    argc = len(sys.argv)
    while i < argc:
        arg = sys.argv[i]
        i += 1
        if arg in ("-h", "-?", "/?", "--help"):
            printHelp(sys.stdout, sys.argv)
            return (0)

        elif arg in ("-V", "--version"):
            printVersion(sys.stdout)
            return (0)

        elif arg in ("--usage", ):
            printUsage(sys.stdout, sys.argv)
            return (0)

        elif arg in ("--debug", ):
            debug = True

        elif arg in ("-b", "--binary", ):
            binary = True

        elif arg in ("-s", "--set"):
            if i == argc:
                sys.stderr.write("%s: Error: Missing required parameter for option %s.\n" % (sys.argv[0], arg))
                sys.stderr.write("%s: Try `%s --help`\n" % (sys.argv[0], sys.argv[0]))
                return (errno.EINVAL)
            else:
                name = sys.argv[i]
                i += 1
                fp = tFilepos.CommandLineFilepos.new(i)
                if i < argc:
                    value = sys.argv[i]
                    value = ttypes.String(value, filepos=fp)
                    i += 1
                else:
                    value = ttypes.Null(filepos=fp)
                globs[name] = value

        else:
            if infile is None:
                infile = arg
            elif outfile is None:
                outfile = arg
            else:
                sys.stderr.write("%s: Error: Unexpected argument \"%s\".\n" % (sys.argv[0], arg))
                sys.stderr.write("%s: Try `%s --help`\n" % (sys.argv[0], sys.argv[0]))
                return (errno.EINVAL)
                

    istream = None
    ostream = None
    try:
        if (infile is None) or (infile == "-"):
            iname = "<stdin>"
            istream = sys.stdin
        else:
            iname = infile
            mode = "r"
            if binary:
                mode += "b"
            istream = open(iname, mode)

        if (outfile is None) or (outfile == "-"):
            ostream = tstreams.TemplateStreamOutputStream(sys.stdout)
        else:
            ostream = tstreams.TemplateStreamOutputStream(open(outfile, "wb"))

        try:
            #Invoke the templ processor.
            process(istream, ostream, globs, iname, debug)

        except TemplateProcessingError, e:
            #Catch and pretty-print errors found in the template.
            if debug:
                raise

            try: istream.close()
            except Exception: pass
            try: ostream.close()
            except Exception: pass

            sys.stderr.write(str(e) + "\n")
            return (-1)

        try: istream.close()
        except Exception: pass
        try: ostream.close()
        except Exception: pass

    except IOError, e:
        if debug:
            raise e

        if istream is not None:
            try: istream.close()
            except Exception: pass
        if ostream is not None:
            try: ostream.close()
            except Exception: pass

        sys.stderr.write("An IO Error occurred: %s\n" % str(e))
        return (errno.EIO)

if __name__ == "__main__":
    ec = main()
    sys.exit(ec)

