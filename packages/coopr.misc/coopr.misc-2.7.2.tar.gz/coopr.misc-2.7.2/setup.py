#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

"""
Script to generate the installer for coopr.misc.
"""

import glob
import os

def _find_packages(path):
    """
    Generate a list of nested packages
    """
    pkg_list=[]
    if not os.path.exists(path):
        return []
    if not os.path.exists(path+os.sep+"__init__.py"):
        return []
    else:
        pkg_list.append(path)
    for root, dirs, files in os.walk(path, topdown=True):
        if root in pkg_list and "__init__.py" in files:
            for name in dirs:
                if os.path.exists(root+os.sep+name+os.sep+"__init__.py"):
                    pkg_list.append(root+os.sep+name)
    return [pkg for pkg in map(lambda x:x.replace(os.sep,"."), pkg_list)]

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

from setuptools import setup
packages = _find_packages('coopr')

setup(name='coopr.misc',
      version='2.7.2',
      maintainer='William E. Hart',
      maintainer_email='wehart@sandia.gov',
      url = 'https://software.sandia.gov/svn/public/coopr/coopr.misc',
      license = 'BSD',
      platforms = ["any"],
      description = 'Miscellaneous Coopr utilities',
      long_description = read('README.txt'),
      classifiers = [
            'Development Status :: 4 - Beta',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: Unix',
            'Programming Language :: Python',
            'Programming Language :: Unix Shell',
            'Topic :: Scientific/Engineering :: Mathematics',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Scientific/Engineering'
        ],
      packages=packages,
      keywords=['optimization'],
      namespace_packages=['coopr'],
      entry_points="""
        [console_scripts]
        test.coopr = coopr.misc.runtests:runCooprTests
        coopr = coopr.misc.coopr_main:main
        coopr_ns = coopr.misc.scripts:coopr_ns
        coopr_nsc = coopr.misc.scripts:coopr_nsc
        kill_pyro_mip_servers = coopr.misc.scripts:kill_pyro_mip_servers
        launch_pyro_mip_servers = coopr.misc.scripts:launch_pyro_mip_servers
        readsol = coopr.misc.scripts:readsol
        OSSolverService = coopr.misc.scripts:OSSolverService
        coopr_python = coopr.misc.scripts:coopr_python
        [coopr.command]
        coopr.cmd = coopr.misc.driver
      """
      )
