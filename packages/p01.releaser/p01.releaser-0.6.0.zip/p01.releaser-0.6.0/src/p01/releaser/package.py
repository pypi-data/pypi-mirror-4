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
"""Build a release based on keas.build.package

$Id:$
"""
__docformat__ = 'ReStructuredText'

import logging
import os
import pkg_resources
import re
import shutil
import sys
import stat
from xml.etree import ElementTree

import p01.releaser.base
import p01.releaser.pypi


logger = p01.releaser.base.logger
formatter = p01.releaser.base.formatter
parser = p01.releaser.base.parser


class PackageBuilder(object):

    pkg = None
    options = None

    pkgURL = None
    tagURL = None
    pypiURL = None
    svn = None

    def __init__(self, pkgName, options):
        self.pkgName = pkgName
        self.options = options
        self.setup()

    def setup(self):
        """Setup svn and locations"""
        # setup simple svn command wrapper
        self.svn = p01.releaser.base.SVN()

        # setup local pkg directory based on cwd dir which is our p01.releaser
        # folder (one up + pkgName)
        cwdDir = os.getcwd()
        parentDir = os.path.normpath(os.path.join(cwdDir, '..'))
        pkgsDir = os.path.normpath(os.path.join(parentDir, '..'))
        parentName = os.path.basename(parentDir)

        # find package, tags directories and urls based on svn layout
        if parentName == 'trunk':
            # svn grouped package layout sharing one trunk folder
            pkgDir = os.path.join(pkgsDir, 'trunk', self.pkgName)
            self.pkgDir = os.path.normpath(pkgDir)
            if not os.path.exists(self.pkgDir):
                logger.error('Package `%s` does not exist' % self.pkgDir)
                logger.error('ABORTED')
                sys.exit(1)
            logger.debug('define package dir: %s' % self.pkgDir)
            tagDir = os.path.join(pkgsDir, 'tags', self.pkgName)
            self.tagDir = os.path.normpath(tagDir)
            logger.debug('define tag dir: %s' % self.tagDir)

            # setup pkgURL and other svn urls based on local package svn info
            xml = self.svn.info(self.pkgDir)
            elem = ElementTree.fromstring(xml)
            # root
            # https://svn.projekt01.ch/svn/p01
            # url
            # https://svn.projekt01.ch/svn/p01/packages/trunk/p01.tmp
            rootURL = elem.find('entry').find("repository").find('root').text
            self.pkgURL = elem.find('entry').find("url").text
            logger.debug('define package url: %s' % self.pkgURL)
            parts = self.pkgURL.split('/')
            # remove trunk and pkgName
            rootParts = parts[:-2]
            rootURL = '/'.join(rootParts)
            self.tagURL = '%s/%s/%s' % (rootURL, 'tags', self.pkgName)
            logger.debug('define tag url: %s' % self.tagURL)
        else:
            # svn single package layout with trunk in every package
            pkgDir = os.path.join(pkgsDir, self.pkgName, 'trunk')
            self.pkgDir = os.path.normpath(pkgDir)
            if not os.path.exists(self.pkgDir):
                logger.error('Package `%s` does not exist' % self.pkgDir)
                logger.error('ABORTED')
                sys.exit(1)
            logger.debug('define package dir: %s' % self.pkgDir)
            tagDir = os.path.join(pkgsDir, self.pkgName, 'tags')
            self.tagDir = os.path.normpath(tagDir)
            logger.debug('define tag dir: %s' % self.tagDir)

            # setup pkgURL and other svn urls based on local package svn info
            xml = self.svn.info(self.pkgDir)
            elem = ElementTree.fromstring(xml)
            # root
            # https://svn.projekt01.ch/svn/p01
            # url
            # https://svn.projekt01.ch/svn/p01/packages/p01.tmp/trunk
            self.pkgURL = elem.find('entry').find("url").text
            logger.debug('define package url: %s' % self.pkgURL)
            parts = self.pkgURL.split('/')
            rootParts = parts[:-1]
            rootURL = '/'.join(rootParts)
            self.tagURL = '%s/%s' % (rootURL, 'tags')
            logger.debug('define tag url: %s' % self.tagURL)

        # check pending changes
        xml = self.svn.status(self.pkgDir)
        elem = ElementTree.fromstring(xml)
        self.pendingChanges = []
        for elem in elem.findall('./target/entry'):
            item = elem.find('wc-status').get('item')
            if item == 'modified':
                path = elem.get('path')
                self.pendingChanges.append({'path': path,
                                            'status': item} )
                logger.info('Pending changes at: %s ' % path)

        # load pypi url from pkg setup.py
        self.pypiURL = p01.releaser.base.getPYPIURLFromPKG(self.pkgDir,
            self.pkgName)

    def getTagURL(self, version):
        tagURL = '%s/%s' %(self.tagURL, version) 
        logger.debug('define tag URL: %s' % tagURL)
        return tagURL

    def getRevision(self, url):
        #xml = base.do('svn info --xml %s' % url)
        xml = self.svn.info(url, defaultOnError=None)
        if xml is None:
            revision = 0
        else:
            elem = ElementTree.fromstring(xml)
            revision = elem.find("entry").find("commit").get("revision")
            if not revision:
                revision = 0
            else:
                revision = int(revision)
        logger.debug('package revision for %s: %i' %(url, revision))
        return revision

    def findVersions(self):
        logger.debug('package index: %s' % self.pypiURL)
        versions = p01.releaser.pypi.getPackageVersions(self.pypiURL,
            self.pkgName)

        logger.debug('all versions: %s' % ' '.join(versions))
        return sorted(versions, key=lambda x: pkg_resources.parse_version(x))

    def hasChangedSince(self, lastVersion):
        tagURL = self.getTagURL(lastVersion)
        pkgRevision = self.getRevision(self.pkgURL)
        changed = pkgRevision - 1 != self.getRevision(tagURL)
        if changed:
            logger.info(
                'trunk changed since the release of version %s' % lastVersion)
        return changed

    def ensureTagFolder(self):
        if not os.path.exists(self.tagDir):
            logger.debug("added tags folder `%s`" % self.tagDir)
            # make tag dir
            os.mkdir(self.tagDir)
            # commit tag dir
            self.svn.add(self.tagDir)
            logger.debug("commit tags folder `%s`" % self.tagDir)
            self.svn.ci(self.tagDir, "added (by p01.releaser)")

    def openChangeEditor(self, version):
        # start an editor
        cPath = os.path.join(self.pkgDir, 'CHANGES.txt')
        p01.releaser.base.openEditor(cPath)
        answer = p01.releaser.base.getInput(
                'Do you like to continue (y)es/(n)o', 'yes', False)
        if answer.startswith('y'):
            # start again with release
            self.startRelease(version)
        else:
            logger.info('ABORTED')
            sys.exit(1)

    def confirmChanges(self, doc, version):
        # get changes
        changes = doc.getReleaseText()
        if not changes:
            logger.info(
                'CHANGES.txt contains no text, add some and continue')
            self.openChangeEditor(version)
        elif not self.options.ignoreChanges:
            # confirm change text
            print "Whould you like accept or edit CHANGES.txt"
            for t in changes.split('\n'):
                print t
            accept = p01.releaser.base.getInput(
                '(a)ccept/(e)dit', 'accept', False)
            if accept.startswith('a'):
                return True
            elif accept.startswith('e'):
                logger.info('Edit Changes.txt and continue')
                self.openChangeEditor(version)

    def testRelease(self, version):
        if self.options.ignoreTesting:
            check = 'no'
        else:
            check = p01.releaser.base.getInput(
                    'Do you like to run tests (y)es/(n)o', 'yes', False)
        if check.startswith('y'):
            if p01.releaser.base.is_win32:
                cmd = 'test.exe'
            else:
                cmd = 'test'
            binDir = os.path.join(self.pkgDir, 'bin')
            cmd = p01.releaser.base.buildCommand(binDir, cmd)
            logger.info('run test for %r with cmd %s' % (self.pkgName, cmd))
            stdout = p01.releaser.base.do(cmd, cwd=self.pkgDir,
                defaultOnError='error', removePythonPath=True)
            if stdout:
                for line in stdout.split('\n'):
                    # skip last empty line
                    if line:
                        print line

    def startRelease(self, version):
        logger.info('creating release for %r with version %s from trunk' %(
            self.pkgName, version))

        # setup doc wrapper
        sPath = os.path.join(self.pkgDir, 'CHANGES.txt')
        doc = p01.releaser.base.ChangeDoc(sPath)
        if not self.confirmChanges(doc, version):
            return False
        else:
            # update version
            doc.setRelease(version)
            doc.save()

        # update version in setup.py
        logger.info("update setup.py version to `%s`" % version)
        spy = file(os.path.join(self.pkgDir, 'setup.py'), 'r').read()
        spy = re.sub("version( )?=( )?'(.*)',", "version = '%s'," % version, spy)
        file(os.path.join(self.pkgDir, 'setup.py'), 'w').write(spy)

        # commit version change (still in trunk)
        logger.info('commit prepare release')
        self.svn.ci(self.pkgDir,
            "prepare release %s (by p01.releaser)" % version)
        
        # create release based on setup.py (still in trunk)
        logger.info("python setup.py register sdist upload")
        p01.releaser.base.do('python setup.py register sdist upload',
            cwd=self.pkgDir)

        # ensure tags folder
        self.ensureTagFolder()

        # tag package (move to tags/pkgName/version or pkgName/tags/version)
        tagURL = self.getTagURL(version)
        logger.info('creating release tag at %s' % tagURL)
        self.svn.cp(self.pkgURL, tagURL, "tag %s release" % version)

        # get next version
        nextVersion = p01.releaser.base.guessNextVersion(version)

        # add dev/unreleased marker in CHANGES.txt
        logger.info('CHANGES.txt add dev marker`%s`' % nextVersion)
        doc.back2Dev(nextVersion)
        doc.save()

        # add dev marker in setup.py
        logger.info('setup.py add dev marker`%sdev`' % nextVersion)
        spy = file(os.path.join(self.pkgDir, 'setup.py'), 'r').read()
        spy = re.sub(
            "version( )?=( )?'(.*)',", "version = '%sdev'," % nextVersion, spy)
        file(os.path.join(self.pkgDir, 'setup.py'), 'w').write(spy)

        # commit dev marker
        logger.info('commit dev marker')
        self.svn.ci(self.pkgDir, "back to dev (by p01.releaser)")
        
        # update pkg directory
        logger.info('update package directory')
        self.svn.up(self.pkgDir)
        
        # update pkg directory
        if not self.options.ignoreUpdateTags:
            logger.info('update tags directory')
            self.svn.up(self.tagDir)

        logger.info("DONE")

    def runCLI(self):
        logger.info('start releasing new version of %s' % self.pkgName)
        if self.pendingChanges:
            logger.info(
                'you have pending modifications in your local repository at:')
            for entry in self.pendingChanges:
                 logger.info('- %s' % entry['path'])
            logger.info('commit pending modifications before release')
            logger.info('ABORTED')
            return 

        localRevision = self.getRevision(self.pkgDir)
        svnRevision = self.getRevision(self.pkgURL)
        if localRevision != svnRevision:
            logger.info('locale revison `%s` does not compare with '
                        'svn revision `%s`. Update your trunk before release'
                        % (localRevision, svnRevision))
            logger.info('ABORTED')
            return

        # find all versions.
        versions = self.findVersions()
        if versions:
            logger.info('existing `%s` versions: %s' % (
                self.pkgName, ' | '.join(reversed(versions))))

        # determine the default version to suggest.
        nextVersion = self.options.nextVersion
        changed = False

        if versions and nextVersion is None:
            last = versions[-1]
            logger.info(
                'checking for changes since version %s; please wait...', last)
            # check whether the trunk changed since the last release
            if self.hasChangedSince(last):
                nextVersion = p01.releaser.base.guessNextVersion(last)
            else:
                logger.info('nothing changed since last release')
                logger.info('ABORTED')
                return

        # check externals
        if not self.options.ignoreExternals:
            p01.releaser.base.checkExternals(self.pkgDir)
            logger.info('extends and develop external checked')
            

        # run test before ask about version
        self.testRelease(nextVersion)

        if nextVersion is None:
            # ask for initial version
            nextVersion = p01.releaser.base.getInput(
                'set initial version for `%s`: ' % self.pkgName, '', False)
        else:
            # confirm/set next version
            nextVersion = p01.releaser.base.getInput(
                'set version for `%s`' % self.pkgName, nextVersion,
                self.options.quiet)

        if nextVersion == '':
            # double check again
            logger.info('empty version given')
            logger.info('ABORTED')
            return
        elif nextVersion in versions:
            logger.info('the version %s already exists' % nextVersion)
            logger.info('ABORTED')
        else:
            # create a release for this version
            logger.info('choose release version: `%s`' % nextVersion)
            self.startRelease(nextVersion)


def main(args=None):
    # Make sure we get the arguments.
    if args is None:
        args = sys.argv[1:]
    if not args:
        args = ['-h']

    # Set up logger handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Parse arguments
    options, args = parser.parse_args(args)

    logger.setLevel(logging.INFO)
    if options.verbose:
        logger.setLevel(logging.DEBUG)

    if len(args) == 0:
        print "No package was specified."
        print "Usage: build-package [options] package1 package2 ..."
        sys.exit(0)

    if len(args) > 1:
        print "More then one package was specified."
        print "Usage: release [options] <package-name>."
        sys.exit(0)

    pkg = args[0]
    builder = PackageBuilder(pkg, options)
    try:
        builder.runCLI()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")
        sys.exit(0)

    # Remove the handler again.
    logger.removeHandler(handler)

    # Exit cleanly.
    sys.exit(0)
