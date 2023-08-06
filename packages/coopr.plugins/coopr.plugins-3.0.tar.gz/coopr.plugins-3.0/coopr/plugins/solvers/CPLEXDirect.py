#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2010 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


import os
import sys
import re
import string
import xml.dom.minidom
import time

from six import itervalues, iterkeys, iteritems, advance_iterator
from six.moves import xrange

_cplex_version = None
try:
    import cplex
    from cplex.exceptions import CplexError
    # create a version tuple of length 4
    _cplex_version = tuple(int(i) for i in cplex.Cplex().get_version().split('.'))
    while(len(_cplex_version) < 4):
        _cplex_version += (0,)
    _cplex_version = _cplex_version[:4]
    cplex_import_available=True
except ImportError:
    cplex_import_available=False

import pyutilib.services
import pyutilib.common
import pyutilib.component.core
from pyutilib.misc import Bunch, Options

from coopr.opt.base import *
from coopr.opt.base.solvers import _extract_version
from coopr.opt.results import *
from coopr.opt.solver import *
from coopr.pyomo.base import SymbolMap, NumericLabeler, Suffix
from coopr.pyomo.base.numvalue import value
from coopr.pyomo.base.block import active_subcomponents_generator, active_subcomponents_data_generator

try:
    unicode
except:
    basestring = str

class ModelSOS(object):
    def __init__(self):
        self.sosType = {}
        self.sosName = {}
        self.varnames = {}
        self.weights = {}
        self.block_cntr = 0

    def count_constraint(self,symbol_map,labeler,con,name,level,index=None):

        self.block_cntr += 1
        self.varnames[self.block_cntr] = []
        self.weights[self.block_cntr] = []
        if level == 1:
            self.sosType[self.block_cntr] = cplex.Cplex.SOS.type.SOS1
        elif level == 2:
            self.sosType[self.block_cntr] = cplex.Cplex.SOS.type.SOS2

        # The variable being indexed
        var = con.sos_vars()
        
        if index is None:
            tmpSet = con.sos_set()
            self.sosName[self.block_cntr] = name
        else:
            tmpSet = con.sos_set()[index]
            self.sosName[self.block_cntr] = name+str(index)

        # Get all the variables
        cntr = 1.0
        for idx in tmpSet:
            self.varnames[self.block_cntr].append(symbol_map.getSymbol(var[idx],labeler))
            # We need to weight each variable
            # For now we just increment a counter
            self.weights[self.block_cntr].append(cntr)
            cntr += 1.0


class CPLEXDirect(OptSolver):
    """The CPLEX LP/MIP solver
    """

    pyutilib.component.core.alias('_cplex_direct',  doc='Direct Python interface to the CPLEX LP/MIP solver')

    def __init__(self, **kwds):

        #
        # Call base class constructor
        #
        kwds['type'] = 'cplexdirect'
        OptSolver.__init__(self, **kwds)

        # NOTE: eventually both of the following attributes should be migrated to a common base class.
        # is the current solve warm-started? a transient data member to communicate state information
        # across the _presolve, _apply_solver, and _postsolve methods.
        self.warm_start_solve = False

        # the working problem instance, via CPLEX python constructs.
        self._active_cplex_instance = None

        # Note: Undefined capabilities default to 'None'
        self._capabilities = Options()
        self._capabilities.linear = True
        self._capabilities.quadratic_objective = True
        self._capabilities.quadratic_constraint = True
        self._capabilities.integer = True
        self._capabilities.sos1 = True
        self._capabilities.sos2 = True

    def available(self, exception_flag=True):
        """ True if the solver is available """

        if exception_flag is False:
            return cplex_import_available
        else:
            if cplex_import_available is False:
                raise ApplicationError("No CPLEX <-> Python bindings available - CPLEX direct solver functionality is not available")
            else:
                return True

    def version(self):
        if _cplex_version is None:
            return _extract_version('')
        return _cplex_version

    #
    # ultimately, this utility should go elsewhere - perhaps on the PyomoModel itself.
    # in the mean time, it is staying here.
    #
    def _hasIntegerVariables(self, instance):

        from coopr.pyomo.base import Var
        from coopr.pyomo.base.set_types import IntegerSet, BooleanSet

        for block in instance.all_blocks():
            for variable in active_subcomponents_generator(block,Var):
                if (isinstance(variable.domain, IntegerSet) is True) or (isinstance(variable.domain, BooleanSet) is True):
                    return True

        return False

    #
    # TBD
    #
    def _evaluate_bound(self, exp):

        from coopr.pyomo.base import expr

        if isinstance(exp, expr._IdentityExpression):
            return self._evaluate_bound(exp._args[0])
        elif exp.is_constant() or exp.is_fixed():
            return exp()
        else:
            raise ValueError("ERROR: nonconstant bound: " + str(exp))

    #
    # CPLEX requires objective expressions to be specified via something other than a sparse pair!
    # NOTE: The returned offset is guaranteed to be a float.
    #
    def _encode_constraint_body_linear(self, expression, labeler, as_pairs=False):

        variables = [] # string names of variables
        coefficients = [] # variable coefficients

        pairs = []

        hash_to_variable_map = expression[-1]

        for var_hash, var_coefficient in iteritems(expression[1]):

            variable_name = self._symbol_map.getSymbol(hash_to_variable_map[var_hash], labeler)

            if as_pairs is True:
                pairs.append((variable_name, var_coefficient))
            else:
                variables.append(variable_name)
                coefficients.append(var_coefficient)

        offset=0.0
        if 0 in expression:
            offset = expression[0][None]

        if as_pairs is True:
            return pairs, offset
        else:
            expr = cplex.SparsePair(ind=variables, val=coefficients)
            return expr, offset

    #
    # CPLEX requires objective expressions to be specified via something other than a sparse pair!
    # NOTE: The returned offset is guaranteed to be a float.
    # NOTE: This function is a variant of the above, specialized for LinearCanonicalRepn objects.
    #
    def _encode_constraint_body_linear_specialized(self, linear_repn, labeler, as_pairs=False):

        variables = [] # string names of variables
        coefficients = [] # variable coefficients

        pairs = []

        for i in xrange(0,len(linear_repn.linear)):

            var_coefficient = linear_repn.linear[i]
            var_value = linear_repn.variables[i]

            variable_name = self._symbol_map.getSymbol(var_value, labeler)

            if as_pairs is True:
                pairs.append((variable_name, var_coefficient))
            else:
                variables.append(variable_name)
                coefficients.append(var_coefficient)

        offset=0.0
        if linear_repn.constant != None:
            offset = linear_repn.constant

        if as_pairs is True:
            return pairs, offset
        else:
            expr = cplex.SparsePair(ind=variables, val=coefficients)
            return expr, offset

    #
    #Handle quadratic constraints and objectives
    #
    def _encode_constraint_body_quadratic(self, expression, labeler, as_triples=False, is_obj=1.0):

        variables1 = [] # string names of variables
        variables2 = [] # string names of variables
        coefficients = [] # variable coefficients

        triples = []

        hash_to_variable_map = expression[-1]

        for vrs, coeff in iteritems(expression[2]):

            if len(vrs)==2:
                variable_hash_iter = iterkeys(vrs)
                var1 = self._symbol_map.getSymbol(hash_to_variable_map[advance_iterator(variable_hash_iter)], labeler)
                var2 = self._symbol_map.getSymbol(hash_to_variable_map[advance_iterator(variable_hash_iter)], labeler)
            else:
                variable_hash_iter = iterkeys(vrs)
                var1 = var2  = self._symbol_map.getSymbol(hash_to_variable_map[advance_iterator(variable_hash_iter)], labeler)

            if as_triples is True:
                triples.append((var1, var2, is_obj*coeff))
            else:
                variables1.append(var1)
                variables2.append(var2)
                coefficients.append(coeff)

        if as_triples is True:
            return triples 
        else:
            expr = cplex.SparseTriple(ind1=variables1,ind2=variables2,val=coefficients)
            return expr


    #
    # method to populate the CPLEX problem instance (interface) from the supplied Pyomo problem instance.
    #
    def _populate_cplex_instance(self, pyomo_instance):

        labeler = NumericLabeler('x')
        self._symbol_map = SymbolMap(pyomo_instance)

        from coopr.pyomo.base import Var, Objective, Constraint, ConstraintList, IntegerSet, BooleanSet, SOSConstraint
        from coopr.pyomo.base.objective import minimize, maximize
        from coopr.pyomo.expr import canonical_is_constant
        from coopr.pyomo import LinearCanonicalRepn
    
        quadratic_constraints = False
        quadratic_objective = False
        used_sos_constraints = False
        cplex_instance = None
        try:
            cplex_instance = cplex.Cplex()
        except CplexError:
            print(sys.exc_info()[1])
            raise ValueError("TBD - FAILED TO CREATE CPLEX INSTANCE!")

        # cplex wants the caller to set the problem type, which is (for current
        # purposes) strictly based on variable type counts.
        num_binary_variables = 0
        num_integer_variables = 0
        num_continuous_variables = 0

        # transfer the variables from pyomo to cplex.
        var_names = []
        var_lbs = []
        var_ubs = []
        var_types = []

        for block in pyomo_instance.all_blocks():
            for var in active_subcomponents_data_generator(block,Var):
                if (not var.active) or var.fixed:
                    continue
                var_names.append(self._symbol_map.getSymbol( var, labeler ))
                if var.lb is None:
                    var_lbs.append(-cplex.infinity)
                else:
                    var_lbs.append(value(var.lb))
                if var.ub is None:
                    var_ubs.append(cplex.infinity)
                else:
                    var_ubs.append(value(var.ub))
                if isinstance(var.domain, IntegerSet):
                    var_types.append(cplex_instance.variables.type.integer)
                    num_integer_variables += 1
                elif isinstance(var.domain, BooleanSet):
                    var_types.append(cplex_instance.variables.type.binary)
                    num_binary_variables += 1
                else:
                    var_types.append(cplex_instance.variables.type.continuous)
                    num_continuous_variables += 1

        cplex_instance.variables.add(names=var_names, lb=var_lbs, ub=var_ubs, types=var_types)
        
        # transfer the constraints.
        expressions = []
        senses = []
        rhss = []
        range_values = []
        names = []

        qexpressions = []
        qlinears = []
        qsenses = []
        qrhss = []
        qnames = []

        for block in pyomo_instance.all_blocks():

            block_repn_suffix = block.subcomponent("repn")
            if (block_repn_suffix is None) or (not block_repn_suffix.type() is Suffix) or (not block_repn_suffix.active is True):
                block_repn_suffix = None

            for constraint in active_subcomponents_generator(block, Constraint):
                if constraint.trivial:
                    continue

                for con in itervalues(constraint): # TBD: more efficient looping here.
                    if not con.active:
                        continue

                    con_repn = None
                    if block_repn_suffix is not None:
                        con_repn = block_repn_suffix.getValue(con)

                    # There are conditions, e.g., when fixing variables, under which
                    # a constraint block might be empty.  Ignore these, for both
                    # practical reasons and the fact that the CPLEX LP format
                    # requires a variable in the constraint body.  It is also
                    # possible that the body of the constraint consists of only a
                    # constant, in which case the "variable" of
                    if isinstance(con_repn, LinearCanonicalRepn):
                        if con_repn.linear == None:
                           continue
                    else:
                       if canonical_is_constant(con_repn):
                           continue

                    name=self._symbol_map.getSymbol(con,labeler)
                    expr=None
                    qexpr=None

                    #Linear constraints
                    quadratic = False
                    if isinstance(con_repn, LinearCanonicalRepn):
                        expr, offset = self._encode_constraint_body_linear_specialized(con_repn, labeler)
                    elif 2 in con_repn:
                        quadratic=True
                    elif 1 in con_repn:
                        expr, offset = self._encode_constraint_body_linear(con_repn, labeler)

                    #Quadratic constraints
                    if quadratic is True:
                        if expr is None:
                            expr = cplex.SparsePair(ind=[0],val=[0.0])
                        quadratic_constraints = True

                        qexpr = self._encode_constraint_body_quadratic(con_repn,labeler)
                        qnames.append(name)

                        if con._equality:
                            # equality constraint.
                            qsenses.append('E')
                            bound_expr = con.lower
                            bound = self._evaluate_bound(bound_expr)
                            qrhss.append(bound)

                        elif con.lower is not None:
                            assert con.upper is not None
                            qsenses.append('G')
                            bound_expr = con.lower
                            bound = self._evaluate_bound(bound_expr)
                            qrhss.append(bound)

                        else:
                            qsenses.append('L')
                            bound_expr = con.upper
                            bound = self._evaluate_bound(bound_expr)
                            qrhss.append(bound)

                        qlinears.append(expr)
                        qexpressions.append(qexpr)

                    else:
                        names.append(name)
                        expressions.append(expr)

                        if con._equality:
                            # equality constraint.
                            senses.append('E')
                            bound_expr = con.lower
                            bound = self._evaluate_bound(bound_expr) - offset
                            rhss.append(bound)
                            range_values.append(0.0)

                        elif (con.lower is not None) and (con.upper is not None):
                            # ranged constraint.
                            senses.append('R')
                            lower_bound_expr = con.lower # TBD - watch the offset - why not subtract?
                            lower_bound = self._evaluate_bound(lower_bound_expr)
                            upper_bound_expr = con.upper # TBD - watch the offset - why not subtract?
                            upper_bound = self._evaluate_bound(upper_bound_expr)
                            rhss.append(lower_bound)
                            range_values.append(upper_bound-lower_bound)

                        elif con.lower is not None:
                            senses.append('G')
                            bound_expr = con.lower
                            bound = self._evaluate_bound(bound_expr) - offset
                            rhss.append(bound)
                            range_values.append(0.0)

                        else:
                            senses.append('L')
                            bound_expr = con.upper
                            bound = self._evaluate_bound(bound_expr) - offset
                            rhss.append(bound)
                            range_values.append(0.0)

        # SOS constraints - largely taken from cpxlp.py so updates there,
        # should be applied here
        # TODO: Allow users to specify the variables coefficients for custom
        # branching/set orders - refer to cpxlp.py
        sosn = self._capabilities.sosn
        sos1 = self._capabilities.sos1
        sos2 = self._capabilities.sos2
        modelSOS = ModelSOS()
        for block in pyomo_instance.all_blocks():
            for con in active_subcomponents_generator(block,SOSConstraint):
                level = con.sos_level()
                if (level == 1 and not sos1) or (level == 2 and not sos2) or (level > 2 and not sosn):
                    raise Exception("Solver does not support SOS level %s constraints" % (level,))
                name = self._symbol_map.getSymbol( con, labeler ) 
                masterIndex = con.sos_set_set()
                if None in masterIndex:
                    # A single constraint
                    modelSOS.count_constraint(self._symbol_map,labeler,con, name, level)
                else:
                    # A series of indexed constraints
                    for index in masterIndex:
                        modelSOS.count_constraint(self._symbol_map,labeler,con, name, level, index)

        if modelSOS.sosType:
            for key in modelSOS.sosType:
                cplex_instance.SOS.add(type = modelSOS.sosType[key], \
                                       name = modelSOS.sosName[key], \
                                       SOS = [modelSOS.varnames[key], modelSOS.weights[key]] )
            used_sos_constraints = True

        cplex_instance.linear_constraints.add(lin_expr=expressions, senses=senses, rhs=rhss, range_values=range_values, names=names)

        for index in xrange(len(qexpressions)):
            cplex_instance.quadratic_constraints.add(lin_expr=qlinears[index], quad_expr=qexpressions[index], sense=qsenses[index], rhs=qrhss[index], name=qnames[index])
        
        model_repn_suffix = pyomo_instance.subcomponent("repn")
        if (model_repn_suffix is None) or (not model_repn_suffix.type() is Suffix) or (not model_repn_suffix.active is True):
            raise ValueError("Unable to find an active Suffix with name 'repn' on block: %s" % (pyomo_instance.cname(True)))

        # transfer the objective.
        for obj_data in active_subcomponents_data_generator(pyomo_instance,Objective):
            if obj_data.is_minimizing():
                cplex_instance.objective.set_sense(cplex_instance.objective.sense.minimize)
            else:
                cplex_instance.objective.set_sense(cplex_instance.objective.sense.maximize)

            cplex_instance.objective.set_name(obj_data.cname(True))

            self._symbol_map.getSymbol(obj_data, labeler)
            self._symbol_map.alias(obj_data,'__default_objective__')

            obj_repn = model_repn_suffix.getValue(obj_data)

            if (isinstance(obj_repn, LinearCanonicalRepn) and (obj_repn.linear == None)) or canonical_is_constant(obj_repn):
                print("Warning: Constant objective detected, replacing " + \
                          "with a placeholder to prevent solver failure.")

                cplex_instance.variables.add(lb=[1],ub=[1],names=["ONE_VAR_CONSTANT"])
                objective_expression = [("ONE_VAR_CONSTANT",offset)]
                cplex_instance.objective.set_linear(objective_expression)
                
            else:

                if isinstance(obj_repn, LinearCanonicalRepn):
                    objective_expression, offset = self._encode_constraint_body_linear_specialized(obj_repn, labeler, as_pairs=True) # how to deal with indexed objectives?
                    if offset != 0:
                        cplex_instance.variables.add(lb=[1],ub=[1],names=["ONE_VAR_CONSTANT"])
                        objective_expression.append(("ONE_VAR_CONSTANT",offset))
                    cplex_instance.objective.set_linear(objective_expression)
                else:
                    #Linear terms
                    if 1 in obj_repn:
                        objective_expression, offset = self._encode_constraint_body_linear(obj_repn, labeler, as_pairs=True) # how to deal with indexed objectives?
                        if offset != 0:
                            cplex_instance.variables.add(lb=[1],ub=[1],names=["ONE_VAR_CONSTANT"])
                            objective_expression.append(("ONE_VAR_CONSTANT",offset))
                        cplex_instance.objective.set_linear(objective_expression)

                    #Quadratic terms 
                    if 2 in obj_repn:
                        quadratic_objective = True
                        objective_expression = self._encode_constraint_body_quadratic(obj_repn, labeler, as_triples=True, is_obj=2.0) # how to deal with indexed objectives?
                        cplex_instance.objective.set_quadratic_coefficients(objective_expression)

        # set the problem type based on the variable counts.
        if (quadratic_objective is True) or (quadratic_constraints is True):
            if (num_integer_variables > 0) or (num_binary_variables > 0) or (used_sos_constraints):
                if quadratic_constraints is True:
                    cplex_instance.set_problem_type(cplex_instance.problem_type.MIQCP)
                else:
                    cplex_instance.set_problem_type(cplex_instance.problem_type.MIQP)
            else:
                if quadratic_constraints is True:
                    cplex_instance.set_problem_type(cplex_instance.problem_type.QCP)
                else:
                    cplex_instance.set_problem_type(cplex_instance.problem_type.QP)
        elif (num_integer_variables > 0) or (num_binary_variables > 0) or (used_sos_constraints):
            cplex_instance.set_problem_type(cplex_instance.problem_type.MILP)
        else:
            cplex_instance.set_problem_type(cplex_instance.problem_type.LP)

        self._active_cplex_instance = cplex_instance

    #
    # cplex has a simple, easy-to-use warm-start capability.
    #
    def warm_start_capable(self):

        return True

    #
    # write a warm-start file in the CPLEX MST format.
    #
    def warm_start(self, instance):

        def _error_labeler(obj):
            raise KeyError(
                "CPLEX Warm Start Error: instance contains an object, %s, "
                "that is not found in the symbol map.  Does the instance "
                "match the provided symbol map?" % ( obj.cname(True), ))

        from coopr.pyomo.base import Var

        labeler = NumericLabeler()
        # the iteration order is identical to that used in generating
        # the cplex instance, so all should be well.
        variable_names = []
        variable_values = []
        for var in active_subcomponents_data_generator(Var):
            if (var.stale is True) or (var.fixed is True):
                continue
            name = self._symbol_map.getSymbol(var, _error_labeler)
            variable_names.append(name)
            variable_values.append(var.value)

        self._active_cplex_instance.MIP_starts.add([variable_names, variable_values],
                                                   self._active_cplex_instance.MIP_starts.effort_level.auto)


    # over-ride presolve to extract the warm-start keyword, if specified.
    def _presolve(self, *args, **kwds):
        from coopr.pyomo.base.PyomoModel import Model

        self.suffixes = kwds.pop( 'suffixes', self.suffixes )
        self.tee = kwds.pop( 'tee', False )
        self.keepfiles = kwds.pop( 'keepfiles', False )
        self.warm_start_solve = kwds.pop( 'warmstart', False )

        # Step 1: extract the pyomo instance from the input arguments,
        #         cache it, and create the corresponding (as of now empty)
        #         CPLEX problem instance.
        if len(args) != 1:
            msg = "The CPLEXDirect plugin method '_presolve' must be supplied "\
                  "a single problem instance - %s were supplied"
            raise ValueError(msg % len(args))

        model = args[ 0 ]
        if not isinstance(model, Model):
            msg = "The problem instance supplied to the CPLEXDirect plugin " \
                  "method '_presolve' must be of type 'Model' - "\
                  "interface does not currently support file names"
            raise ValueError(msg)

        # TBD-document.
        self._populate_cplex_instance(model)

        if 'write' in self.options:
            fname = self.options.write
            self._active_cplex_instance.write(fname)
        
        # Handle other keywords

        # if the first argument is a string (representing a filename),
        # then we don't have an instance => the solver is being applied
        # to a file.

        # FIXME: This appears to be a bogus test: we raise an exception
        # above if len(args) != 1 or type(args[0]) != Model
        if (len(args) > 0) and not isinstance(model,basestring):

            # write the warm-start file - currently only supports MIPs.
            # we only know how to deal with a single problem instance.
            if self.warm_start_solve is True:

                if len(args) != 1:
                    msg = "CPLEX _presolve method can only handle a single " \
                          "problem instance - %s were supplied"
                    raise ValueError(msg % len(args))

                if self._hasIntegerVariables(model) is True:
                    start_time = time.time()
                    self.warm_start(model)
                    end_time = time.time()
                    if self._report_timing is True:
                        print("Warm start write time=%.2f seconds" % (end_time-start_time))

    #
    # TBD
    #
    def _apply_solver(self):

        # set up all user-specified parameters.
        if (self.options.mipgap is not None) and (self.options.mipgap > 0.0):
            self._active_cplex_instance.parameters.mip.tolerances.mipgap.set(self.options.mipgap)

        for key in self.options:
            if key == 'relax_integrality' or key == 'mipgap' or key == 'write':
                continue
            else:
                opt_cmd = self._active_cplex_instance.parameters
                key_pieces = key.split('_')
                for key_piece in key_pieces:
                    opt_cmd = getattr(opt_cmd,key_piece)
                opt_cmd.set(self.options[key])
                
        if 'relax_integrality' in self.options:
            self._active_cplex_instance.set_problem_type(self._active_cplex_instance.problem_type.LP)
        
        # and kick off the solve.
        if self.tee == True:
            #Should this use pyutilib's tee_io? I couldn't find where
            #other solvers set output using tee=True/False
            from sys import stdout
            self._active_cplex_instance.set_results_stream(stdout)
        elif self.keepfiles == True:
            log_file = pyutilib.services.TempfileManager.create_tempfile(suffix = '.cplex.log')
            print("Solver log file: " + log_file)
            self._active_cplex_instance.set_results_stream(log_file)
            #Not sure why the following doesn't work. As a result, it's either stream output
            #or write a logfile, but not both.
            #self._active_cplex_instance.set_log_stream(log_file)
        else:
            self._active_cplex_instance.set_results_stream(None)
        self._active_cplex_instance.solve()

        # FIXME: can we get a return code indicating if CPLEX had a
        # significant failure?
        return Bunch(rc=None, log=None)

    def _postsolve(self):

        # the only suffixes that we extract from CPLEX are
        # constraint duals, constraint slacks, and variable
        # reduced-costs. scan through the solver suffix list
        # and throw an exception if the user has specified
        # any others.
        extract_duals = False
        extract_slacks = False
        extract_reduced_costs = False
        for suffix in self.suffixes:
            flag=False
            if re.match(suffix,"dual"):
                extract_duals = True
                flag=True
            if re.match(suffix,"slack"):
                extract_slacks = True
                flag=True
            if re.match(suffix,"rc"):
                extract_reduced_costs = True
                flag=True
            if not flag:
                raise RuntimeError("***The CPLEXDirect solver plugin cannot extract solution suffix="+suffix)


        instance = self._active_cplex_instance


        if instance.get_problem_type() in [instance.problem_type.MILP,
                                           instance.problem_type.MIQP,
                                           instance.problem_type.MIQCP]:
            extract_reduced_costs = False
            extract_duals = False

        # Remove variables whose absolute value is smaller than CPLEX's epsilon from the results data
        #instance.cleanup()

        results = SolverResults()
        results.problem.name = instance.get_problem_name()
        results.problem.lower_bound = None #instance.solution.
        results.problem.upper_bound = None
        results.problem.number_of_variables = instance.variables.get_num()
        results.problem.number_of_constraints = instance.linear_constraints.get_num() \
                                                + instance.quadratic_constraints.get_num() \
                                                + instance.indicator_constraints.get_num() \
                                                + instance.SOS.get_num()
        results.problem.number_of_nonzeros = None
        results.problem.number_of_binary_variables = instance.variables.get_num_binary()
        results.problem.number_of_integer_variables = instance.variables.get_num_integer()
        results.problem.number_of_continuous_variables = instance.variables.get_num() \
                                                            - instance.variables.get_num_binary() \
                                                            - instance.variables.get_num_integer() \
                                                            - instance.variables.get_num_semiinteger()
                                                            #TODO: Does this double-count semi-integers?
                                                            #Should we also remove semi-continuous?
        results.problem.number_of_objectives = 1

        results.solver.name = "CPLEX "+instance.get_version()
#        results.solver.status = None
        results.solver.return_code = None
        results.solver.message = None
        results.solver.user_time = None
        results.solver.system_time = None
        results.solver.wallclock_time = None
        results.solver.termination_message = None
        
        soln = Solution()

        #Get solution status -- for now, if CPLEX returns anything we don't recognize, mark as an error
        soln_status = instance.solution.get_status()
        if soln_status in [1, 101, 102]:
            results.solver.termination_condition = TerminationCondition.optimal
            soln.status = SolutionStatus.optimal
        elif soln_status in [2, 4, 118, 119]:
            # Note: soln_status of 4 means infeasible or unbounded
            #       and 119 means MIP infeasible or unbounded
            results.solver.termination_condition = TerminationCondition.unbounded
            soln.status = SolutionStatus.unbounded
        elif soln_status in [3, 103]:
            results.solver.termination_condition = TerminationCondition.infeasible
            soln.status = SolutionStatus.infeasible
        else:
            soln.status = SolutionStatus.error

        #Only try to get objective and variable values if a solution exists
        soln_type = instance.solution.get_solution_type()
        if soln_type > 0:
            soln.objective['__default_objective__'].value = instance.solution.get_objective_value()
            num_variables = instance.variables.get_num()
            variable_names = instance.variables.get_names()
            variable_values = instance.solution.get_values()
            for i in xrange(num_variables):
                variable_name = variable_names[i]
                soln.variable[variable_name] = {"Value" : variable_values[i], "Id" : len(soln.variable)}

            if extract_reduced_costs:
                # get variable reduced costs
                rc_values = instance.solution.get_reduced_costs()
                for i in xrange(num_variables):
                    soln.variable[variable_names[i]]["Rc"] = rc_values[i]

            if extract_duals:
                # get duals (linear constraints only)
                num_linear_constraints = instance.linear_constraints.get_num()
                constraint_names = instance.linear_constraints.get_names()
                dual_values = instance.solution.get_dual_values() 
                for i in xrange(num_linear_constraints):
                    soln.constraint[constraint_names[i]].dual = dual_values[i]

                # CPLEX PYTHON API DOES NOT SUPPORT QUADRATIC DUAL COLLECTION

            if extract_slacks:
                # get linear slacks
                num_linear_constraints = instance.linear_constraints.get_num()
                constraint_names = instance.linear_constraints.get_names()
                slack_values = instance.solution.get_linear_slacks() 
                for i in xrange(num_linear_constraints):
                    # if both U and L exist (i.e., a range constraint) then 
                    # R_ = U-L
                    R_ = instance.linear_constraints.get_range_values(i)
                    if R_ == 0.0:
                        soln.constraint[constraint_names[i]].slack = slack_values[i]
                    else:
                        # This is a range constraint for which cplex always returns the
                        # value of f(x)-L. In the spirit of conforming with the other writer,
                        # I will return the max (in absolute value) of L-f(x) and U-f(x)
                        Ls_ = slack_values[i]
                        Us_ = R_ - slack_values[i]
                        if Us_ > Ls_:
                            soln.constraint[constraint_names[i]].slack = Us_
                        else:
                            soln.constraint[constraint_names[i]].slack = -Ls_
                
                # get quadratic slacks
                num_quadratic_constraints = instance.quadratic_constraints.get_num()
                constraint_names = instance.quadratic_constraints.get_names()
                slack_values = instance.solution.get_quadratic_slacks() 
                for i in xrange(num_quadratic_constraints):
                    # if both U and L exist (i.e., a range constraint) then 
                    # R_ = U-L
                    soln.constraint[constraint_names[i]].slack = slack_values[i]

            results.solution.insert(soln)

        self.results = results

        # don't know if any of this is necessary!

        # take care of the annoying (and empty) CPLEX temporary files in
        # the current directory.  this approach doesn't seem overly
        # efficient, but python os module functions don't accept regular
        # expression directly.
        filename_list = os.listdir(".")
        clone_re = re.compile('clone\d+\.log')
        for filename in filename_list:
            # CPLEX temporary files come in two flavors - cplex.log and
            # clone*.log.  the latter is the case for multi-processor
            # environments.
            #
            # IMPT: trap the possible exception raised by the file not existing.
            #       this can occur in pyro environments where > 1 workers are
            #       running CPLEX, and were started from the same directory.
            #       these logs don't matter anyway (we redirect everything),
            #       and are largely an annoyance.
            try:
                if filename == 'cplex.log':
                    os.remove(filename)
                elif clone_re.match(filename):
                    os.remove(filename)
            except OSError:
                pass

        # let the base class deal with returning results.
        return OptSolver._postsolve(self)


if cplex_import_available is False:
    SolverFactory().deactivate('_cplex_direct')
    SolverFactory().deactivate('_mock_cplexdirect')
