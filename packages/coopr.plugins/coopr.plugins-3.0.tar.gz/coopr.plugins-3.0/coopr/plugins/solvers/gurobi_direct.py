#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2010 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import logging
import re
import itertools

from six import itervalues, iteritems, advance_iterator

_gurobi_version = None
try:
    # import all the glp_* functions
    from gurobipy import *
    # create a version tuple of length 4
    _gurobi_version = gurobi.version()
    while(len(_gurobi_version) < 4):
        _gurobi_version += (0,)
    _gurobi_version = _gurobi_version[:4]
    _GUROBI_VERSION_MAJOR = _gurobi_version[0]
    gurobi_python_api_exists = True
except ImportError:
    gurobi_python_api_exists = False

from pyutilib.misc import Bunch, Options
from pyutilib.component.core import alias
from pyutilib.services import TempfileManager

from coopr.opt.base import *
from coopr.opt.base.solvers import _extract_version
from coopr.opt.results import *
from coopr.opt.solver import *
from coopr.pyomo.base import SymbolMap, NumericLabeler, Suffix
from coopr.pyomo.base.numvalue import value
from coopr.pyomo.base.block import active_subcomponents_generator, active_subcomponents_data_generator

logger = logging.getLogger('coopr.plugins')

GRB_MAX = -1
GRB_MIN = 1

class ModelSOS(object):
    def __init__(self):
        self.sosType = {}
        self.sosName = {}
        self.varnames = {}
        self.weights = {}
        self.block_cntr = 0

    def count_constraint(self,symbol_map,labeler,gurobi_var_map,con,name,level,index=None):

        self.block_cntr += 1
        self.varnames[self.block_cntr] = []
        self.weights[self.block_cntr] = []
        if level == 1:
            self.sosType[self.block_cntr] = GRB.SOS_TYPE1
        elif level == 2:
            self.sosType[self.block_cntr] = GRB.SOS_TYPE2

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
            self.varnames[self.block_cntr].append(gurobi_var_map[symbol_map.getSymbol(var[idx],labeler)])
            # We need to weight each variable
            # For now we just increment a counter
            self.weights[self.block_cntr].append(cntr)
            cntr += 1.0

class gurobi_direct ( OptSolver ):
    """The Gurobi optimization solver (direct API plugin)

 The gurobi_direct plugin offers an API interface to Gurobi.  It requires the
 Python Gurobi API interface (gurobipy) be in Coopr's lib/ directory.  Generally, if you can run Coopr's Python instance, and execute

 >>> import gurobipy
 >>>

 with no errors, then this plugin will be enabled.

 Because of the direct connection with the Gurobi, no temporary files need be
 written or read.  That ostensibly makes this a faster plugin than the file-based
 Gurobi plugin.  However, you will likely not notice any speed up unless you are
 using the GLPK solver with PySP problems (due to the rapid re-solves).

 One downside to the lack of temporary files, is that there is no LP file to
 inspect for clues while debugging a model.  For that, use the 'write' solver
 option:

 $ pyomo model.{py,dat} \
   --solver=gurobi_direct \
   --solver-options  write=/path/to/some/file.lp

 This is a direct interface to Gurobi's Model.write function, the extension of the file is important.  You could, for example, write the file in MPS format:

 $ pyomo model.{py,dat} \
   --solver=gurobi_direct \
   --solver-options  write=/path/to/some/file.mps

    """

    alias('_gurobi_direct', doc='Direct Python interface to the Gurobi optimization solver.')

    def __init__(self, **kwds):
        #
        # Call base class constructor
        #
        kwds['type'] = 'gurobi_direct'
        OptSolver.__init__(self, **kwds)

        self._model = None

        # NOTE: eventually both of the following attributes should be migrated
        # to a common base class.  Is the current solve warm-started?  A
        # transient data member to communicate state information across the
        # _presolve, _apply_solver, and _postsolve methods.
        self.warm_start_solve = False

        # Note: Undefined capabilities default to 'None'
        self._capabilities = Options()
        self._capabilities.linear = True
        self._capabilities.quadratic_objective = True
        self._capabilities.quadratic_constraint = True
        self._capabilities.integer = True
        self._capabilities.sos1 = True
        self._capabilities.sos2 = True

    def version(self):
        if _gurobi_version is None:
            return _extract_version('')
        return _gurobi_version

    def available(self, exception_flag=True):
        """ True if the solver is available """

        if exception_flag is False:
            return gurobi_python_api_exists
        else:
            if gurobi_python_api_exists is False:
                raise pyutilib.common.ApplicationError("No Gurobi <-> Python bindings available - Gurobi direct solver functionality is not available")
            else:
                return True        

    def _populate_gurobi_instance ( self, model ):

        from coopr.pyomo.base import Var, Objective, Constraint, ConstraintList, IntegerSet, BooleanSet, SOSConstraint
        from coopr.pyomo.expr import canonical_is_constant
        from coopr.pyomo import LinearCanonicalRepn

        try:
            grbmodel = Model( name=model.name )
        except Exception:
            e = sys.exc_info()[1]
            msg = 'Unable to create Gurobi model.  Have you installed the Python'\
            '\n       bindings for Gurobi?\n\n\tError message: %s'
            raise Exception(msg % e)

        labeler = NumericLabeler('x')
        self._symbol_map = SymbolMap(model)

        pyomo_gurobi_variable_map = {} # maps labels to the corresponding Gurobi variable object
        
        for block in model.all_blocks():
            for var_value in active_subcomponents_data_generator(block,Var):
                if (not var_value.active) or (var_value.fixed is True):
                    continue
    
                lb = -GRB.INFINITY
                ub = GRB.INFINITY
    
                if var_value.lb is not None:
                    lb = value(var_value.lb)
                if var_value.ub is not None:
                    ub = value(var_value.ub)
    
                var_value_label = self._symbol_map.getSymbol(var_value, labeler)
                
                # be sure to impart the integer and binary nature of any variables
                if isinstance(var_value.domain, IntegerSet):
                    var_type = GRB.INTEGER
                elif isinstance(var_value.domain, BooleanSet):
                    var_type = GRB.BINARY
                else:
                    var_type = GRB.CONTINUOUS
    
                pyomo_gurobi_variable_map[var_value_label] = grbmodel.addVar(lb=lb, \
                                                                             ub=ub, \
                                                                             vtype=var_type, \
                                                                             name=var_value_label)

        grbmodel.update() 

        model_repn_suffix = model.subcomponent("repn")
        if (model_repn_suffix is None) or (not model_repn_suffix.type() is Suffix) or (not model_repn_suffix.active is True):
            raise ValueError("Unable to find an active Suffix with name 'repn' on block: %s" % (model.cname(True)))

        for obj_data in active_subcomponents_data_generator(model,Objective):
            sense = GRB_MAX
            if obj_data.is_minimizing(): sense = GRB_MIN
            grbmodel.ModelSense = sense
            obj_expr = LinExpr()

            obj_repn = model_repn_suffix.getValue(obj_data)

            if (isinstance(obj_repn, LinearCanonicalRepn) and (obj_repn.linear == None)) or canonical_is_constant(obj_repn):
                msg = "Ignoring objective '%s[%s]' which is constant"
                logger.warning( msg % (str(objective), str(key)) )
                continue

            if isinstance(obj_repn, LinearCanonicalRepn):

                if obj_repn.constant != None:
                    obj_expr.addConstant(obj_repn.constant)

                if obj_repn.linear != None:

                    for i in xrange(len(obj_repn.linear)):
                        var_coefficient = obj_repn.linear[i]
                        var_value = obj_repn.variables[i]                    

                        label = self._symbol_map.getSymbol(var_value, labeler)
                        obj_expr.addTerms(var_coefficient, pyomo_gurobi_variable_map[label])
                        # the coefficients are attached to the model when creating the
                        # variables, below

            else:

                if 0 in obj_repn: # constant term
                    obj_expr.addConstant(obj_repn[0][None])

                if 1 in obj_repn: # first-order terms
                    hash_to_variable_map = obj_repn[-1]
                    for var_hash, var_coefficient in iteritems(obj_repn[1]):
                        label = self._symbol_map.getSymbol(hash_to_variable_map[var_hash], labeler)
                        obj_expr.addTerms(var_coefficient, pyomo_gurobi_variable_map[label])
                        # the coefficients are attached to the model when creating the
                        # variables, below

                if 2 in obj_repn:
                    obj_expr = QuadExpr(obj_expr)
                    hash_to_variable_map = obj_repn[-1]
                    for quad_repn, coef in iteritems(obj_repn[2]):
                        gurobi_expr = QuadExpr(coef)
                        for var_hash, exponent in iteritems(quad_repn):
                            gurobi_var = pyomo_gurobi_variable_map[self._symbol_map.getSymbol(hash_to_variable_map[var_hash], labeler)]
                            gurobi_expr *= gurobi_var 
                            if exponent == 2:
                                gurobi_expr *= gurobi_var
                        obj_expr += gurobi_expr
            # need to cache the objective label, because the GUROBI python interface doesn't track this.
            self._objective_label = self._symbol_map.getSymbol(obj_data, labeler)

        grbmodel.setObjective(obj_expr,sense=sense)       
 
        # SOS constraints - largely taken from cpxlp.py so updates there,
        # should be applied here
        # TODO: Allow users to specify the variables coefficients for custom
        # branching/set orders - refer to cpxlp.py
        sos1 = self._capabilities.sos1
        sos2 = self._capabilities.sos2
        
        modelSOS = ModelSOS()
        for block in model.all_blocks():
            for con in active_subcomponents_generator(block,SOSConstraint):
                level = con.sos_level()
                if (level == 1 and not sos1) or (level == 2 and not sos2) or (level > 2):
                    raise Exception("Solver does not support SOS level %s constraints" % (level,))
                name = self._symbol_map.getSymbol( con, labeler )
                masterIndex = con.sos_set_set()
                if None in masterIndex:
                    # A single constraint
                    modelSOS.count_constraint(self._symbol_map,labeler,pyomo_gurobi_variable_map,con, name, level)
                else:
                    # A series of indexed constraints
                    for index in masterIndex:
                        modelSOS.count_constraint(self._symbol_map,labeler,pyomo_gurobi_variable_map,con, name, level, index)
        
        if modelSOS.sosType:
            for key in modelSOS.sosType:
                grbmodel.addSOS(modelSOS.sosType[key], \
                                modelSOS.varnames[key], \
                                modelSOS.weights[key] )
        
        grbmodel.update()

        # Track the range constraints and there associated variables added by gurobi
        self._last_native_var_idx = grbmodel.NumVars-1
        range_var_idx = grbmodel.NumVars
        _self_range_con_var_pairs = self._range_con_var_pairs = []

        for block in model.all_blocks():
            
            block_repn_suffix = block.subcomponent("repn")
            if (block_repn_suffix is None) or (not block_repn_suffix.type() is Suffix) or (not block_repn_suffix.active is True):
                block_repn_suffix = None

            for constraint in active_subcomponents_generator(block,Constraint):
                if constraint.trivial: 
                    continue
    
                for constraint_data in itervalues(constraint):
    
                    if not constraint_data.active: 
                        continue
                    elif constraint_data.lower is None and constraint_data.upper is None:
                        continue  # not binding at all, don't bother
    
                    con_repn = None
                    if block_repn_suffix is not None:
                        con_repn = block_repn_suffix.getValue(constraint_data)

                    offset = 0.0
                    constraint_label = self._symbol_map.getSymbol(constraint_data, labeler)

                    if isinstance(con_repn, LinearCanonicalRepn):

                        if con_repn.constant != None:
                            offset = con_repn.constant
                        expr = LinExpr() + offset

                        if con_repn.linear != None:
    
                            linear_coefs = list()
                            linear_vars = list()

                            for i in xrange(len(con_repn.linear)):

                                var_coefficient = con_repn.linear[i]
                                var_value = con_repn.variables[i]
    
                                label = self._symbol_map.getSymbol(var_value, labeler)
                                linear_coefs.append( var_coefficient )
                                linear_vars.append( pyomo_gurobi_variable_map[label] )
    
                            expr += LinExpr(linear_coefs, linear_vars)

                    else:                        

                        if 0 in con_repn:
                            offset = con_repn[0][None]
                        expr = LinExpr() + offset

                        if 1 in con_repn: # first-order terms
    
                            linear_coefs = list()
                            linear_vars = list()
    
                            hash_to_variable_map = con_repn[-1]
                            for var_hash, var_coefficient in iteritems(con_repn[1]):
                                var = hash_to_variable_map[var_hash]
                                label = self._symbol_map.getSymbol(var, labeler)
                                linear_coefs.append( var_coefficient )
                                linear_vars.append( pyomo_gurobi_variable_map[label] )
    
                            expr += LinExpr(linear_coefs, linear_vars)

                        if 2 in con_repn: # quadratic constraint
                            if _GUROBI_VERSION_MAJOR < 5:
                                raise ValueError("The gurobi_direct plugin does not handle quadratic constraint expressions\
                            \nfor Gurobi major versions < 5. Current version: Gurobi %s.%s%s" % gurobi.version())
                            expr = QuadExpr(expr)
                            hash_to_variable_map = con_repn[-1]
                            for quad_repn, coef in iteritems(con_repn[2]):
                                gurobi_expr = QuadExpr(coef)
                                for var_hash, exponent in iteritems(quad_repn):
                                    gurobi_var = pyomo_gurobi_variable_map[self._symbol_map.getSymbol(hash_to_variable_map[var_hash], labeler)]
                                    gurobi_expr *= gurobi_var 
                                    if exponent == 2:
                                        gurobi_expr *= gurobi_var
                                expr += gurobi_expr

                    if constraint_data._equality:
                        sense = GRB.EQUAL    # Fixed
                        bound = constraint_data.lower()
                        grbmodel.addConstr(
                            lhs=expr, sense=sense, rhs=bound, name=constraint_label )
                    else:
                        # L <= body <= U
                        if (constraint_data.upper is not None) and (constraint_data.lower is not None):
                            grb_con = grbmodel.addRange(expr, constraint_data.lower(), constraint_data.upper(), constraint_label)
                            _self_range_con_var_pairs.append((grb_con,range_var_idx))
                            range_var_idx += 1
                        # body <= U
                        elif constraint_data.upper is not None:
                            bound = constraint_data.upper()
                            if bound < float('inf'):
                                grbmodel.addConstr(
                                    lhs=expr,
                                    sense=GRB.LESS_EQUAL,
                                    rhs=bound,
                                    name=constraint_label
                                    )
                        # L <= body            
                        else:
                            bound = constraint_data.lower()
                            if bound > -float('inf'):
                                grbmodel.addConstr(
                                    lhs=expr,
                                    sense=GRB.GREATER_EQUAL,
                                    rhs=bound,
                                    name=constraint_label
                                    )
         
        grbmodel.update()

        self._gurobi_instance = grbmodel

    def warm_start_capable(self):
        msg = "Gurobi has the ability to use warmstart solutions.  However, it "\
              "has not yet been implemented into the Coopr gurobi_direct plugin."
        logger.info( msg )
        return False


    def warm_start(self, instance):
        pass


    def _presolve(self, *args, **kwargs):
        from coopr.pyomo.base.PyomoModel import Model

        self.suffixes = kwargs.pop( 'suffixes', self.suffixes )
        self.warm_start_solve = kwargs.pop( 'warmstart', False )
        self.keepfiles = kwargs.pop( 'keepfiles' , False )
        self.tee = kwargs.pop( 'tee', False )

        model = args[0]
        if len(args) != 1:
            msg = "The gurobi_direct plugin method '_presolve' must be supplied "\
                  "a single problem instance - %s were supplied"
            raise ValueError(msg % len(args))
        elif not isinstance(model, Model):
            raise ValueError("The problem instance supplied to the "            \
                 "gurobi_direct plugin '_presolve' method must be of type 'Model'")

        self._populate_gurobi_instance( model )
        grbmodel = self._gurobi_instance

        if 'write' in self.options:
            fname = self.options.write
            grbmodel.write( fname )

        # Scaffolding in place
        if self.warm_start_solve is True:

            if len(args) != 1:
                msg = "The gurobi_direct _presolve method can only handle a single"\
                      "problem instance - %s were supplied"
                raise ValueError(msg % len(args))

            self.warm_start( model )


    def _apply_solver(self):
        # TODO apply appropriate user-specified parameters

        prob = self._gurobi_instance

        if self.tee:
            prob.setParam( 'OutputFlag', self.tee )
        else:
            prob.setParam( 'OutputFlag', 0)
        
        if self.keepfiles == True:
            log_file = TempfileManager.create_tempfile(suffix = '.gurobi.log')
            print("Solver log file: " + log_file)
            prob.setParam('LogFile', log_file)

        #Options accepted by gurobi (case insensitive):
        #['Cutoff', 'IterationLimit', 'NodeLimit', 'SolutionLimit', 'TimeLimit',
        # 'FeasibilityTol', 'IntFeasTol', 'MarkowitzTol', 'MIPGap', 'MIPGapAbs',
        # 'OptimalityTol', 'PSDTol', 'Method', 'PerturbValue', 'ObjScale', 'ScaleFlag',
        # 'SimplexPricing', 'Quad', 'NormAdjust', 'BarIterLimit', 'BarConvTol',
        # 'BarCorrectors', 'BarOrder', 'Crossover', 'CrossoverBasis', 'BranchDir',
        # 'Heuristics', 'MinRelNodes', 'MIPFocus', 'NodefileStart', 'NodefileDir',
        # 'NodeMethod', 'PumpPasses', 'RINS', 'SolutionNumber', 'SubMIPNodes', 'Symmetry',
        # 'VarBranch', 'Cuts', 'CutPasses', 'CliqueCuts', 'CoverCuts', 'CutAggPasses',
        # 'FlowCoverCuts', 'FlowPathCuts', 'GomoryPasses', 'GUBCoverCuts', 'ImpliedCuts',
        # 'MIPSepCuts', 'MIRCuts', 'NetworkCuts', 'SubMIPCuts', 'ZeroHalfCuts', 'ModKCuts',
        # 'Aggregate', 'AggFill', 'PreDual', 'DisplayInterval', 'IISMethod', 'InfUnbdInfo',
        # 'LogFile', 'PreCrush', 'PreDepRow', 'PreMIQPMethod', 'PrePasses', 'Presolve',
        # 'ResultFile', 'ImproveStartTime', 'ImproveStartGap', 'Threads', 'Dummy', 'OutputFlag']
        for key in self.options:
            prob.setParam( key, self.options[key] )
            
        if 'relax_integrality' in self.options:
            for v in prob.getVars():
                if v.vType != GRB.CONTINUOUS:
                    v.vType = GRB.CONTINUOUS
            prob.update()

        if _GUROBI_VERSION_MAJOR >= 5:
            for suffix in self.suffixes:
                if re.match(suffix,"dual"):
                    prob.setParam(GRB.Param.QCPDual,1)

        # Actually solve the problem.
        prob.optimize()

        # FIXME: can we get a return code indicating if Gurobi had a
        # significant failure?
        return Bunch(rc=None, log=None)


    def _gurobi_get_solution_status ( self ):
        status = self._gurobi_instance.Status
        if   GRB.OPTIMAL         == status: return SolutionStatus.optimal
        elif GRB.INFEASIBLE      == status: return SolutionStatus.infeasible
        elif GRB.CUTOFF          == status: return SolutionStatus.other
        elif GRB.INF_OR_UNBD     == status: return SolutionStatus.other
        elif GRB.INTERRUPTED     == status: return SolutionStatus.other
        elif GRB.LOADED          == status: return SolutionStatus.other
        elif GRB.SUBOPTIMAL      == status: return SolutionStatus.other
        elif GRB.UNBOUNDED       == status: return SolutionStatus.other
        elif GRB.ITERATION_LIMIT == status: return SolutionStatus.stoppedByLimit
        elif GRB.NODE_LIMIT      == status: return SolutionStatus.stoppedByLimit
        elif GRB.SOLUTION_LIMIT  == status: return SolutionStatus.stoppedByLimit
        elif GRB.TIME_LIMIT      == status: return SolutionStatus.stoppedByLimit
        elif GRB.NUMERIC         == status: return SolutionStatus.error
        raise RuntimeError('Unknown solution status returned by Gurobi solver')


    def _postsolve(self):

        # the only suffixes that we extract from GUROBI are
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
                raise RuntimeError("***The gurobi_direct solver plugin cannot extract solution suffix="+suffix)

        gprob = self._gurobi_instance

        if (gprob.getAttr(GRB.Attr.IsMIP)):
            extract_reduced_costs = False
            extract_duals = False

        pvars = gprob.getVars()
        cons = gprob.getConstrs()
        qcons = []
        if _GUROBI_VERSION_MAJOR >= 5:
            qcons = gprob.getQConstrs()
        
        results = SolverResults()
        soln = Solution()
        problem = results.problem
        solver  = results.solver

        solver.name = "Gurobi %s.%s%s" % gurobi.version()
        # solver.memory_used =
        # solver.user_time = None
        # solver.system_time = None
        solver.wallclock_time = gprob.Runtime
        # solver.termination_condition = None
        # solver.termination_message = None

        problem.name = gprob.ModelName
        problem.lower_bound = None
        problem.upper_bound = None
        problem.number_of_constraints          = len(cons)+len(qcons)+gprob.NumSOS
        problem.number_of_nonzeros             = gprob.NumNZs
        problem.number_of_variables            = gprob.NumVars
        problem.number_of_binary_variables     = gprob.NumBinVars
        problem.number_of_integer_variables    = gprob.NumIntVars
        problem.number_of_continuous_variables = gprob.NumVars \
                                                - gprob.NumIntVars \
                                                - gprob.NumBinVars
        problem.number_of_objectives = 1
        problem.number_of_solutions = gprob.SolCount

        problem.sense = ProblemSense.minimize
        if problem.sense == GRB_MAX: problem.sense = ProblemSense.maximize

        soln.status = self._gurobi_get_solution_status()

        if soln.status in (SolutionStatus.optimal, SolutionStatus.stoppedByLimit):
            obj_val = gprob.ObjVal
            if problem.sense == ProblemSense.minimize:
                problem.lower_bound = obj_val
                if problem.number_of_binary_variables + problem.number_of_integer_variables == 0:
                    problem.upper_bound = obj_val
            else:
                problem.upper_bound = obj_val
                if problem.number_of_binary_variables + problem.number_of_integer_variables == 0:
                    problem.lower_bound = obj_val

            soln.objective[self._objective_label].value = obj_val
            
            # Those variables not added by gurobi due to range constraints
            for var in itertools.islice(pvars,self._last_native_var_idx+1):
                soln.variable[ var.VarName ] = {"Value" : var.X, "Id" : len(soln.variable) - 1}

            if extract_reduced_costs is True:
                for var in itertools.islice(pvars,self._last_native_var_idx+1):
                    soln.variable[ var.VarName ]["Rc"] = var.Rc

            if extract_duals is True:
                for con in cons:
                    # Pi attributes in Gurobi are the constraint duals
                    soln.constraint[ con.ConstrName ].dual = con.Pi                
                for con in qcons:
                    # QCPI attributes in Gurobi are the constraint duals
                    soln.constraint[ con.QCName ].dual = con.QCPi

            if extract_slacks is True:
                for con in cons:
                    soln.constraint[ con.ConstrName ].slack = con.Slack
                for con in qcons:
                    soln.constraint[ con.QCName ].slack = con.QCSlack
                # The above loops may include range constraints but will 
                # always report a slack of zero since gurobi transforms
                # range constraints by adding a slack variable in the following way
                # L <= f(x) <= U 
                # becomes
                # 0 <= U-f(x) <= U-L
                # becomes
                # U-f(x) == s
                # 0 <= s <= U-L
                # Therefore we need to check the value of the associated slack variable
                # with its upper bound to compute the original constraint slacks. To conform
                # with the other problem writers we return the slack value that is largest in 
                # magnitude (L-f(x) or U-f(x))
                for con,var_idx in self._range_con_var_pairs:
                    var = pvars[var_idx]
                    # U-f(x)
                    Us_ = var.X
                    # f(x)-L
                    Ls_ = var.UB-var.X
                    if Us_ > Ls_:
                        soln.constraint[ con.ConstrName ].slack = Us_
                    else:
                        soln.constraint[ con.ConstrName ].slack = -Ls_
                    


        results.solution.insert(soln)

        self.results = results

        # Done with the model object; free up some memory.
        self._last_native_var_idx = -1
        self._range_con_var_pairs = []
        del gprob, self._gurobi_instance

        # let the base class deal with returning results.
        return OptSolver._postsolve(self)


if not gurobi_python_api_exists:
    SolverFactory().deactivate('_gurobi_direct')
    SolverFactory().deactivate('_mock_gurobi_direct')
