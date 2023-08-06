#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

#
# AMPL Problem Writer Plugin
#

__all__ = ['ProblemWriter_nl']

from coopr.opt import ProblemFormat, WriterFactory
from coopr.opt.base import *
from coopr.pyomo.base.objective import minimize, maximize
from coopr.pyomo.base import *
from coopr.pyomo.base import expr
from coopr.pyomo.base import external
from coopr.pyomo.base import SymbolMap
from coopr.pyomo.base import intrinsic_functions
from coopr.pyomo.base.var import _VarData, Var, _VarElement
from coopr.pyomo.base.numvalue import NumericConstant, native_numeric_types
from coopr.pyomo.base.param import _ParamData
from coopr.pyomo.base import var
from coopr.pyomo.base import param
from coopr.pyomo.base import numvalue
from coopr.pyomo.base.suffix import active_export_suffix_generator
from coopr.pyomo.expr.ampl_repn import generate_ampl_repn
from pyutilib.component.core import alias
from pyutilib.misc import PauseGC

import itertools
import logging
import operator
import os
import time
import sys

from six import itervalues, iteritems, iterkeys, StringIO
from six.moves import xrange, zip

logger = logging.getLogger('coopr.pyomo')

intrinsic_function_operators = {\
'log':    'o43',\
'log10':  'o42',\
'sin':    'o41',\
'cos':    'o46',
'tan':    'o38',\
'sinh':   'o40',\
'cosh':   'o45',\
'tanh':   'o37',\
'asin':   'o51',\
'acos':   'o53',\
'atan':   'o49',\
'exp':    'o44',\
'sqrt':   'o39',\
'asinh':  'o50',\
'acosh':  'o52',\
'atanh':  'o47',\
'pow':    'o5',\
'abs':    'o15'}


class _Counter(object):

    def __init__(self, start):
        self._id = start

    def __call__(self, obj):
        tmp = self._id
        self._id += 1
        return tmp



class ModelSOS(object):

    class AmplSuffix(object):

        def __init__(self,name):
            self.name = name
            self.ids = []
            self.vals = []

        def add(self,idx,val):
            if idx in self.ids:
                raise RuntimeError("The NL file format does not support multiple nonzero "\
                                    "values for a single component and suffix. \n"\
                                    "Suffix Name:  %s\n"\
                                    "Component ID: %s\n" % (self.name, idx))
            else:
                self.ids.append(idx)
                self.vals.append(val)
                    
        def genfilelines(self):
            base_line = "{0} {1}\n"
            return [base_line.format(idx, val) for idx, val in zip(self.ids,self.vals) if val != 0]

        def is_empty(self):
            return not bool(len(self.ids))

    def __init__(self,ampl_var_id, varID_map):

        self.ampl_var_id = ampl_var_id
        self.sosno = self.AmplSuffix('sosno')
        self.ref = self.AmplSuffix('ref')
        self.block_cntr = 0
        self.varID_map = varID_map

    def count_constraint(self,con,level,index=None):
        
        ampl_var_id = self.ampl_var_id
        varID_map = self.varID_map
        sos_vars = con.sos_vars()

        # Identifies the the current set from others in the NL file
        self.block_cntr += 1

        # If SOS1, the identifier must be positive
        # if SOS2, the identifier must be negative
        sign_tag = 1
        if level == 2:
            sign_tag = -1

        if index is None:
            tmpSet = con.sos_set()
        else:
            tmpSet = con.sos_set()[index]

        # Get all the variables
        cntr = 0
        for x in tmpSet:
            ID = ampl_var_id[varID_map[id(sos_vars[x])]]
            self.sosno.add(ID,self.block_cntr*sign_tag)
            # We need to weight each variable
            # For now we just increment a counter
            if cntr > 0:
                # We only need to report variables with weight greater than zero
                # Zero weight is assumed for variables with no weight reported.
                self.ref.add(ID,cntr)
            cntr += 1

class RepnWrapper(object):
    __slots__ = ('repn','_linear_vars','_nonlinear_vars')
    def __init__(self,repn,linear,nonlinear):
        self.repn = repn
        self._linear_vars = linear
        self._nonlinear_vars = nonlinear


class ProblemWriter_nl(AbstractProblemWriter):

    alias(str(ProblemFormat.nl))

    def __init__(self):
        self._ampl_var_id = {}
        self._ampl_con_id = {}
        self._ampl_obj_id = {}
        self._OUTPUT = None
        self._varID_map = None
        AbstractProblemWriter.__init__(self, ProblemFormat.nl)

    def __call__(self, model, filename, solver_capability, symbolic_solver_labels, **kwds):
        # Pause the GC for the duration of this method
        suspend_gc = PauseGC()
        if filename is None:
            filename = model.cname() + ".nl"
        with open(filename,"w") as f:
            self._OUTPUT = f
            symbol_map = self._print_model_NL(model, solver_capability, symbolic_solver_labels, verbose=False)
        self._OUTPUT = None
        self._varID_map = None
        return filename, symbol_map

    def _get_bound(self, exp):
        if exp.is_fixed():
            return exp()
        else:
            raise ValueError("ERROR: nonconstant bound: " + str(exp))

    def _print_nonlinear_terms_NL(self, exp):
        OUTPUT = self._OUTPUT
        exp_type = type(exp)
        # JDS: check list first so that after this, we know that exp
        # must be some form of NumericValue
        if exp_type is list:
            # this is an implied summation of expressions (we did not create a new sum expression for efficiency)
            # this should be a list of tuples where [0] is the coeff and [1] is the expr to write
            n = len(exp)
            if n > 2:
                # sum
                OUTPUT.write( "o54\n%d\n"%(n) )
                for i in xrange(0,n):
                    assert(exp[i].__class__ is tuple)
                    coef = exp[i][0]
                    child_exp = exp[i][1]
                    if coef != 1.0:
                        # *
                        OUTPUT.write( "o2\nn{0!r}\n".format(coef) )
                    self._print_nonlinear_terms_NL(child_exp)
            else:
                for i in xrange(0,n):
                    assert(exp[i].__class__ is tuple)
                    coef = exp[i][0]
                    child_exp = exp[i][1]
                    if i != n-1:
                        # need the + op if it is not the last entry in the list
                        # +
                        OUTPUT.write( "o0\n" )
                    if coef != 1.0:
                        # *
                        OUTPUT.write( "o2\nn{0!r}\n".format(coef) )
                    self._print_nonlinear_terms_NL(child_exp)
        elif exp.is_expression():
            if exp_type is expr._SumExpression:
                n = len(exp._args)
                if n > 2:
                    # sum
                    OUTPUT.write( "o54\n%d\n"%(n) )
                    if exp._const != 0.0:
                        # +
                        OUTPUT.write( "o0\nn{0!r}\n".format(exp._const) )
                    for i in xrange(0,n):
                        if exp._coef[i] != 1:
                            # *
                            OUTPUT.write( "o2\nn{0!r}\n".format(exp._coef[i]) )
                        self._print_nonlinear_terms_NL(exp._args[i])
                else:
                    if exp._const != 0.0:
                        # +
                        OUTPUT.write( "o0\nn{0!r}\n".format(exp._const) )
                    for i in xrange(0,n-1):
                        # +
                        OUTPUT.write( "o0\n" )
                        if exp._coef[i] != 1.0:
                            # *
                            OUTPUT.write( "o2\nn{0!r}\n".format(exp._coef[i]) )
                        self._print_nonlinear_terms_NL(exp._args[i])
                    if exp._coef[n-1] != 1.0:
                        # *
                        OUTPUT.write( "o2\nn{0!r}\n".format(exp._coef[n-1]) )
                    self._print_nonlinear_terms_NL(exp._args[n-1])
    
            elif exp_type is expr._ProductExpression:
                denom_exists = False
                if len(exp._denominator) == 0:
                    pass
                else:
                    # /
                    OUTPUT.write( "o3\n" )
                    denom_exists = True
                if exp._coef != 1.0:
                    # *
                    OUTPUT.write( "o2\nn{0!r}\n".format(exp._coef) )
                if len(exp._numerator) == 0:
                    OUTPUT.write( "n1\n" )
                # print out the numerator
                child_counter = 0
                max_count = len(exp._numerator)-1
                for child_exp in exp._numerator:
                    if child_counter < max_count:
                        # *
                        OUTPUT.write( "o2\n" )
                    self._print_nonlinear_terms_NL(child_exp)
                    child_counter += 1
                if denom_exists:
                    # print out the denominator
                    child_counter = 0
                    max_count = len(exp._denominator)-1
                    for child_exp in exp._denominator:
                        if child_counter < max_count:
                            # *
                            OUTPUT.write( "o2\n" )
                        self._print_nonlinear_terms_NL(child_exp)
                        child_counter += 1
    
            elif exp_type is external._ExternalFunctionExpression:
                OUTPUT.write("f%d %d\n" % (
                        self.external_byFcn[exp._fcn._function][1], 
                        len(exp._args) ) )
                for arg in exp._args:
                    if isinstance(arg, basestring):
                        OUTPUT.write("h%d:%s\n" % (len(arg), arg))
                    else:
                        self._print_nonlinear_terms_NL(arg)
            elif isinstance(exp, expr._IntrinsicFunctionExpression):
                intr_expr = intrinsic_function_operators.get(exp.cname(),None)
                if intr_expr is not None:
                    OUTPUT.write( intr_expr+"\n" )
                else:
                    logger.error("Unsupported intrinsic function ({0})", exp.cname(True))
                    raise TypeError("ASL writer does not support '{0}' expressions"
                                   .format(exp.cname(True)))
                    
                for child_exp in exp._args:
                    self._print_nonlinear_terms_NL(child_exp)
            elif exp_type is expr.Expr_if:
                OUTPUT.write("o35\n")
                self._print_nonlinear_terms_NL(exp._if)
                self._print_nonlinear_terms_NL(exp._then)
                self._print_nonlinear_terms_NL(exp._else)
            elif exp_type is expr._InequalityExpression:
                len_args = len(exp._args)
                assert len_args in [2,3]
                left = exp._args[0]
                middle = exp._args[1]
                right = None
                if len_args == 3:
                    right = exp._args[2]
                    OUTPUT.write("o21\n") # and
                if exp._strict[0]:
                    OUTPUT.write("o22\n")
                else:
                    OUTPUT.write("o23\n")
                self._print_nonlinear_terms_NL(left)
                self._print_nonlinear_terms_NL(middle)
                if not right is None:
                    if exp._strict[1]:
                        OUTPUT.write("o22\n")
                    else:
                        OUTPUT.write("o23\n")
                    self._print_nonlinear_terms_NL(middle)
                    self._print_nonlinear_terms_NL(right)
            elif exp_type is expr._EqualityExpression:
                OUTPUT.write("o24\n")
                self._print_nonlinear_terms_NL(exp._args[0])
                self._print_nonlinear_terms_NL(exp._args[1])
            else:
                raise ValueError("Unsupported expression type (%s) in _print_nonlinear_terms_NL" % exp_type)

        elif isinstance(exp,var._VarData) and not exp.is_fixed():
            OUTPUT.write( "v{0}\n".format(self.ampl_var_id[self._varID_map[id(exp)]]) )
        elif isinstance(exp,param._ParamData):
            OUTPUT.write( "n{0!r}\n".format(value(exp)) )
        elif isinstance(exp,NumericConstant) or exp.is_fixed():
            OUTPUT.write( "n{0!r}\n".format(value(exp)) )
        else:
            raise ValueError("Unsupported expression type (%s) in _print_nonlinear_terms_NL" % exp_type)
        
    
    def _print_model_NL(self, model, solver_capability, symbolic_solver_labels, verbose=False):

        OUTPUT = self._OUTPUT
        assert OUTPUT is not None

        # maps NL variables to the "real" variable names in the problem.
        # it's really NL variable ordering, as there are no variable names
        # in the NL format. however, we by convention make them go from
        # x0 upward.

#        start_overall_time = time.clock()

        # create the symbol_map
        symbol_map = SymbolMap(model)

        # Speeds up calling cname on every component when
        # writing .row and .col files (when symbolic_solver_labels is True)
        name_labeler = NameLabeler()

        #
        # Collect statistics
        #
        self_ampl_var_id = self.ampl_var_id = {}
        self_ampl_con_id = self.ampl_con_id = {}
        self_ampl_obj_id = self.ampl_obj_id = {}

        Vars_dict = dict() # will be the entire list of all vars used in the problem
        Objectives_dict = dict() # will be the entire list of all objective used in the problem (size=1)
        Constraints_dict = dict() # will be the entire list of all constraints used in the problem

        # linear variables
        LinearVars = set()
        LinearVarsInt = set()
        LinearVarsBool = set()

        # Tabulate the External Function definitions
        self.external_byFcn = {}
        external_Libs = set()
        for block in model.all_blocks():
            for fcn in active_subcomponents_generator(block,ExternalFunction):
                if fcn._function in self.external_byFcn and \
                        self.external_byFcn[fcn._function][0]._library != fcn._library:
                    raise RuntimeError(
                        "The same external function name (%s) is associated "
                        "with two different libraries (%s through %s, and %s "
                        "through %s).  The ASL solver will fail to link "
                        "correctly." %
                        ( fcn._function, 
                          self.external_byFcn[fcn._function]._library,
                          self.external_byFcn[fcn._function]._library.cname(True),
                          fcn._library,
                          fcn.cname(True) ) )
                self.external_byFcn[fcn._function] = (fcn, len(self.external_byFcn))
                external_Libs.add(fcn._library)
        if external_Libs:
            os.environ["COOPR_AMPLFUNC"] = "\n".join(sorted(external_Libs))
        elif "COOPR_AMPLFUNC" in os.environ:
            del os.environ["COOPR_AMPLFUNC"]


#        print "Generate objective representation:",
#        start_time = time.clock()

        # create a deterministic var labeling
        cntr = 0
        for block in model.all_blocks():
            vars_counter = tuple(enumerate(active_subcomponents_data_generator(block, Var), cntr))
            cntr += len(vars_counter)+1
            Vars_dict.update(vars_counter)
        self._varID_map = dict((id(val),key) for key,val in iteritems(Vars_dict))
        self_varID_map = self._varID_map
        # Use to label the rest of the components (which we will not encounter twice)
        trivial_labeler = _Counter(cntr)
        

        #
        # Count number of objectives and build the ampl_repns
        #
        n_objs = 0
        n_nonlinear_objs = 0
        ObjVars = set()
        ObjNonlinearVars = set()
        ObjNonlinearVarsInt = set()
        active_objective = None
        # We only check for an objective on the top level model
        # Create a suffix component for the ampl_repn
        obj_ampl_repn_suffix = model.subcomponent("_ampl_repn")
        if (obj_ampl_repn_suffix is None) or (not obj_ampl_repn_suffix.type() is Suffix) or (not obj_ampl_repn_suffix.active is True):
            model.del_component("_ampl_repn")
            obj_ampl_repn_suffix = model._ampl_repn = Suffix(direction=Suffix.LOCAL,datatype=None)

        gen_obj_ampl_repn = getattr(model,"gen_obj_ampl_repn",True)
        for active_objective in active_subcomponents_data_generator(model,Objective):
        
            if gen_obj_ampl_repn is True:
                ampl_repn = generate_ampl_repn(active_objective.expr)
                obj_ampl_repn_suffix.setValue(active_objective, ampl_repn)
            else:
                ampl_repn = obj_ampl_repn_suffix.getValue(active_objective)

            wrapped_ampl_repn = RepnWrapper(ampl_repn,
                                            list(self_varID_map[id(var)] for var in ampl_repn._linear_vars),
                                            list(self_varID_map[id(var)] for var in ampl_repn._nonlinear_vars))
            
            LinearVars.update(wrapped_ampl_repn._linear_vars)
            ObjNonlinearVars.update(wrapped_ampl_repn._nonlinear_vars)
            
            ObjVars.update(wrapped_ampl_repn._linear_vars)
            ObjVars.update(wrapped_ampl_repn._nonlinear_vars)

            obj_ID = trivial_labeler(active_objective)
            Objectives_dict[obj_ID] = (active_objective, wrapped_ampl_repn)
            self_ampl_obj_id[obj_ID] = n_objs
            symbol_map.updateSymbols([(active_objective, ".o%d"%n_objs)])

            n_objs += 1
            if ampl_repn.is_nonlinear():
                n_nonlinear_objs += 1

        # I don't think this is necessarily true for the entire code base, 
        # but seeing has how its never been tested we should go ahead and
        # raise an exception
        if n_objs > 1:
            raise ValueError("The NL writer has detected multiple active objective functions, but currently only handles a single objective.")
        else:
            symbol_map.alias(symbol_map.bySymbol[".o0"](),"__default_objective__")

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Generate constraint repns:",
#        start_time = time.clock()

        #
        # Count number of constraints and build the ampl_repns
        #
        n_ranges = 0
        n_single_sided_ineq = 0
        n_equals = 0
        n_nonlinear_constraints = 0
        ConNonlinearVars = set()
        ConNonlinearVarsInt = set()
        nnz_grad_constraints = 0
        constraint_bounds_dict = {}
        nonlin_con_order_list = []
        lin_con_order_list = []        

        for block in model.all_blocks():
            all_repns = list()
            
            gen_con_ampl_repn = getattr(block,"gen_con_ampl_repn",True)

            # Create a suffix component for the ampl_repn
            block_ampl_repn_suffix = block.subcomponent("_ampl_repn")
            if (block_ampl_repn_suffix is None) or (not block_ampl_repn_suffix.type() is Suffix) or (not block_ampl_repn_suffix.active is True):
                block.del_component("_ampl_repn")
                block_ampl_repn_suffix = block._ampl_repn = Suffix(direction=Suffix.LOCAL,datatype=None)

            for constraint_data in active_subcomponents_data_generator(block,Constraint):
                
                con_ID = trivial_labeler(constraint_data)
                if gen_con_ampl_repn is True:
                    ampl_repn = generate_ampl_repn(constraint_data.body)
                    all_repns.append((constraint_data,ampl_repn))
                else:
                    ampl_repn = block_ampl_repn_suffix.getValue(constraint_data)

                wrapped_ampl_repn = RepnWrapper(ampl_repn,
                                                list(self_varID_map[id(var)] for var in ampl_repn._linear_vars),
                                                list(self_varID_map[id(var)] for var in ampl_repn._nonlinear_vars))
                
                ### GAH: Even if this is fixed, it is still useful to write out these types of constraints
                ###      (trivial) as a feasibility check for fixed variables, in which case the solver
                ###      will pick up on the model infeasibility.
                ### **NOTE: If we change this loop to start skipping fixed constraints, then the "J" section must
                ###         be updated to do so as well since the constraint id is calculated on the fly using
                ###         a cntr.
                #if ampl_repn.is_fixed():
                #    continue
                    
                if ampl_repn.is_nonlinear():
                    nonlin_con_order_list.append(con_ID)
                    n_nonlinear_constraints += 1
                else:
                    lin_con_order_list.append(con_ID)

                Constraints_dict[con_ID] = (constraint_data, wrapped_ampl_repn)
                
                LinearVars.update(wrapped_ampl_repn._linear_vars)
                ConNonlinearVars.update(wrapped_ampl_repn._nonlinear_vars)
                    
                nnz_grad_constraints += len(set(wrapped_ampl_repn._linear_vars).union(wrapped_ampl_repn._nonlinear_vars))
    
                L = None
                U = None
                if constraint_data.lower is not None: L = self._get_bound(constraint_data.lower)
                if constraint_data.upper is not None: U = self._get_bound(constraint_data.upper)

                offset = ampl_repn._constant
                #if constraint_data._equality is True:
                #    assert L == U
                if L == U:
                    constraint_bounds_dict[con_ID] = "4 {0!r}\n".format(L-offset)
                    n_equals += 1
                elif L is None:
                    constraint_bounds_dict[con_ID] = "1 {0!r}\n".format(U-offset)
                    n_single_sided_ineq += 1
                elif U is None:
                    constraint_bounds_dict[con_ID] = "2 {0!r}\n".format(L-offset)
                    n_single_sided_ineq += 1
                elif (L > U):
                    msg = 'Constraint {0}: lower bound greater than upper' \
                        ' bound ({1} > {2})'
                    raise ValueError(msg.format(con_ID, str(L), str(U)))
                else:
                    constraint_bounds_dict[con_ID] = "0 {0!r} {1!r}\n".format(L-offset, U-offset)
                    # double sided inequality
                    # both are not none and they are valid
                    n_ranges += 1
            block_ampl_repn_suffix.updateValues(all_repns)
            
        # create the ampl constraint ids
        self_ampl_con_id.update((con_ID,row_id) for row_id,con_ID in \
                                enumerate(itertools.chain(nonlin_con_order_list,lin_con_order_list)))
        # populate the symbol_map
        symbol_map.updateSymbols( [(Constraints_dict[con_ID][0],".c%d"%row_id) for row_id,con_ID in \
                                   enumerate(itertools.chain(nonlin_con_order_list,lin_con_order_list))] )

#        end_time = time.clock()
#        print (end_time - start_time)


#        print "Partitioning Variable Types:",
#        start_time = time.clock()

        LinearVars = LinearVars.difference(ObjNonlinearVars)
        LinearVars = LinearVars.difference(ConNonlinearVars)

        ### There used to be an if statement here for the following code block 
        ### checking model.statistics.num_binary_vars was greater than zero.
        ### To this day, I don't know how it worked.
        ### TODO: Figure out why
        ###############
        for var_ID in LinearVars:
            var = Vars_dict[var_ID]
            var_type = type(var.domain)
            if var_type is IntegerSet:
                LinearVarsInt.add(var_ID)
            elif var_type is BooleanSet:
                L = var.lb
                U = var.ub
                if L is None or U is None:
                    raise ValueError("Variable " + str(var.cname(True)) +\
                                     "is binary, but does not have lb and ub set")
                elif value(L) == 0 and value(U) == 1:
                    LinearVarsBool.add(var_ID)
                else:
                    LinearVarsInt.add(var_ID)
        LinearVars.difference_update(LinearVarsInt)
        LinearVars.difference_update(LinearVarsBool)

        for var_ID in ObjNonlinearVars:
            var_type = type(Vars_dict[var_ID].domain)
            if var_type is IntegerSet or var_type is BooleanSet:
                ObjNonlinearVarsInt.add(var_ID)
        ObjNonlinearVars.difference_update(ObjNonlinearVarsInt)
        for var_ID in ConNonlinearVars:
            var_type = type(Vars_dict[var_ID].domain)
            if var_type is IntegerSet or var_type is BooleanSet:
                ConNonlinearVarsInt.add(var_ID)
        ConNonlinearVars.difference_update(ConNonlinearVarsInt)
        ##################

        Nonlinear_Vars_in_Objs_and_Constraints = ObjNonlinearVars.intersection(ConNonlinearVars)
        Discrete_Nonlinear_Vars_in_Objs_and_Constraints = ObjNonlinearVarsInt.intersection(ConNonlinearVarsInt)
        ObjNonlinearVars = ObjNonlinearVars.difference(Nonlinear_Vars_in_Objs_and_Constraints)
        ConNonlinearVars = ConNonlinearVars.difference(Nonlinear_Vars_in_Objs_and_Constraints)
        ObjNonlinearVarsInt = ObjNonlinearVarsInt.difference(Discrete_Nonlinear_Vars_in_Objs_and_Constraints)
        ConNonlinearVarsInt = ConNonlinearVarsInt.difference(Discrete_Nonlinear_Vars_in_Objs_and_Constraints)
        
        # put the ampl variable id into the variable
        full_var_list = []
        full_var_list.extend(sorted(Nonlinear_Vars_in_Objs_and_Constraints))
        full_var_list.extend(sorted(Discrete_Nonlinear_Vars_in_Objs_and_Constraints))
        idx_nl_both = len(full_var_list)
        #
        full_var_list.extend(sorted(ConNonlinearVars))
        full_var_list.extend(sorted(ConNonlinearVarsInt))
        idx_nl_con = len(full_var_list)
        #
        full_var_list.extend(sorted(ObjNonlinearVars))
        full_var_list.extend(sorted(ObjNonlinearVarsInt))
        idx_nl_obj = len(full_var_list)
        #
        full_var_list.extend(sorted(LinearVars))
        full_var_list.extend(sorted(LinearVarsBool))
        full_var_list.extend(sorted(LinearVarsInt))

        if (idx_nl_obj == idx_nl_con):
            idx_nl_obj = idx_nl_both

        # create the ampl variable column ids
        self_ampl_var_id.update( (var_ID,column_id) for column_id,var_ID in enumerate(full_var_list))
        # populate the symbol_map
        symbol_map.updateSymbols( [(Vars_dict[var_ID],".v%d"%column_id) for column_id,var_ID in enumerate(full_var_list)] )

        ##################################################
        ############ # LQM additions start here ##########
        ##################################################

        ###                                                                                                    
        # Generate file containing matrices for continuity variables between blocks.                            
        # This checks for a LOCAL suffix 'lqm' on variables.
        ###
        lqm_suffix = model.subcomponent("lqm")
        if (lqm_suffix is None) or (not (lqm_suffix.type() is Suffix)) or \
           (not (lqm_suffix.active is True)) or (not (lqm_suffix.getDirection() is Suffix.LOCAL)):
            lqm_suffix = None
        if lqm_suffix is not None:
            lqm_var_column_ids = []
            for var_ID in full_var_list:
                lqm = lqm_suffix.getValue(Vars_dict[var_ID])
                if lqm != -1:
                    # store the column index (and translate to one-based indexing
                    lqm_var_column_ids.append(self_ampl_var_id[var_ID]+1)

            num_lqm_vars = len(lqm_var_column_ids)
            if num_lqm_vars > 0:
                lqm_output_name = OUTPUT.name.split('.')[0]+".lqm"
                LQM_OUTPUT = open(lqm_output_name,'w')
                LQM_OUTPUT.write( "Matrix Li\n" )
                LQM_OUTPUT.write( "%d\n"%(len(full_var_list)) )
                LQM_OUTPUT.write( "%d\n"%(num_lqm_vars) )
                LQM_OUTPUT.write( "%d\n"%(num_lqm_vars) )
                # The matrix uses one based indexing
                for row_id, col_id in enumerate(lqm_var_column_ids,1):
                    LQM_OUTPUT.write( "%d %d 1\n" % (row_id, col_id) )
                LQM_OUTPUT.write( "Matrix Qi\n" )
                LQM_OUTPUT.write("%d\n" % (num_lqm_vars) )
                LQM_OUTPUT.write("%d\n" % (num_lqm_vars) )
                LQM_OUTPUT.write("%d\n" % (num_lqm_vars) )
                # one based indexing
                for counter in xrange(1,num_lqm_vars+1):
                    LQM_OUTPUT.write("%d %d -1\n" % (counter, counter) )
                LQM_OUTPUT.close()

        ##################################################
        ############ # LQM additions end here ############
        ##################################################

#        end_time = time.clock()
#        print (end_time - start_time)

        colfilename = None
        if OUTPUT.name.endswith('.nl'):
            colfilename = OUTPUT.name.replace('.nl','.col')
        else:
            colfilename = OUTPUT.name+'.col'
        if symbolic_solver_labels is True:
            colf = open(colfilename,'w')
            for var_ID in full_var_list:
                colf.write(name_labeler(Vars_dict[var_ID])+'\n')
            colf.close()
        
#        print "Printing NL file header:",
#        start_time = time.clock()
        #
        # Print Header
        #
        # LINE 1
        #
        OUTPUT.write("g3 1 1 0\t# problem {0}\n".format(model.cname()) )
        #
        # LINE 2
        #
        OUTPUT.write( " {0} {1} {2} {3} {4} \t# vars, constraints, objectives, general inequalities, equalities\n" \
                          .format(len(full_var_list), n_single_sided_ineq+n_ranges+n_equals, n_objs, n_ranges, n_equals) )
        #
        # LINE 3
        #
        OUTPUT.write( " {0} {1} \t# nonlinear constraints, objectives\n".format(n_nonlinear_constraints, n_nonlinear_objs) )
        #
        # LINE 4
        #
        OUTPUT.write( " 0 0\t# network constraints: nonlinear, linear\n" )
        #
        # LINE 5
        #
        OUTPUT.write( " {0} {1} {2} \t# nonlinear vars in constraints, objectives, both\n" \
                          .format(idx_nl_con, idx_nl_obj, idx_nl_both) )

        #
        # LINE 6
        #
        OUTPUT.write( " 0 {0} 0 1\t# linear network variables; functions; arith, flags\n".format(len(self.external_byFcn)) )
        #
        # LINE 7
        #
        n_int_nonlinear_b = len(Discrete_Nonlinear_Vars_in_Objs_and_Constraints)
        n_int_nonlinear_c = len(ConNonlinearVarsInt)
        n_int_nonlinear_o = len(ObjNonlinearVarsInt) 
        OUTPUT.write( " {0} {1} {2} {3} {4} \t# discrete variables: binary, integer, nonlinear (b,c,o)\n" \
           .format(len(LinearVarsBool), len(LinearVarsInt), n_int_nonlinear_b, n_int_nonlinear_c, n_int_nonlinear_o) )
        #
        # LINE 8
        #
        # objective info computed above
        OUTPUT.write( " {0} {1} \t# nonzeros in Jacobian, obj. gradient\n".format(nnz_grad_constraints, len(ObjVars)) )
        #
        # LINE 9
        #
        OUTPUT.write( " 0 0\t# max name lengths: constraints, variables\n" )
        #
        # LINE 10
        #
        OUTPUT.write( " 0 0 0 0 0\t# common exprs: b,c,o,c1,o1\n" )

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing constraints:",
#        start_time = time.clock()


        #
        # "F" lines
        #
        for fcn, fid in sorted(itervalues(self.external_byFcn), key=operator.itemgetter(1)):
            OUTPUT.write( "F%d 1 -1 %s\n" % ( fid, fcn._function ))

        #
        # "S" lines
        #

        # Tranlate the SOSConstraint component into ampl suffixes
        # SOS constraints - largely taken from cpxlp.py so updates there,
        # should be applied here
        # TODO: Allow users to specify the variables coefficients for custom
        # branching/set orders - refer to cpxlp.py
        sos1 = solver_capability("sos1")
        sos2 = solver_capability("sos2")
        modelSOS = ModelSOS(self_ampl_var_id, self_varID_map)
        if sos1 or sos2:
            for block in model.all_blocks():
                for con in itervalues(block.active_subcomponents(SOSConstraint)):
                    level = con.sos_level()
                    if (level == 1 and sos1) or (level == 2 and sos2):
                        masterIndex = con.sos_set_set()
                        if None in masterIndex:
                            modelSOS.count_constraint(con, level)
                        else:
                            for index in masterIndex:
                                modelSOS.count_constraint(con, level, index)
        var_sosno_suffix = modelSOS.sosno
        var_ref_suffix = modelSOS.ref
        sosconstraint_sosno_vals = set(var_sosno_suffix.vals)

        # Translate the rest of the Pyomo Suffix components
        suffix_header_line = "S{0} {1} {2}\n"
        suffix_line = "{0} {1!r}\n"
        var_tag = 0
        con_tag = 1
        obj_tag = 2
        prob_tag = 3
        suffix_dict = dict(active_export_suffix_generator(model))
        has_dual_initials = False
        if not ('sosno' in suffix_dict):
            # We still need to write out the SOSConstraint suffixes
            # even though these may have not been "declared" on the model
            s_lines = var_sosno_suffix.genfilelines()
            len_s_lines = len(s_lines)
            if len_s_lines > 0:
                OUTPUT.write(suffix_header_line.format(var_tag,len_s_lines,'sosno'))
                OUTPUT.writelines(s_lines)
        else:
            # I am choosing not to allow a user to mix the use of the Pyomo
            # SOSConstraint component and manual sosno declarations within
            # a single model. I initially tried to allow this but the
            # var section of the code below blows up for two reason. (1)
            # we have to make sure that the sosno suffix is not defined
            # twice for the same variable (2) We have to make sure that
            # the automatically chosen sosno used by the SOSConstraint
            # translation does not already match one a user has manually
            # implemented (this would modify the members in an sos set).
            # Since this suffix is exclusively used for defining sos sets,
            # there is no reason a user can not just stick to one method.
            if not var_sosno_suffix.is_empty():
                raise RuntimeError("The Pyomo NL file writer does not allow both manually "\
                                    "declared 'sosno' suffixes as well as SOSConstraint "\
                                    "components to exist on a single model. To avoid this "\
                                    "error please use only one of these methods to define "\
                                    "special ordered sets.")
        if not ('ref' in suffix_dict):
            # We still need to write out the SOSConstraint suffixes
            # even though these may have not been "declared" on the model
            s_lines = var_ref_suffix.genfilelines()
            len_s_lines = len(s_lines)
            if len_s_lines > 0:
                OUTPUT.write(suffix_header_line.format(var_tag,len_s_lines,'ref'))
                OUTPUT.writelines(s_lines)
        else:
            # see reason (1) in the paragraph above for why we raise this
            # exception (replacing sosno with ref).
            if not var_ref_suffix.is_empty():
                raise RuntimeError("The Pyomo NL file writer does not allow both manually "\
                                    "declared 'ref' suffixes as well as SOSConstraint "\
                                    "components to exist on a single model. To avoid this "\
                                    "error please use only one of these methods to define "\
                                    "special ordered sets.")
        for suffix_name, suffix in iteritems(suffix_dict): 
            if suffix.getDatatype() not in (float,int,bool,str):
                raise ValueError("The Pyomo NL file writer requires that all active export Suffix components "\
                                  "have a strict datatype equal to one of %s, but Suffix component with "\
                                  "name %s has datatype %s" % ((float,int,bool,str), suffix_name, suffix.getDatatype()))
            if suffix_name == "dual":
                # The NL file format has a special section for dual initializations
                has_dual_initials = True
                continue
            float_tag = 0
            if suffix.getDatatype() is float:
                float_tag = 4
            ################## vars
            s_lines = []
            for var_ID in full_var_list:
                suffix_value = suffix.getNumericValue(Vars_dict[var_ID])
                if suffix_value is not None:
                    s_lines.append(suffix_line.format(self_ampl_var_id[var_ID],suffix_value))
            len_s_lines = len(s_lines)
            if len_s_lines > 0:
                OUTPUT.write(suffix_header_line.format(var_tag | float_tag, len_s_lines,suffix_name))
                OUTPUT.writelines(s_lines)
                    
            ################## constraints
            s_lines = []
            for con_ID, (con_component, wrapped_ampl_repn) in iteritems(Constraints_dict):
                suffix_value = suffix.getNumericValue(con_component)
                if suffix_value is not None:
                    s_lines.append(suffix_line.format(self_ampl_con_id[con_ID],suffix_value))
            len_s_lines = len(s_lines)
            if len_s_lines > 0:
                OUTPUT.write(suffix_header_line.format(con_tag | float_tag, len_s_lines,suffix_name))
                OUTPUT.writelines(s_lines)

            ################## objectives
            s_lines = []
            for obj_ID, (obj_component, wrapped_ampl_repn) in iteritems(Objectives_dict):
                suffix_value = suffix.getNumericValue(obj_component)
                if suffix_value is not None:
                    s_lines.append(suffix_line.format(self_ampl_obj_id[obj_ID],suffix_value))
            len_s_lines = len(s_lines)
            if len_s_lines > 0:
                OUTPUT.write(suffix_header_line.format(obj_tag | float_tag, len_s_lines,suffix_name))
                OUTPUT.writelines(s_lines)

            ################## problems (in this case the one problem)
            suffix_value = suffix.getNumericValue(model)
            if suffix_value is not None:
                OUTPUT.write(suffix_header_line.format(prob_tag | float_tag, 1,suffix_name))
                OUTPUT.write(suffix_line.format(0,suffix_value))
        del modelSOS

        #
        # "C" lines
        #
        rowfilename = None
        if OUTPUT.name.endswith('.nl'):
            rowfilename = OUTPUT.name.replace('.nl','.row')
        else:
            rowfilename = OUTPUT.name+'.row'
        if symbolic_solver_labels is True:
            rowf = open(rowfilename,'w')

        cu = [0 for i in xrange(len(full_var_list))]
        for con_ID in nonlin_con_order_list:
            con_data, wrapped_ampl_repn = Constraints_dict[con_ID]
            row_id = self_ampl_con_id[con_ID]
            OUTPUT.write( "C%d\n"%(row_id) )
            if symbolic_solver_labels is True:
                rowf.write( name_labeler(con_data)+"\n" ) 
            self._print_nonlinear_terms_NL(wrapped_ampl_repn.repn._nonlinear_expr)

            for var_ID in set(wrapped_ampl_repn._linear_vars).union(wrapped_ampl_repn._nonlinear_vars):
                cu[self_ampl_var_id[var_ID]] += 1

        for con_ID in lin_con_order_list:
            con_data, wrapped_ampl_repn = Constraints_dict[con_ID]
            row_id = self_ampl_con_id[con_ID]
            con_vars = set(wrapped_ampl_repn._linear_vars)
            for var_ID in con_vars:
                cu[self_ampl_var_id[var_ID]] += 1
            OUTPUT.write( "C%d\n"%(row_id) )
            if symbolic_solver_labels is True:
                rowf.write( name_labeler(con_data)+"\n" )
            OUTPUT.write( "n0\n" )

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing objective:",
#        start_time = time.clock()
        #
        # "O" lines
        #
        for obj_ID, (obj, wrapped_ampl_repn) in iteritems(Objectives_dict):

            k = 0
            if not obj.is_minimizing():
                k = 1

            OUTPUT.write( "O%d %d\n"%(self_ampl_obj_id[obj_ID], k) )
            if symbolic_solver_labels is True:
                rowf.write(name_labeler(obj)+"\n")

            if wrapped_ampl_repn.repn.is_linear():
                OUTPUT.write( "n{0!r}\n".format(wrapped_ampl_repn.repn._constant) )
            else:
                if wrapped_ampl_repn.repn._constant != 0.0:
                    # +
                    OUTPUT.write( "o0\nn{0!r}\n".format(wrapped_ampl_repn.repn._constant) )
                self._print_nonlinear_terms_NL(wrapped_ampl_repn.repn._nonlinear_expr)

        if symbolic_solver_labels is True:
            rowf.close()
        del name_labeler

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing intializations:",
#        start_time = time.clock()

        #
        # "d" lines
        #
        # dual initialization
        if has_dual_initials is True:
            dual_suffix = model.dual
            s_lines = []
            for con_ID, (con_component, wrapped_ampl_repn) in iteritems(Constraints_dict):
                suffix_value = dual_suffix.getNumericValue(con_component)
                if (suffix_value is not None) and (suffix_value != 0):
                    s_lines.append(suffix_line.format(self_ampl_con_id[con_ID],suffix_value))
            len_s_lines = len(s_lines)
            if len_s_lines > 0:
                OUTPUT.write( "d%d\n"%(len_s_lines) )
                OUTPUT.writelines(s_lines)
            

        #
        # "x" lines
        #
        # variable initialization
        var_bound_list = []
        x_init_list = []
        for ampl_var_id, var_ID in enumerate(full_var_list):
            var = Vars_dict[var_ID]
            # FIXME: This will need to change when var.value changes/goes away
            #        The test is here because we are inconsistent about initializing
            #        values of variables
            if var.value is not None:
                x_init_list.append("{0} {1!r}\n".format(ampl_var_id,var.value))
            if isinstance(var.domain, BooleanSet):
                var_bound_list.append("0 0 1\n")
                continue
            L = var.lb
            U = var.ub
            if L is not None:
                Lv = value(L)
                if U is not None:
                    Uv = value(U)
                    if Lv == Uv:
                        var_bound_list.append("4 {0!r}\n".format(Lv))
                    else:
                        var_bound_list.append("0 {0!r} {1!r}\n".format(Lv, Uv))
                else:
                    var_bound_list.append("2 {0!r}\n".format(Lv))
            elif U is not None:
                var_bound_list.append("1 {0!r}\n".format(value(U)))
            else:
                var_bound_list.append("3\n")


        OUTPUT.write( "x%d\n"%(len(x_init_list)) )
        OUTPUT.writelines(x_init_list)
        del x_init_list
        
#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing constraint bounds:",
#        start_time = time.clock()
        #
        # "r" lines
        #
        OUTPUT.write( "r\n" )
        # *NOTE: This iteration follows the assignment of the ampl_con_id
        OUTPUT.writelines(constraint_bounds_dict[con_ID] for con_ID in itertools.chain(nonlin_con_order_list, lin_con_order_list))

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing variable bounds:",
#        start_time = time.clock()
        #
        # "b" lines
        #
        OUTPUT.write( "b\n" )
        OUTPUT.writelines(var_bound_list)
        del var_bound_list
        
#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing k's:",
#        start_time = time.clock()        

        #
        # "k" lines
        #
        ktot = 0
        n1 = len(full_var_list) - 1
        OUTPUT.write( "k%d\n"%(n1) )
        ktot = 0
        for i in xrange(n1):
            ktot += cu[i]
            OUTPUT.write( "%d\n"%(ktot) )
        del cu

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing Jacobian's:",
#        start_time= time.clock()

        #
        # "J" lines
        # 
        for nc, con_ID in enumerate(itertools.chain(nonlin_con_order_list,lin_con_order_list)):
            con_data, wrapped_ampl_repn = Constraints_dict[con_ID]
            con_vars = set(wrapped_ampl_repn._nonlinear_vars)
            nl_con_vars = sorted(con_vars.difference(wrapped_ampl_repn._linear_vars))
            con_vars.update(wrapped_ampl_repn._linear_vars)
            linear_dict = dict((var_ID, coef) for var_ID, coef in zip(wrapped_ampl_repn._linear_vars, wrapped_ampl_repn.repn._linear_terms_coef))
            ### GAH: This replaces the checks for constraint.trivial,
            ###      and ampl_repn.fixed. In these cases no active variables
            ###      will exist inside the ampl_repn. The purpose here is to have
            ###      constraints that become trivial due to fixed variables still
            ###      be written in the "C" section as a feasibility check for the fixed
            ###      variable values.
            if len(con_vars) > 0:
                OUTPUT.write( "J%d %d\n"%(nc, len(con_vars)) )
                OUTPUT.writelines( "{0} {1!r}\n".format(self_ampl_var_id[con_var], linear_dict[con_var]) for con_var in sorted(linear_dict.keys()) )
                OUTPUT.writelines( "%d 0\n"%(self_ampl_var_id[con_var]) for con_var in nl_con_vars )

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing objective gradient:",
#        start_time = time.clock()
        #
        # "G" lines
        #
        for obj_ID, (obj, wrapped_ampl_repn) in iteritems(Objectives_dict):
        
            grad_entries = {}
            for idx, obj_var in enumerate(wrapped_ampl_repn._linear_vars):
                grad_entries[self_ampl_var_id[obj_var]] = wrapped_ampl_repn.repn._linear_terms_coef[idx]
            for obj_var in wrapped_ampl_repn._nonlinear_vars:
                if obj_var not in wrapped_ampl_repn._linear_vars:
                    grad_entries[self_ampl_var_id[obj_var]] = 0
            len_ge = len(grad_entries)
            if len_ge > 0:
                OUTPUT.write( "G%d %d\n"%(self_ampl_obj_id[obj_ID], len_ge) )
                for var_ID in sorted(grad_entries.keys()):
                    OUTPUT.write( "{0} {1!r}\n".format(var_ID, grad_entries[var_ID]) )

#        print (end_time - start_time)
#        end_overall_time = time.clock()
#        print "Total time:",end_overall_time-start_overall_time

        return symbol_map


# Switch from Python to C generate_ampl_repn function when possible
#try:
#    py_generate_ampl_repn = generate_ampl_repn
#    from cAmpl import generate_ampl_repn
#except ImportError:
#    del py_generate_ampl_repn

# Alternative: import C implementation under another name for testing
#from cAmpl import generate_ampl_repn as cgar
#__all__.append('cgar')
