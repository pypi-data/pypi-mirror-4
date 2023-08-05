======
README
======

This package provides a release helper script which can get used for svn based
repository development. The script will do all the steps which are required
forrelease a package and add a dev marker if done. A new package release will
get uploaded to the right pypi based on the package url. If authentication is
required, the script will find them in your HOME/.pypirc configuration file.
This means there is no configuration required if your package meta data is
correct defined and your "python setup.py sdist upload" command works.


Requirement
-----------

Before using the script make sure the following requirements are fine::

  - correct <HOME>/.pypirc setup

  - pypi package server tweaks in setup.py (see Server Lock below)

  - working "python setup.py sdist upload" command

  - correct meta data (url, version) in <package>/setup.py
  
  - existing CHANGES.txt file in your package


Setup
-----

You can setup the p01.releaser as a buildout part using the offered entry_point.
See setup.py. But I recommend not using the script as a buildout part in your
package because it will include the part in your deployment.

The recommended way to use the script is to link the p01.releaser package as
an svn external in your package <root> next to your other packages. It doesn't
matter which svn layout structure you are using. The release script will
automaticaly detect the svn repository layout and find the relevant folders.
With such a setup, you can go to the p01.releaser package and call the
release command. Of corse, you have to run::

  python bootstrap.py
  bin/buildout

before you can use the method::

  bin/release

The releaser script will find the correct package and tag folder based on your
svn layout. See below for more information about the common svn repository
layout structure.


Note
----
The release method will only release the package if something changed since the
last release. The release method will also not start the release process if
there is pending (not commited) code in your package. And the release method
supports you by adding comments to the CHANGES.txt.


SVN
---

We support 2 kind of svn layout. The first layout is the default layout used
for independent python libraries. Each package provdies own branches, tags and
trunk folders::

  - <root> (svn layout detection rule: can't use trunk as name)
    |
    |- p01.releaser (cwd location)
    |  |
    |   - bin
    |     |
    |      - releaser.py (releaser.exe)
    |
    |- package1
    |  |
    |   - branches
    |  |
    |   - tags
    |  |  |
    |  |   - 0.5.0 (version)
    |  |
    |  |- trunk
    |     |
    |      - src ...
    |
     - package1
       |
        - branches
       |
        - tags
       |  |
       |   - 0.5.0 (version)
       |
       |- trunk
          |
           - src ...

The second svn layout is used for frameworks or other group of packages.
Each package is located in the same trunk folder and they share branches and
tags folders. This layout provides the option to simply tag all packages in
one step::

  - <root>
    |
     - branches
    |
     - tags
    |  |
    |   - package1
    |     |
    |      - 0.5.0 (version)
    |
     - trunk
       |
       |- p01.releaser (cwd location)
       |  |
       |   - bin
       |     |
       |      - releaser.py (releaser.exe)
       |
       |- package1
       |  | 
       |   - src ..
       |
        - package2
          | 
           - src ..


Server Lock
-----------

The p01.releaser script will upload a relase to the pypi server found based on
the <HOME>/.pypirc information. This should prevent that a release accidently
get uploaded to the official public pypi server. But remember, the package meta
data in <package>/setup.py must proide te correct url. And if you start the
release process by hand with the command "python.setup.py sdist upload" you
will release to the public pypi server which is probably not what you want.

Our solution which we use for private packages is the following. We use a
mypypi server and a locker.py script in each of our private packages. This
script provides the following content::

    import sys
    import os.path
    from ConfigParser import ConfigParser
    
    
    #---[ repository locking ]-----------------------------------------------------
    
    def getRepository(name):
        """Return repository server defined in  .pypirc file"""
        server = None
        # find repository in .pypirc file
        rc = os.path.join(os.path.expanduser('~'), '.pypirc')
        if os.path.exists(rc):
            config = ConfigParser()
            config.read(rc)
            if 'distutils' in config.sections():
                # let's get the list of servers
                index_servers = config.get('distutils', 'index-servers')
                _servers = [s.strip() for s in index_servers.split('\n')
                            if s.strip() != '']
                for srv in _servers:
                    if srv == name:
                        repos = config.get(srv, 'repository')
                        print "Found repository %s for %s in '%s'" % (repos,name,rc)
                        server = repos
                        break
        if not server:
            print "No repository for %s found in '%s'" % (name, rc)
            sys.exit(1)
        else:
            return server
        
    def lockRelease(name):
        """Lock repository if we use the register or upload command"""
    
        COMMANDS_WATCHED = ('register', 'upload')
        changed = False
        server = None
    
        for command in COMMANDS_WATCHED:
            if command in sys.argv:
                # now get the server from pypirc
                if server is None:
                    server = getRepository(name)
                # found one command, check for -r or --repository
                commandpos = sys.argv.index(command)
                i = commandpos+1
                repo = None
                while i<len(sys.argv) and sys.argv[i].startswith('-'):
                    # check all following options (not commands)
                    if (sys.argv[i] == '-r') or (sys.argv[i] == '--repository'):
                        #next one is the repository itself
                        try:
                            repo = sys.argv[i+1]
                            if repo.lower() != server.lower():
                                print "You tried to %s to %s, while this package "\
                                       "is locked to %s" % (command, repo, server)
                                sys.exit(1)
                            else:
                                #repo OK
                                pass
                        except IndexError:
                            #end of args
                            pass
                    i += 1
    
                if repo is None:
                    #no repo found for the command
                    print "Adding repository %s to the command %s" % (
                        server, command )
                    sys.argv[commandpos+1:commandpos+1] = ['-r', server]
                    changed = True
    
        if changed:
            print "Final command: %s" % (' '.join(sys.argv))

With this locker.py script, you can simply lock the release to an own pypi
server with the following command in your setup.py file::

    import locker
    locker.lockRelease("projekt01")

The single lockRelease method argument must be an existing index-servers name
defined in your <HOME>/.pypirc file. The .pypirc file could look like::

    [distutils]
    index-servers = pypi
                    mypypi

    [pypi]
    repository: http://pypi.python.org/pypi
    username:<username>
    password:<password>
    
    [mypypi]
    repository: http://pypi.domain.tld
    username:<username>
    password:<password>

This locker.py script concept is a seatbelt an prevents any release file upload
to a wrong pypi server with or without the p01.releaser scipt. Remember the 
releaser script will find it's correct server without this script. But it's
allwayys a good idea to backup the concept if you have important libraries.


Issues
------

Just like to remember that distutils is broken because of a bad re pattern.
It is not possible to include buildout.cfg or other files starting with
``build`` on windows. This is only relevant if you need to include additional
package data with ``include_package_data=True``. After patching your pyhton
installation it should be fine to include a MANIFST.in file with:

  include buildout.cfg

see:

  http://bugs.python.org/issue6884
