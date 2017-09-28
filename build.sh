#!/bin/sh
DISTCODENAME=$(facter --puppet lsbdistcodename)
PACKAGEITERATION=1
PACKAGENAME=numatuned

python3 setup.py --command-packages=stdeb.command sdist_dsc --with-python2=False --dist-dir=build --debian-version ${DISTCODENAME}${PACKAGEITERATION} --package $PACKAGENAME bdist_deb
