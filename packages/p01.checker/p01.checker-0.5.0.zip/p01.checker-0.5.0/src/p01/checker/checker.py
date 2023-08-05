##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Source code checker, to be used in unittests (original written by agroszer)

$Id: checker.py 3585 2012-12-23 12:48:35Z roger.ineichen $
"""

import re
import os
import os.path
import string
import logging
import polib
import lxml.etree
import cStringIO
import cssutils.parse

from p01.checker.pyflakes import checkPYFlakes


###############################################################################
#
# checker classes
#
###############################################################################

class BaseChecker(object):
    """Checker base class"""

    error = None
    indent = '    '

    def log(self, idx, line=None, pos=None, error=None):
        if error is None:
            error = self.error
        return {'checker': self, 'error': error,
                'idx': idx, 'line': line, 'pos': pos}

    def check(self, basename, filename, content, lines):
        raise StopIteration


class TabChecker(BaseChecker):
    """Text tabulator checker"""

    error = 'tab found in file'

    def check(self, basename, filename, content, lines):
        for idx, line in enumerate(lines):
            if '\t' in line:
                yield self.log(idx, line)


VALIDCHARS = string.printable


def replaceUnicode(line):
    try:
        return line.decode('utf-8', 'replace')
    except UnicodeEncodeError:
        return line

class NonASCIIChecker(BaseChecker):
    """Non ascii text checker"""

    error = 'non ASCII char found'

    def check(self, basename, filename, content, lines):
        for idx, line in enumerate(lines):
            for cidx, c in enumerate(line):
                if c not in VALIDCHARS:
                    yield self.log(idx, replaceUnicode(line), cidx)
                    break


class BreakPointChecker(BaseChecker):
    """Debug break point checker"""

    error = 'debug break point found'
    parts = ['pdb.set_trace', 'from pub.dbgpclient import brk'] # p01.checker.silence

    def check(self, basename, filename, content, lines):
        for part in self.parts:
            for idx, line in enumerate(lines):
                if part in line \
                    and not (-1 < line.find('#') < line.find(part)) \
                    and not '# p01.checker.silence' in line:
                    line = '%s # p01.checker.silence' % line
                    yield self.log(idx, line)


class OpenInBrowserChecker(BaseChecker):
    """Open in browser method checker"""

    error = 'openInBrowser found'

    def check(self, basename, filename, content, lines):
        key = '.open' + 'InBrowser'
        for idx, line in enumerate(lines):
            if (key in line
                and not (-1 < line.find('#') < line.find(key))):
                yield self.log(idx, line)


class PYFlakesChecker(BaseChecker):
    """Pyflakes checker"""

    error = 'pyflakes warning'

    def fixcontent(self, lines):
        #pyflakes does not like CRLF linefeeds
        #and files ending with comments
        idx = len(lines)-1
        lastline = lines[idx].strip()
        while idx >= 1 and (lastline == '' or lastline.startswith('#')):
            del lines[idx]
            idx -= 1
            lastline = lines[idx].strip()

        content = '\n'.join(lines)
        return content

    def check(self, basename, filename, content, lines):
        if "##skip pyflakes##" in content:
            raise StopIteration

        content = self.fixcontent(lines)
        try:
            result = checkPYFlakes(content, filename)
        except Exception, e:
            result = "Fatal PyFlakes exception: %s" % e

        if isinstance(result, basestring):
            #something fatal occurred
            self.error = result
            self.log(0)
        else:
            #there are messages
            for warning in result:
                if ('undefined name' in warning.message
                    and not 'unable to detect undefined names' in warning.message):
                    self.error = warning.message % warning.message_args
                    yield self.log(warning.lineno-1, lines[warning.lineno-1])


class ConsoleLogChecker(BaseChecker):
    """Javascript console log checker"""

    error = 'javascript console.log found'

    skipFileNames = ['jquery.nivo.slider.pack.js']

    def check(self, basename, filename, content, lines):
        for skipName in self.skipFileNames:
            if filename.endswith(skipName):
                raise StopIteration
        for idx, line in enumerate(lines):
            if 'console.log' in line \
                and not (-1 < line.find('//') < line.find('console.log')):
                yield self.log(idx, line)


class AlertChecker(BaseChecker):
    """Javascript alert checker"""

    error = 'javascript alert found'

    skipFileNames = []

    def check(self, basename, filename, content, lines):
        for skipName in self.skipFileNames:
            if filename.endswith(skipName):
                raise StopIteration
        for idx, line in enumerate(lines):
            if 'alert(' in line \
                and not (-1 < line.find('//') < line.find('alert()')):
                yield self.log(idx, line)


class CSSLogger(object):
    # this is a fake logger that redirects the actual logging calls to us

    errors = []

    def __init__(self):
        self.errors = []

    def noop(self, *args, **kw):
        pass

    debug = noop
    info = noop
    setLevel = noop
    getEffectiveLevel = noop
    addHandler = noop
    removeHandler = noop

    def error(self, msg):
        try:
            error = str(msg)
        except UnicodeEncodeError:
            error = msg.encode('ascii', 'replace')
        error = error.strip()
        # can't add much help, all info is encoded in msg
        self.errors.append((0, None, None, error))

    warn = error
    critical = error
    fatal = error


class CSSChecker(BaseChecker):
    """CSS checker"""

    error = 'CSS'

    def check(self, basename, filename, content, lines):
        logger = CSSLogger()
        parser = cssutils.parse.CSSParser(log=logger, loglevel=logging.WARN,
            validate=True)
        parser.parseString(content)
        for idx, line, pos, error in logger.errors:
            yield self.log(idx, line, pos, error)


class JPGChecker(BaseChecker):
    """JPG image compression checker"""

    error = 'image bloat found'

    def check(self, basename, filename, content, lines):
        if "ns.adobe.com" in content:
            yield self.log(0, "Adobe Photoshop bloat found")
            raise StopIteration

        if "<rdf:RDF" in content:
            yield self.log(0, "RDF bloat found")
            raise StopIteration

        if len(content)<500:
            raise StopIteration

        compressed = content.encode('zlib')
        ratio = len(compressed) / float(len(content)-200)
        #200= circa static header length

        if ratio < 0.8:
            line = "Some other bloat found, compression ratio: %s" %ratio
            yield self.log(0, line)


class POChecker(BaseChecker):
    """PO fuzzy counter checker"""

    error = 'fuzzy/untranslated found'

    def check(self, basename, filename, content, lines):
        pos = polib.pofile(filename)
        untrans = pos.untranslated_entries()
        fuzzy = pos.fuzzy_entries()

        if len(untrans) > 0:
            error = 'untranslated found'
            line = "%s items" % len(untrans)
            yield self.log(0, line, None, error)

        if len(fuzzy) > 0:
            error = 'fuzzy found'
            yield self.log(0, line, None, error)


class BadI18nDomainChecker(BaseChecker):
    """Bad i18n domain checker"""

    error = 'bad i18n domain found'

    def __init__(self, pattern, pathPart, domains=()):
        self.pattern = pattern
        self.pathPart = pathPart
        self.domains = domains

    def check(self, basename, filename, content, lines):
        # make it linux-ish
        error = self.error
        filename = filename.replace('\\', '/')

        if self.pathPart in filename:
            for idx, line in enumerate(lines):
                if 'i18n:domain=""' in line:
                    error = 'empty i18n:domain="" found'
                    yield self.log(idx, line, None, error)
                if 'i18n_domain=""' in line:
                    error = 'empty i18n_domain="" found'
                    yield self.log(idx, line, None, error)
                if self.pattern.search(content):
                    for fdomain in self.pattern.findall(line):
                        if fdomain == '' or fdomain not in self.domains:
                            error = 'bad i18n domain found'
                            yield self.log(idx, line, None, error)


class ZCMLBadI18nDomainChecker(BadI18nDomainChecker):
    """Bad zcml i18n domain checker"""

    def __init__(self, pathPart, domains=()):
        pattern = re.compile(r'domain="(\w+)"')
        super(ZCMLBadI18nDomainChecker, self).__init__(pattern, pathPart,
            domains)


class PTBadI18nDomainChecker(BadI18nDomainChecker):
    """Bad pt i18n domain checker"""

    def __init__(self, pathPart, domains=()):
        pattern = re.compile(r'i18n:domain="(\w+)"')
        super(PTBadI18nDomainChecker, self).__init__(pattern, pathPart, domains)


class PTMissingDomainChecker(BaseChecker):
    """Missing i18n:domain checker"""

    indent = '    '

    def reprElement(self, ele):
        res = lxml.etree.tostring(ele)
        res = res.replace(' xmlns="http://www.w3.org/1999/xhtml"', '')
        res = res.replace(' xmlns:tal="http://xml.zope.org/namespaces/tal"', '')
        res = res.replace(' xmlns:i18n="http://xml.zope.org/namespaces/i18n"', '')
        res = res.replace(' xmlns:metal="http://xml.zope.org/namespaces/metal"', '')
        return res

    def checkDomain(self, ele):
        dKey = '{http://xml.zope.org/namespaces/i18n}domain'
        while ele is not None:
            if ele.attrib.get(dKey) is not None:
                return True
            ele = ele.getparent()
        return False

    def check(self, basename, filename, content, lines):
        if not 'i18n:translate' in content:
            # no translation
            raise StopIteration

        # checks for i18n:translate and find i18n:domain in parent elements
        # if no domain get found report line and element content
        error = None
        lineCorrector = 0
        if not content.startswith('<!DOCTYPE') or content.startswith('<html>'):
            content = HTML_WRAPPER % content
            lineCorrector = 5
        sc = cStringIO.StringIO(content)
        msgs = []
        append = msgs.append
        try:
            for event, element in lxml.etree.iterparse(sc):
                # check if we have an i18n:translate without a i18n:domain
                # parent
                if '{http://xml.zope.org/namespaces/i18n}translate' in element.attrib:
                    # find i18n:domain in parent elements
                    if not self.checkDomain(element):
                        ele = self.reprElement(element)
                        line = element.sourceline - lineCorrector
                        msg = "%sline %s needs i18n:domain" % (
                            self.indent, line)
                        append(msg)
                        msg = "%sline '%s' needs i18n:domain, line: %s" % (
                            self.indent, ele, line)
                        append('%s%s' % (self.indent, ele))
        except lxml.etree.XMLSyntaxError, e:
            # we do not validate XML in this check, see PTXHTMLChecker
            pass

        if msgs:
            error = '\n'.join(msgs)
            error = error[len(self.indent):]

        if isinstance(error, basestring):
            # something fatal occurred, use error as line
            yield self.log(None, error, None, 'fatal error')


HTML_WRAPPER = """
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:tal="http://xml.zope.org/namespaces/tal"
      xmlns:metal="http://xml.zope.org/namespaces/metal"
      xmlns:i18n="http://xml.zope.org/namespaces/i18n">
  %s
</html>

"""

class PTXHTMLChecker(BaseChecker):
    """Chameleon template checker
    
    Chameleon defines the following namespaces by default:
    
    xmlns:tal="http://xml.zope.org/namespaces/tal"
    xmlns:metal="http://xml.zope.org/namespaces/metal"
    xmlns:i18n="http://xml.zope.org/namespaces/i18n"
    
    This means the document does not have to define them. We will wrap the 
    content with this namespaces if the document does not start with <html
    or <!DOCTYPE.
    
    """
    indent = '    '
    allowedErrorMassageStarts = [
        'Namespace prefix tal for ',
        'Namespace prefix tal on ',
        'Namespace prefix i18n for ',
        'Namespace prefix i18n on ',
        'Namespace prefix metal for ',
        'Namespace prefix metal on ',
        "Entity 'nbsp' not defined",
        "Entity 'ndash' not defined",
        "Entity 'raquo' not defined",
    ]

    def validateError(self, e):
        for allowed in self.allowedErrorMassageStarts:
           if e.message.startswith(allowed):
                return False
        return True

    def formatError(self, e, lineCorrector):
        eLine = e.line
        msg = e.message
        if lineCorrector:
            # adjust error line
            eLine = e.line - lineCorrector
            # probably there is a line reference in our error, adjust them
            number = re.search("line ([0-9]+)", msg)
            if number:
                orgNum = int(number.group(1))
                newNum = orgNum - lineCorrector
                orgStr = 'line %s' % orgNum
                newStr = 'line %s' % newNum
                msg = msg.replace(orgStr, newStr)
        return '%s%s, line: %s, block: %s' % (self.indent, msg, eLine, e.column)

    def check(self, basename, filename, content, lines):
        error = None
        lineCorrector = 0
        if not (content.startswith('<html>') or \
                content.startswith('<!DOCTYPE') or \
                content.startswith('<!doctype')):
            content = HTML_WRAPPER % content
            lineCorrector = 5

        sc = cStringIO.StringIO(content)
        try:
            p = lxml.etree.XMLParser()
            ignored = lxml.etree.XML(content, p)
        except lxml.etree.XMLSyntaxError, e:
            msg = '\n'.join(
                [self.formatError(e, lineCorrector)
                 for e in p.error_log
                 if self.validateError(e)
                 ])
            if msg:
                error = msg[len(self.indent):]

        if isinstance(error, basestring):
            # something fatal occurred, use error as line
            yield self.log(None, error, None, 'fatal error')
