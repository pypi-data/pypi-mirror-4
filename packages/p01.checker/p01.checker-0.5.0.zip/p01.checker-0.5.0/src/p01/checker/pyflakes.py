##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""pyflakes (by agroszer)

$Id: pyflakes.py 3584 2012-12-22 16:48:37Z roger.ineichen $
"""

# this is a !!MODIFIED!!! version of the original
# this one returns the warnings instead of printing them to stdout

"""
Implementation of the command-line I{pyflakes} tool.
"""

import compiler
import sys

checker = __import__('pyflakes.checker').checker


def checkPYFlakes(codeString, filename):
    """
    Check the Python source given by C{codeString} for flakes.

    @param codeString: The Python source to check.
    @type codeString: C{str}

    @param filename: The name of the file the source came from, used to report
        errors.
    @type filename: C{str}

    @return: The number of warnings emitted.
    @rtype: C{int}
    """
    # Since compiler.parse does not reliably report syntax errors, use the
    # built in compiler first to detect those.
    try:
        try:
            compile(codeString, filename, "exec")
        except MemoryError:
            # Python 2.4 will raise MemoryError if the source can't be
            # decoded.
            if sys.version_info[:2] == (2, 4):
                raise SyntaxError(None)
            raise
    except (SyntaxError, IndentationError), value:
        msg = value.args[0]

        (lineno, offset, text) = value.lineno, value.offset, value.text

        # If there's an encoding problem with the file, the text is None.
        if text is None:
            # Avoid using msg, since for the only known case, it contains a
            # bogus message that claims the encoding the file declared was
            # unknown.
            return  "%s: problem decoding source" % (filename, )
        else:
            line = text.splitlines()[-1]

            if offset is not None:
                offset = offset - (len(text) - len(line))

            result = '%s:%d: %s\n%s' % (filename, lineno, msg, line)

            if offset is not None:
                result += '\n'+" " * offset+"^"

        return result
    else:
        # Okay, it's syntactically valid.  Now parse it into an ast and check
        # it.
        tree = compiler.parse(codeString)
        w = checker.Checker(tree, filename)
        w.messages.sort(lambda a, b: cmp(a.lineno, b.lineno))
        return w.messages
