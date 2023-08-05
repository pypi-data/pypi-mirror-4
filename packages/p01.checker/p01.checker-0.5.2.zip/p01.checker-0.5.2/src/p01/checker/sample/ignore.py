##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Sample module which get ignored from checking

$Id: ignore.py 3585 2012-12-23 12:48:35Z roger.ineichen $
"""

# p01.checker.ignore


class Foo(object):
    """A sample class forcing pyflake troubles"""

    def undefined_name(self):
        foo = False
        return bar

    def non_ascii(self):
        return u'ö'
