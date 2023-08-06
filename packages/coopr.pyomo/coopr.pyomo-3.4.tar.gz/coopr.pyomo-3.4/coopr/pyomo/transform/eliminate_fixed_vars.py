#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import pyutilib.component.core
from coopr.pyomo.base import IModelTransformation
from coopr.pyomo import Constraint, Objective, NumericConstant, Expression
from coopr.pyomo.base.var import Var, _VarData
from coopr.pyomo.base.util import xsequence


class EliminateFixedVars(pyutilib.component.core.SingletonPlugin):
    """
    This plugin relaxes integrality in a Pyomo model.
    """

    pyutilib.component.core.implements(IModelTransformation)

    def __init__(self, **kwds):
        kwds['name'] = "eliminate_fixed_vars"
        pyutilib.component.core.Plugin.__init__(self, **kwds)

    def apply(self, model, **kwds):
        #
        # Clone the model
        #
        M = model.clone()
        #
        # Iterate over the expressions in all objectives and constraints, replacing fixed
        # variables with their associated constants.
        #
        for ctype in [Objective, Constraint]:
            for obj in M.components(Objective).values():
                for name in obj:
                    if not obj[name].expr is None:
                        obj[name].expr = self._fix_vars(obj[name].expr, model)
        #
        # Iterate over variables, omitting those that have fixed values
        #
        ctr = 0
        for i in xsequence(M.nvariables()):
            var = M.variable(i)
            del M._var[ i-1 ]
            if var.fixed:
                if var.is_binary():
                    M.statistics.number_of_binary_variables -= 1
                elif var.is_integer():
                    M.statistics.number_of_integer_variables -= 1
                elif var.is_continuous():
                    M.statistics.number_of_continuous_variables -= 1
                M.statistics.number_of_variables -= 1
                del M._label_var_map[ var.label ]
                del var.component()._data[ var.index ]
            else:
                M._var[ ctr ] = var
                var._old_id = var.id
                var.id = ctr
                ctr += 1
        return M

    def _fix_vars(self, expr, model):
        """ Walk through the S-expression, fixing variables. """
        if expr._args is None:
            return expr
        _args = []
        for i in range(len(expr._args)):
            if isinstance(expr._args[i],Expression):
                _args.append( self._fix_vars(expr._args[i], model) )
            elif (isinstance(expr._args[i],Var) or isinstance(expr._args[i],_VarData)) and expr._args[i].fixed:
                if expr._args[i].value != 0.0:
                    _args.append( NumericConstant(None,None,expr._args[i].value) )
            else:
                _args.append( expr._args[i] )
        expr._args = _args
        return expr
