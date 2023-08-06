#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

"""
Script to generate the installer for coopr.pysp.
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

setup(name='coopr.pysp',
      version='3.3',
      maintainer='Jean-Paul Watson',
      maintainer_email='jwatson@sandia.gov',
      url = 'https://software.sandia.gov/svn/public/coopr/coopr.pysp',
      license = 'BSD',
      platforms = ["any"],
      description = 'Coopr stochastic programming modeling and solver techniques',
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
      entry_points = """
        [console_scripts]
        runph=coopr.pysp.phinit:PH_main
        rundph=coopr.pysp.phinit:DualPH_main
        runef=coopr.pysp.ef_writer_script:main
        ph_test_client=coopr.pysp.ph_test_client:main
        phsolverserver=coopr.pysp.phsolverserver:main
        computeconf=coopr.pysp.computeconf:main
      """
      )
