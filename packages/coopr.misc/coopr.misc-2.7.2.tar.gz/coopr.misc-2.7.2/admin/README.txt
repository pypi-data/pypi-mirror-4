This directory contains a Makefile that is handy for building
a pyomo distribution from Cygwin.  Note: this assume that Python
is installed natively on Windows, and that py2exe has been installed
with this Python installation.

NOTES:

python setup.py sdist --format=tar
python setup.py sdist --format=gztar
python setup.py sdist --format=bztar
python setup.py sdist --format=zip
python setup.py sdist --format=ztar
