#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import pyutilib.component.core
pyutilib.component.core.PluginGlobals.push_env( 'coopr.opt' )

from coopr.plugins.solvers.ps import PatternSearch
from coopr.plugins.solvers.PICO import PICO, MockPICO
from coopr.plugins.solvers.CBCplugin import CBC, MockCBC, configure_cbc
from coopr.plugins.solvers.GLPK import GLPK, configure_glpk
import coopr.plugins.solvers.GLPK_old
from coopr.plugins.solvers.glpk_direct import GLPKDirect
from coopr.plugins.solvers.CPLEX import CPLEX, MockCPLEX
from coopr.plugins.solvers.CPLEXDirect import CPLEXDirect
from coopr.plugins.solvers.GUROBI import GUROBI
from coopr.plugins.solvers.gurobi_direct import gurobi_direct
from coopr.plugins.solvers.ASL import ASL, MockASL
from coopr.plugins.solvers.SCIPAMPL import SCIPAMPL
from coopr.plugins.solvers.XPRESS import XPRESS, MockXPRESS

#
# Interrogate the CBC executable to see if it recognizes the -AMPL flag
#
configure_cbc()

#
# Interrogate the glpsol executable to see if it is new enough to allow the new parser logic
#
configure_glpk()

pyutilib.component.core.PluginGlobals.pop_env()
