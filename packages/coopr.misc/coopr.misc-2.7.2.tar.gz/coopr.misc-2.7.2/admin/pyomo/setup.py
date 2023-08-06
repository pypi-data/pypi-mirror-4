import sys
sys.path.append("../..")
from distutils.core import setup
import py2exe

setup(console=['../../bin/pyomo'])
