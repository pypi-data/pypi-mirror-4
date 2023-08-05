=======
Summary
=======

install
-------

Download and unzip this package next to your other packages in your local svn
folder structure. After that, install the p01.releaser package by running the
following commands on linux:

  python bootstrap.py

  bin/buildout

windows:

  python bootstrap.py

  bin\buildout.exe


release
-------

You can use the release method with the following command for make a new or
next release.

nix:

  bin/release <package-name>

windows:

  bin\release.exe <package-name>


With this command the release script will do the following for the package
with the given name:

  - check for pending local modification

  - find existing versions

  - get next version based on options (-n, --next-version)

  - guess next version if nothing defined in options

  - ask for confirm guessed version or set explicit/initial version

  - ask for CHANGES.txt release text confirmation if already exist
  
  - or offer inplace CHANGES.txt editing if empty confirmed

After this, the srcipt will start an automated build process and abort on any
error. Note an error could end in partial commited svn data or a missing
release file. But this should be simple to check and correct. The steps are:

  - update version in CHANGES.txt if not already updated during editing

  - update version in setup.py

  - commit version change (local pkg dir)

  - create release based on setup.py (local pkg dir)

  - ensure tags folder if new package get release

  - tag package (svn cp tags/pkgName/version)

  - guess next release version

  - add next version and unreleased marker in CHANGES.txt

  - add next version including dev marker in setup.py

  - commit setup.py and CHANGES.txt dev marker update

Now you are done and the release should be ready.


in short
--------

In short, the releae script should normal only do the following steps:

  - ask for new guessed version confirmation
  
  - ask for CHANGES.txt confirmation or offer editing

and the release should just start.


credits
-------

This package is a kind of simple version of keas.build for one package. The
keas.build package offers support for build several release based on
configuration files. This is usefull if you need to make several releases
based on deifferent packages but not for release the package itself.
