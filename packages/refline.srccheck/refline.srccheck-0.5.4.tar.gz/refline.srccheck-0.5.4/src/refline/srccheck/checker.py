##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Sourcecode checker, to be used in unittests
"""

import logging
import os
import os.path
import string
import polib
import fnmatch

from cssutils import parse
from refline.srccheck import pyflakes

INDENT = '  '


class BaseChecker(object):
    fnameprinted = False
    filename = None
    basename = None
    error = None

    def log(self, lineidx=0, line=None, pos=None, noInfo=False):
        if not self.fnameprinted:
            # always slash please, for cross platform stability
            filename = self.filename.replace('\\', '/')
            filename = filename[len(self.basename) + 1:]
            print
            print filename
            print '-' * len(filename)
            self.fnameprinted = True

        print "%s%s" % (INDENT, self.error)

        if noInfo:
            return

        lineidx = str(lineidx + 1) + ': '
        print "%s%s%s" % (INDENT, lineidx, line)
        if pos is not None:
            print "%s%s^" % (INDENT, ' ' * (len(lineidx) + pos))

    def check(self, filename, content, lines):
        pass

    def __call__(self, basename, filename, content, lines):
        self.fnameprinted = False
        self.filename = filename
        self.basename = basename

        return self.check(filename, content, lines)


class TabChecker(BaseChecker):
    error = 'Tab found in file'

    def check(self, filename, content, lines):
        for lineidx, line in enumerate(lines):
            if '\t' in line:
                pos = line.index('\t')
                self.log(lineidx, line, pos)

VALIDCHARS = string.printable


class NonAsciiChecker(BaseChecker):
    error = 'Non ASCII char found in line'

    def check(self, filename, content, lines):
        for lineidx, line in enumerate(lines):
            for pos, c in enumerate(line):
                if c not in VALIDCHARS:
                    self.log(lineidx, line, pos)
                    break


class BreakChecker(BaseChecker):
    error = 'Breakpoint found in line'

    def check(self, filename, content, lines):
        for lineidx, line in enumerate(lines):
            if 'pdb.set_trace' in line \
                and not (-1 < line.find('#') < line.find('pdb.set_trace')):
                self.log(lineidx, line)

            if 'from dbgp.client import brk; brk(' in line \
                and not (-1 < line.find('#') < line.find('dbgp.client.brk')):
                self.log(lineidx, line)

            if 'import rpdb2; rpdb2.start_embedded_debugger' in line \
                and not (-1 < line.find('#') < line.find(
                'rpdb2.start_embedded_debugger')):
                self.log(lineidx, line)


class OpenInBrowserChecker(BaseChecker):
    error = 'openInBrowser found in line'

    def check(self, filename, content, lines):
        for lineidx, line in enumerate(lines):
            if 'openInBrowser' in line \
                and not (-1 < line.find('#') < line.find('openInBrowser')):
                self.log(lineidx, line)


class PyflakesChecker(BaseChecker):
    error = 'pyflakes warning'

    def fixcontent(self, lines):
        if not lines:
            return ''
        #pyflakes does not like CRLF linefeeds
        #and files ending with comments
        idx = len(lines) - 1
        lastline = lines[idx].strip()
        while idx >= 1 and (lastline == '' or lastline.startswith('#')):
            del lines[idx]
            idx -= 1
            lastline = lines[idx].strip()

        content = '\n'.join(lines)
        return content

    def check(self, filename, content, lines):
        if not content:
            return
        if "##ignore PyflakesChecker##" in content:
            return

        content = self.fixcontent(lines)
        try:
            result = pyflakes.check(content, filename)
        except Exception, e:
            result = "Fatal exception in pyflakes: %s" % e

        if isinstance(result, basestring):
            #something fatal occurred
            self.error = result
            self.log(noInfo=True)
        else:
            #there are messages
            for warning in result:
                if ('undefined name' in warning.message
                    and not 'unable to detect undefined names' in warning.message):
                    self.error = warning.message % warning.message_args
                    self.log(warning.lineno - 1, lines[warning.lineno - 1])


class ConsoleLogChecker(BaseChecker):
    error = 'Breakpoint found in line'

    def check(self, filename, content, lines):
        for lineidx, line in enumerate(lines):
            if 'console.log' in line \
                and not (-1 < line.find('//') < line.find('console.log')):
                self.log(lineidx, line)


class POChecker(BaseChecker):
    error = 'Fuzzy/untranslated found'

    def check(self, filename, content, lines):
        pos = polib.pofile(filename)
        untrans = pos.untranslated_entries()
        fuzzy = pos.fuzzy_entries()

        if len(untrans) > 0:
            self.log(0, "%s untranslated items" % len(untrans))

        if len(fuzzy) > 0:
            self.log(0, "%s fuzzy items" % len(fuzzy))


class JPGChecker(BaseChecker):
    error = 'Image bloat found'

    def check(self, filename, content, lines):
        if "ns.adobe.com" in content:
            self.log(0, "Adobe Photoshop bloat found")
            return

        if "<rdf:RDF" in content:
            self.log(0, "RDF bloat found")
            return

        if len(content) < 500:
            return

        compressed = content.encode('zlib')
        ratio = len(compressed) / float(len(content) - 200)
        #200= circa static header length

        if ratio < 0.8:
            self.log(0, "Some other bloat found, compression ratio: %s" %ratio)
            return


class PTFragmentNeedsDomain(BaseChecker):
    error = "A PT fragment needs i18n:domain otherwise it won't be translated"

    def check(self, filename, content, lines):
        if '<html' in content:
            #not a fragment
            return

        if not 'i18n:translate' in content:
            #no translation
            return

        if not 'i18n:domain' in content:
            #bummer, here we go
            self.log(noInfo=True)


class CSSLogger(object):
    # this is a fake logger that redirects the actual logging calls to us

    def __init__(self, checker):
        self.checker = checker

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
            self.checker.error = str(msg)
        except UnicodeEncodeError:
            # unicode in doctests drives me mad
            self.checker.error = msg.encode('ascii', 'replace')
        # can't add much help, all info is encoded in msg
        self.checker.log(noInfo=True)

    warn = error
    critical = error
    fatal = error


class CSSChecker(BaseChecker):
    error = 'CSS'

    def check(self, filename, content, lines):
        parse.CSSParser(log=CSSLogger(self),
                        loglevel=logging.WARN,
                        validate=True).parseString(content)


PY_CHECKS = [
    TabChecker(),
    NonAsciiChecker(),
    BreakChecker(),
    OpenInBrowserChecker(),
    PyflakesChecker(),
    ]
PT_CHECKS = [
    TabChecker(),
    NonAsciiChecker(),
    ConsoleLogChecker(),
    PTFragmentNeedsDomain(),
    ]
JS_CHECKS = [
    TabChecker(),
    NonAsciiChecker(),
    ConsoleLogChecker(),
    ]
TXT_CHECKS = [
    TabChecker(),
    NonAsciiChecker(),
    BreakChecker(),
    OpenInBrowserChecker(),
    ]
PO_CHECKS = [
    POChecker(),
]
JPG_CHECKS = [
    JPGChecker(),
]
ZCML_CHECKS = [
]
CSS_CHECKS = [
    CSSChecker(),
]

CHECKS = {
    'py':   PY_CHECKS,
    'pt':   PT_CHECKS,
    'html': PT_CHECKS,
    'js':   JS_CHECKS,
    'txt':  TXT_CHECKS,
    'po':   PO_CHECKS,
    'jpg':  JPG_CHECKS,
    'zcml': ZCML_CHECKS,
    'css':  CSS_CHECKS,
}


class checker(object):
    checks = None
    extensions = None

    def __init__(self, module, checks=CHECKS, ignoreFiles=()):
        self.module = module
        self.checks = checks

        self.extensions = tuple(checks.keys())
        self.ignoreFiles = ignoreFiles

    def run(self):
        top = os.path.dirname(self.module.__file__)

        for root, dirs, files in os.walk(top, topdown=True):
            #keep the name order
            dirs.sort()
            files.sort()
            for name in files:
                ignoreThis = False
                for ignore in self.ignoreFiles:
                    if fnmatch.fnmatch(name, ignore):
                        ignoreThis = True
                if ignoreThis:
                    continue

                justname, ext = os.path.splitext(name)
                fullname = os.path.join(root, name)
                ext = ext.replace('.', '')

                if ext in self.extensions:
                    #read file once, pass the content to checkers
                    content = open(fullname, 'rb').read()

                    if 'checker_ignore_this_file' in content:
                        continue

                    lines = content.splitlines()

                    for check in self.checks[ext]:
                        check(top, fullname, content, lines)
