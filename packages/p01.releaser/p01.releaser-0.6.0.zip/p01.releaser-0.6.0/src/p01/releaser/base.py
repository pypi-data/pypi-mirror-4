###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""Internals

$Id:$
"""
__docformat__ = 'ReStructuredText'

import ConfigParser
import datetime
import logging
import optparse
import os
import pkg_resources
import re
import subprocess
import sys
import webbrowser

logger = logging.Logger('p01.releaser')
formatter = logging.Formatter('%(levelname)s - %(message)s')

is_win32 = sys.platform == 'win32'

RE_SETUP_URL = re.compile("url ?= ?'(.*)',")

RE_VERSION = re.compile(
    r"(?P<version>^[0-9a-z.]+)\s*\((?P<date>unreleased|[0-9.-]+)\)", re.VERBOSE)

_marker = object()


def buildCommand(cmdDir, cmd, oStr=None):
    if oStr is not None:
        return '%s %s' % (os.path.join(cmdDir, cmd), oStr)
    else:
        return os.path.join(cmdDir, cmd)


def do(cmd, cwd=None, captureOutput=True, defaultOnError=_marker,
    removePythonPath=False):
    if removePythonPath:
        env = os.environ
        if os.environ.get('PYTHONPATH'):
            del env['PYTHONPATH']
    logger.debug('command: ' + cmd)
    if captureOutput:
        stdout = stderr = subprocess.PIPE
    else:
        stdout = stderr = None
    p = subprocess.Popen(
        cmd, stdout=stdout, stderr=stderr,
        shell=True, cwd=cwd)
    stdout, stderr = p.communicate()
    if stdout is None:
        stdout = "see output above"
    if stderr is None:
        stderr = "see output above"
    if p.returncode != 0:
        if defaultOnError == _marker:
            logger.error(u'an error occurred while running command: %s' %cmd)
            logger.error('error output: \n%s' % stderr)
            sys.exit(p.returncode)
        else:
            return defaultOnError
    logger.debug('output: \n%s' % stdout)
    return stdout


def checkRO(function, path, excinfo):
    if (function == os.remove
        and excinfo[0] == WindowsError
        and excinfo[1].winerror == 5):
        #Access is denied
        #because it's a readonly file
        os.chmod(path, stat.S_IWRITE)
        os.remove(path)


def rmtree(dirname):
    if is_win32:
        shutil.rmtree(dirname, ignore_errors=False, onerror=checkRO)
    else:
        shutil.rmtree(dirname)


class SVN(object):
    """SVN command wrapper"""

    user = None
    passwd = None
    forceAuth = False

    #TODO: spaces in urls+folder names???

    def __init__(self, user=None, passwd=None, forceAuth=False):
        self.user = user
        self.passwd = passwd
        self.forceAuth = forceAuth

    def _addAuth(self, command):
        auth = ''
        if self.user:
            auth = '--username %s --password %s' % (self.user, self.passwd)
            if self.forceAuth:
                auth += ' --no-auth-cache'
        command = command.replace('##__auth__##', auth)
        return command

    def info(self, url, defaultOnError=_marker):
        command = 'svn info --non-interactive ##__auth__## --xml %s' % url
        command = self._addAuth(command)
        return do(command, defaultOnError=defaultOnError)

    def ls(self, url):
        command = 'svn ls --non-interactive ##__auth__## --xml %s' % url
        command = self._addAuth(command)
        return do(command)

    def cp(self, fromurl, tourl, comment):
        command = 'svn cp --non-interactive ##__auth__## -m "%s" %s %s' %(
            comment, fromurl, tourl)
        command = self._addAuth(command)
        do(command)

    def co(self, url, folder):
        command = 'svn co --non-interactive ##__auth__## %s %s' % (url, folder)
        command = self._addAuth(command)
        do(command)

    def add(self, folder):
        command = 'svn add --non-interactive ##__auth__## %s' % folder
        command = self._addAuth(command)
        do(command)

    def ci(self, folder, comment):
        command = 'svn ci --non-interactive ##__auth__## -m "%s" %s' % (
            comment, folder)
        command = self._addAuth(command)
        do(command)

    def up(self, folder):
        command = 'svn up --non-interactive ##__auth__## "%s"' % folder
        command = self._addAuth(command)
        do(command)

    def status(self, pkgDir):
        command = 'svn status --non-interactive ##__auth__## --xml %s' % pkgDir
        command = self._addAuth(command)
        return do(command)


# TODO: whould be nice to block and on edotr close fetch the CHANGES.txt
#       but it seems thats not so easy because if the file get opend in an
#       already open editor it's not possible to block becaues some editor
#       will just return and not block with subprocess.call()
def openEditor(cPath):
    """Open an editor with CHANGES.txt"""
    try:
        # this should open text files with our preferred text editor
        webbrowser.open(cPath)
    except:
        # just leave and forget for now
        pass


def guessNextVersion(version):
    pieces = pkg_resources.parse_version(version)
    newPieces = []
    for piece in pieces:
        try:
            newPieces.append(int(piece))
        except ValueError:
            break
    newPieces += [0]*(3-len(newPieces))
    newPieces[-1] += 1
    newVersion = '.'.join([str(piece) for piece in newPieces])
    logger.debug('Last Version: %s -> %s' %(version, newVersion))
    return newVersion


class Section(object):
    """Section which knows how to dump lines"""

    def __init__(self, version, date):
        self.version = version
        self.date = date
        self.lines = []

    @property
    def headline(self):
        return '%s (%s)' % (self.version, self.date)

    @property
    def underline(self):
        return '-' * (len(self.version) + len(self.date) + 3)

    @property
    def text(self):
        txt = self.headline
        txt += '\n'
        txt += '%s' % self.underline
        txt += '\n'
        txt += '\n'
        txt += '\n'.join(self.lines)
        txt += '\n'
        return txt

    def append(self, line):
        """Append lines at the end"""
        if not line:
            # skip empty lines
            return
        elif line.startswith('---'):
            # skip underlines
            return
        else:
            self.lines.append(line)

    def insert(self, line):
        """insert in front of other lines"""
        if len(self.lines) == 1 and self.lines[0] == EMPTY_RELEASE_TEXT:
            # remove initial content, also prevents to set it twice
            self.lines = []
        self.lines.insert(0, line)

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self.version, self.date)


class Sections(object):
    """Ordered section storage"""

    def __init__(self):
        self.data = {}
        self._keys = []
        self.current = None

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, item):
        if self.current is None:
            self.current = item
        if key not in self._keys:
            self._keys.append(key)
        else:
            raise KeyError("Key already exist", key)
        self.data[key] = item

    def get(self, key, default=None):
        """Get item by key"""
        return self.data.get(key, default)

    def keys(self):
        return self._keys

    def values(self):
        for key in self._keys:
            yield self.data[key]

    def items(self):
        for key in self._keys:
            yield key, self.data[key]

    def __iter__(self):
        for key in self._keys:
            yield self.data[key]

    def __repr__(self):
        return repr(self.data.values())


EMPTY_RELEASE_TEXT = '- ...'

class ChangeDoc(object):
    """Wrapper for CHANGES.txt file"""

    header = u"=======\nCHANGES\n=======\n"

    def __init__(self, path):
        if not os.path.exists(path):
            raise ValueError("Missing CHANGES.txt file at %s"  % path)
        self.path = path
        self._load()

    def _load(self):
        """Load data for each line"""
        f = open(self.path, 'rb')
        content = f.read()
        f.close()
        self.sections = Sections()
        content = content.replace('\r', '')
        section = None
        for line in content.split('\n')[4:]:
            line = line.strip()
            if not line:
                continue
            match = RE_VERSION.search(line)
            if match:
                version = match.group('version').strip()
                date = match.group('date'.strip())
                section = Section(version, date)
                self.sections[version] = section
            elif section is not None:
                # skip empty lines
                section.append(line)
            else:
                raise ValueError("Bad CHANGES.txt file format")

    def revert(self):
        self._load()

    @property
    def current(self):
        return self.sections.current

    def getSection(self, version='unreleased'):
        if version == 'unreleased':
            # unrelease must be the current or something is wrong
            if self.current.date != version:
                raise KeyError("Bad setup, current != unreleased", version)
            return self.current
        else:
            return self.sections[version]

    def getReleaseText(self):
        """Return content lines or raise KeyError"""
        lines = self.current.lines
        txt = '\n'.join(lines)
        if txt == EMPTY_RELEASE_TEXT:
            return ''
        else:
            return txt

    def hasReleaseText(self):
        lines = self.current.lines
        if not lines:
            return False
        elif len(lines) < 1:
            return False
        elif len(lines) > 0 and lines[0] != EMPTY_RELEASE_TEXT:
            return True
        else:
            return False

    def replaceReleaseText(self, text):
        """REpalce release text"""
        self.current.lines = text.split('\n')

    def appendReleaseText(self, text):
        """Append release text"""
        for line in text.split('\n'):
            self.current.append(line)

    def insertReleaseText(self, text):
        """insert release text"""
        for line in text.split('\n'):
            self.current.insert(line)

    def setRelease(self, version, date=None):
        """Set release date for unreleased version"""
        if self.current is None:
            raise ValueError("No unreleasd version found")
        else:
            self.current.version = version
            if date is None:
                date = datetime.datetime.today().strftime('%Y-%m-%d')
            self.current.date = date

    def save(self):
        """Set given version with some comment"""
        # first ensure that we allways update the version
        lines = []
        append = lines.append
        append(self.header)
        for section in self.sections.values():
            append(section.text)
        content = '\n'.join(lines)
        if os.path.exists(self.path):
            os.remove(self.path)
        f = open(self.path, 'w')
        f.write(content)
        f.close()

    def back2Dev(self, nextVersion=None):
        """Add unreleased version info and text based on last version in doc"""
        if nextVersion is None:
           nextVersion = guessNextVersion(self.current.version)
        section = Section(nextVersion, 'unreleased')
        section.lines = [EMPTY_RELEASE_TEXT]
        self.sections.current = section
        sections = Sections()
        sections[nextVersion] = section
        for k, v in self.sections.items():
            sections[k] = v
        self.sections = sections


def getPYPIURLFromPKG(pkgDir, pkgName, private=True):
    url = None
    path = os.path.join(pkgDir, 'setup.py')
    if os.path.exists(path):
        f = open(path, 'rb')
        content = f.read()
        f.close()
        match = re.search(RE_SETUP_URL, content)
        if match is not None:
            url = match.group(1)
            url = url[:-(len(pkgName)+1)]
    return url


def getInput(prompt, default, quiet=False):
    if quiet and default:
        return default
    defaultStr = ''
    if default:
        defaultStr = ' [' + default + ']: '
    value = raw_input(prompt + defaultStr)
    if not value:
        return default
    return value


def checkExternals(pkgDir, curDir=None, fileName=None, files=None):
    pkgDir = os.path.abspath(pkgDir)
    if curDir is None:
        curDir = pkgDir
    if fileName is None:
        fileName = 'buildout.cfg'

    fPath = os.path.join(curDir, fileName)
    fPath = os.path.abspath(fPath)
    config = ConfigParser.RawConfigParser()
    config.read(fPath)

    # check develope externals
    develops = ''
    try:
        develops = config.get('buildout', 'develop')
    except ConfigParser.NoSectionError:
        pass
    except ConfigParser.NoOptionError:
        pass

    developeParts = develops.split()
    for part in developeParts:
        # extends files are always relative to the actual file
        dPath = os.path.join(curDir, part)
        dPath = os.path.abspath(dPath)
        if not os.path.exists(dPath):
            logger.error("Develop path: `%s` not found, but is referenced by `%s`" % (
                dPath, fPath))
            logger.error("ABORTED")
            sys.exit(0)

        if not dPath.startswith(pkgDir):
            logger.error("Develop path: `%s` is not located in package `%s`" % (
                dPath, pkgDir))
            logger.error("ABORTED")
            sys.exit(0)

    # check extends externals
    extends = ''
    try:
        extends = config.get('buildout', 'extends')
    except ConfigParser.NoSectionError:
        pass
    except ConfigParser.NoOptionError:
        pass

    extendParts = extends.split()
    for part in extendParts:
        # extends files are always relative to the actual file
        ePath = os.path.join(curDir, part)
        ePath = os.path.abspath(ePath)
        if not os.path.exists(ePath):
            logger.error("Extends path: `%s` not found, but is referenced by `%s`" % (
                ePath, fPath))
            logger.error("ABORTED")
            sys.exit(0)

        if not ePath.startswith(pkgDir):
            logger.error("Extends path: `%s` is not located in package `%s`" % (
                ePath, pkgDir))
            logger.error("ABORTED")
            sys.exit(0)

        # get extends file folder
        dirPath = os.path.dirname(ePath)
        checkExternals(pkgDir, curDir, ePath)


# options
usage = "usage: release [options] <package-name>"
parser = optparse.OptionParser(usage)

parser.add_option(
    "-c", "--ignore-changes", action="store_true",
    dest="ignoreChanges", default=None,
    help="When set, the system does't check the CHANGES.txt file content.")

parser.add_option(
    "-d", "--use-defaults", action="store_true",
    dest="useDefaults", default=False,
    help="When specified, less user input is required and the defaults are used.")

parser.add_option(
    "-e", "--ignore-externals", action="store_true",
    dest="ignoreExternals", default=None,
    help="When set, the system ignores checking external extends path in buildout.cfg.")

parser.add_option(
    "-n", "--next-version", action="store_true",
    dest="nextVersion", default=None,
    help="When set, the system uses this version.")

parser.add_option(
    "-t", "--ignore-update-tags", action="store_true",
    dest="ignoreUpdateTags", default=None,
    help="When set, the system will not update the tags folder at the end.")

parser.add_option(
    "-u", "--ignore-testing", action="store_true",
    dest="ignoreTesting", default=None,
    help="When set, the system does't run tests.")

parser.add_option(
    "-v", "--verbose", action="store_true",
    dest="verbose", default=False,
    help="When specified, debug information is created.")

parser.add_option(
    "-q", "--quiet", action="store_true",
    dest="quiet", default=False,
    help="When specified, less user input is required and the defaults are used.")
