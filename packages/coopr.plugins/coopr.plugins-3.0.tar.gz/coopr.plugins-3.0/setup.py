#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

"""
Script to generate the installer for coopr.plugins.
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

scripts = glob.glob("scripts/*")

setup(name='coopr.plugins',
      version='3.0',
      maintainer='William E. Hart',
      maintainer_email='wehart@sandia.gov',
      url = 'https://software.sandia.gov/svn/public/coopr/coopr.plugins',
      license = 'BSD',
      platforms = ["any"],
      description = 'Plugins that are typically bundled with Coopr',
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
      scripts=scripts,
      namespace_packages=['coopr', 'coopr.plugins'],
      entry_points = {
        'coopr.opt': [
            'solvermanager.pyro = coopr.plugins.smanager.pyro',
            'converter.glpsol = coopr.plugins.converter.glpsol',
            'converter.pico = coopr.plugins.converter.pico',
            'converter.pyomo = coopr.plugins.converter.pyomo',
            'solver.cbc = coopr.plugins.solvers.CBCplugin',
            'solver.cplex = coopr.plugins.solvers.CPLEX',
            'solver.pico = coopr.plugins.solvers.PICO',
            'solver.glpk = coopr.plugins.solvers.GLPK',
            'solver.asl = coopr.plugins.solvers.ASL',
            'solver.gurobi = coopr.plugins.solvers.GUROBI',
            'solver.ps = coopr.plugins.solvers.ps',
            'testdriver.coopr.mip = coopr.plugins.testdriver.mip',
        ],
        'coopr.pyomo': [
            'testdriver.coopr.pyomo = coopr.plugins.testdriver.pyomo',
        ]
      }
      )
