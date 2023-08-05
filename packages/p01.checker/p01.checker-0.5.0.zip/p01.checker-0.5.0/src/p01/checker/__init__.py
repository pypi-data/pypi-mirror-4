##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Sourcecode checker, to be used in unittests (by agroszer)

$Id: __init__.py 3585 2012-12-23 12:48:35Z roger.ineichen $
"""

import os.path

from p01.checker.checker import AlertChecker
from p01.checker.checker import BadI18nDomainChecker
from p01.checker.checker import BreakPointChecker
from p01.checker.checker import CSSChecker
from p01.checker.checker import ConsoleLogChecker
from p01.checker.checker import JPGChecker
from p01.checker.checker import NonASCIIChecker
from p01.checker.checker import OpenInBrowserChecker
from p01.checker.checker import POChecker
from p01.checker.checker import PTBadI18nDomainChecker
from p01.checker.checker import PTMissingDomainChecker
from p01.checker.checker import PTXHTMLChecker
from p01.checker.checker import PYFlakesChecker
from p01.checker.checker import TabChecker
from p01.checker.checker import ZCMLBadI18nDomainChecker

###############################################################################
# 
# p01.checker.silence
#
# p01.checker.silnce is not a variable, it's just a hint that you can
# silence output given from Checker classes. Just add the following
# comment behind a line of code if you like to
# skip checker alerts:
#
# import pdb;pdb.set_trace() # p01.checker.silence
# 
# for HTML, javascript and page templates, you can use the phrase
# p01.checker.silence in the same line as the error message will get
# reported e.g.
#
# <!-- p01.checker.silence -->
#
# or
#
# // p01.checker.silence
#


###############################################################################
#
# p01.checker.ignore
#
# This line somewhere in a file will force to ignore checking the file at all
#


PY_CHECKS = [
    TabChecker(),
    NonASCIIChecker(),
    BreakPointChecker(),
    OpenInBrowserChecker(),
    PYFlakesChecker(),
    ]
PT_CHECKS = [
    TabChecker(),
    NonASCIIChecker(),
    ConsoleLogChecker(),
    AlertChecker(),
    # see checker.txt for how to add a page template domain checker
    #PTBadI18nDomainChecker('/p01/', ('p01',)),
    PTXHTMLChecker(),
    PTMissingDomainChecker(),
    ]
JS_CHECKS = [
    TabChecker(),
    ConsoleLogChecker(),
    AlertChecker(),
    ]
CSS_CHECKS = [
    CSSChecker(),
    NonASCIIChecker(),
    ]
TXT_CHECKS = [
    TabChecker(),
    BreakPointChecker(),
    OpenInBrowserChecker(),
    ]
PO_CHECKS = [
    POChecker(),
]
JPG_CHECKS = [
    JPGChecker(),
]
ZCML_CHECKS = [
    # see checker.txt for how to add a zcml domain checker
    #ZCMLBadI18nDomainChecker('/p01/', ('p01',)),
]

CHECKS = {
    'css': CSS_CHECKS,
    'html': PT_CHECKS,
    'jpg': JPG_CHECKS,
    'js': JS_CHECKS,
    'po': PO_CHECKS,
    'pt': PT_CHECKS,
    'py': PY_CHECKS,
    'txt': TXT_CHECKS,
    'zcml': ZCML_CHECKS,
}


def sortErrors(error):
    return error.get('idx', 0)

class Checker(object):
    """Checker implementation"""

    indent = '    '
    intro = False
    filename = None
    basename = None

    def __init__(self, checks=CHECKS, intend='    '):
        self.checks = checks
        self.intend = intend

    def addChecker(self, ext, checker):
        """Add custom checker for given file name extension
        
        This is usefull for simply add a checker with a custom setup
        """
        checkers = self.checks.setdefault(ext, [])
        checkers.append(checker)

    def start(self, basename, filename):
        """Log file intro"""
        # always slash please
        filename = filename.replace('\\','/')
        filename = filename[len(basename)+1:]
        print '-'* (len(filename))
        print filename
        print '-'* (len(filename))

    def log(self, data):
        idx = data.get('idx')
        line = data.get('line')
        pos = data.get('pos')
        error = data.get('error')

        # print line no and error msg
        if not idx:
            idx = '0: '
        else:
            idx = str(idx+1)+': '
        print "%s%s" % (idx, error)

        if line:
            # calculate strip lenght
            l = len(line)
            line = line.strip()
            skip = l - len(line)
            # print line
            print "%s%s" % (self.indent, line)
            # optional mark position
            if pos is not None and pos -skip <= len(line):
                print "%s%s^" % (self.indent, ' '*(pos -skip))

    def summary(self, basename, filename, errors=[]):
        """Report errors per file"""
        if len(errors):
            self.start(basename, filename)
            for data in sorted(errors, key=sortErrors):
                # log data per checker
                self.log(data)

    def check(self, module):
        """Thread save checker method"""
        basename = os.path.dirname(module.__file__)
        for root, dirs, files in os.walk(basename, topdown=True):
            #keep the name order
            dirs.sort()
            files.sort()
            for name in files:
                errors = []
                append = errors.append
                justname, ext = os.path.splitext(name)
                filename = os.path.join(root, name)
                ext = ext.replace('.','')
                if ext in self.checks.keys():
                    # read file once, pass the content to checkers
                    content = open(filename, 'rb').read()
    
                    if 'p01.checker.ignore' in content:
                        # ignore this file
                        continue
    
                    lines = content.splitlines()
                    for checker in self.checks[ext]:
                        checkerName = checker.__class__.__name__
                        for data in checker.check(basename, filename, content,
                            lines):
                            append(data)

                # report found errors per file
                self.summary(basename, filename, errors)
