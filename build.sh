#!/bin/sh
python setup.py --command-packages=stdeb.command sdist_dsc --with-python3=True --no-python2-scripts=True bdist_deb
