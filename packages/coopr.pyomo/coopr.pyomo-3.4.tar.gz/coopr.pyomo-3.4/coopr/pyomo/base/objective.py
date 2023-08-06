#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Objective', 'simple_objective_rule', '_ObjectiveData', 'minimize', 'maximize']

import sys
import logging
import weakref

import pyutilib.math
import pyutilib.misc

from coopr.pyomo.base.numvalue import NumericValue, as_numeric, value, native_numeric_types
from coopr.pyomo.base.expr import Expression
from coopr.pyomo.base.component import Component, ComponentData, register_component
from coopr.pyomo.base.indexed_component import IndexedComponent
from coopr.pyomo.base.misc import create_name, apply_indexed_rule
from coopr.pyomo.base.sets import Set
from coopr.pyomo.base.var import _VarData
from coopr.pyomo.base.set_types import Reals

#import time
#from coopr.pyomo.base.expr import generate_expression, generate_relational_expression
#from coopr.pyomo.base.intrinsic_functions import generate_intrinsic_function_expression

logger = logging.getLogger('coopr.pyomo')

minimize=1
maximize=-1


def simple_objective_rule( fn ):
    """
    This is a decorator that translates None into Constraint.Skip.
    This supports a simpler syntax in objective rules, though these
    can be more difficult to debug when errors occur.

    Example use:

    @simple_objective_rule
    def O_rule(model, i, j):
        ...
    """

    def wrapper_function ( *args, **kwargs ):
        value = fn( *args, **kwargs )
        if value is None:
            return Objective.Skip
        return value
    return wrapper_function


class _ObjectiveData(ComponentData, NumericValue):
    """
    This class defines the data for a single objective.

    Note that this is a subclass of NumericValue to allow
    objectives to be used as part of expressions.

    Constructor arguments:
        expr            The expression for this objective.
        name            The name of this objective.
        component       The Objective object that owns this data.

    Public class attributes:
        active          A boolean that is true if this objective is active in the model.
        component       The objective component.
        domain          A domain object that restricts possible values for this objective.
        expr            The Pyomo expression for this objective
        id              An integer value that defines 
        name            The name of this objective
        value           The numeric value of this objective

    Private class attributes:
        _repn           TBD
    """

    __pickle_slots__ = ( 'value', 'expr', 'id', 'active')
    __slots__ = __pickle_slots__ + ( '__weakref__', )

    def __init__(self, component, expr):
        ComponentData.__init__(self, component)
        self.value = None
        #
        self.active = True
        self.expr = expr
        self.id = -1

    def __getstate__(self):
        # This method is required because this class uses slots.
        state = super(_ObjectiveData, self).__getstate__()
        for i in _ObjectiveData.__pickle_slots__:
            state[i] = getattr(self,i)
        return state

    # Note: because NONE of the slots on this class need to be edited,
    # we don't need to implement a specialized __setstate__ method, and
    # can quietly rely on the super() class's implementation.
    # def __setstate__(self, state):
    #     pass

    def __call__(self, exception=True):
        """
        Compute the value of this objective.

        This method does not simply return self.value because that data value may be out of date
        w.r.t. the value of decision variables.
        """
        if self.expr is None:
            return None
        return self.expr()

    def polynomial_degree(self):
        """
        Return the polynomial degree of the objective expression.
        """
        if self.expr is None:
            return None
        return self.expr.polynomial_degree()

    def activate(self):
        """
        Activate this objective.
        """
        self.active=True

    def deactivate(self):
        """
        Deactivate this objective.
        """
        self.active=False

    # GAH: Should we actually move the .sense attribute down to
    #      _ObjectiveData?
    def is_minimizing ( self ):
        """Return true if this is a minimization objective"""
        return self.component().sense == minimize


class Objective(IndexedComponent):
    """
    This modeling component defines an objective expression.

    Note that this is a subclass of NumericValue to allow
    objectives to be used as part of expressions.

    Constructor arguments:
        expr            A Pyomo expression for this objective
        doc             A text string describing this component
        name            A name for this component
        noruleinit      Indicate that its OK that no initialization is
                            specified
        rule            A function that is used to construct objective
                            expressions
        sense           Indicate whether minimizing or maximizing
        
    Public class attributes:
        active          A boolean that is true if this component will be 
                            used to construct a model instance
        doc             A text string describing this component
        domain          A domain object that restricts possible values for this object.
        expr*           Not defined
        id*             Not defined
        index*          Not defined
        name            A name for this object.
        rule            The rule used to initialize the objective(s)
        sense           The objective sense
        trivial         A boolean if all objective indices have trivial expressions
        value           The numeric value of this object.

    Private class attributes:
        _constructed    A boolean that is true if this component has been
                            constructed
        _data           A dictionary from the index set to component data objects
        _index          The set of valid indices
        _index_set      A tuple of set objects that represents the index set
        _model          A weakref to the model that owns this component
        _ndim           The dimension of the index set
        _no_rule_init   A boolean that indicates if an initialization rule is needed
        _parent         A weakref to the parent block that owns this component
        _type           The class type for the derived subclass
    """

    Skip        = (1000,)
    NoObjective = (1000,)

    def __new__(cls, *args, **kwds):
        if cls != Objective:
            return super(Objective, cls).__new__(cls)
        if args == ():
            return _ObjectiveElement.__new__(_ObjectiveElement)
        else:
            return _ObjectiveArray.__new__(_ObjectiveArray)

    def __init__(self, *args, **kwargs):
        # Initialize values defined in NumericValue base class
        self.domain = None
        self.value = None
        #
        self.sense = kwargs.pop('sense', minimize )
        tmprule  = kwargs.pop('rule', None )
        self.rule  = kwargs.pop('expr', tmprule )
        self._no_rule_init = kwargs.pop('noruleinit', None )
        self.trivial = False
        self._constructed = False
        #
        kwargs.setdefault('ctype', Objective)
        IndexedComponent.__init__(self, *args, **kwargs)

    def __getstate__(self):
        """
        This method is required because this class uses slots.  Call base class __getstate__
        methods since this class does not define additional slots.
        """
        return super(Objective, self).__getstate__()

    def __setstate__(self, state):
        """
        This method is required because this class uses slots.  Call base class __setstate__
        methods since this class does not define additional slots.
        """
        IndexedComponent.__setstate__(self, state)
 
    def is_minimizing ( self ):
        """Return true if this is a minimization objective"""
        return self.sense == minimize

    def construct(self, data=None):
        """Construct the expression(s) for this objective."""
        if __debug__:
            logger.debug("Constructing objective %s", self.name)
        if (self._no_rule_init is not None) and (self.rule is not None):
            msg = 'WARNING: noruleinit keyword is being used in conjunction ' \
                  "with rule keyword for objective '%s'; defaulting to "      \
                  'rule-based construction'
            print(msg % self.name)
        if self.rule is None:
            if self._no_rule_init is None:
                msg = 'WARNING: No construction rule or expression specified ' \
                      "for objective '%s'"
                print(msg % self.name)
            return
        if self._constructed:
            return
        self._constructed=True
        # NumbericValue -> single Var, single Param, Expression
        if isinstance(self.rule,NumericValue):
            if None in self._index or len(self._index) == 0 or self._index[None] is None:
                self._data[None].expr = self.rule
            else:
                msg = 'Cannot define multiple indices in an objective with a' \
                      'single expression'
                raise IndexError(msg)
        # A very uncommon case where the objective is simply a number
        # Number -> int, long, float
        elif self.rule.__class__ in native_numeric_types:
            if None in self._index or len(self._index) == 0 or self._index[None] is None:
                self._data[None].expr = as_numeric(self.rule)
            else:
                msg = 'Cannot define multiple indices in an objective with a' \
                      'single expression'
                raise IndexError(msg)
        #
        elif self.rule is not None:
            if self._ndim==0:
                tmp = self.rule(self._parent())
                if tmp is None:
                    raise ValueError("Objective rule returned None instead of Objective.Skip")
                if not (tmp.__class__ is tuple and tmp == Objective.Skip):
                    self._data[None].expr = as_numeric(tmp)
            else:
                _name=self.name
                for val in self._index:
                    tmp = apply_indexed_rule(self, self.rule, self._parent(), val)
                    if tmp is None:
                        raise ValueError("Objective rule returned None instead of Objective.Skip")
                    if not (tmp.__class__ is tuple and tmp == Objective.Skip):
                        self._data[val] = _ObjectiveData(self, as_numeric(tmp))
        #
        #if None in self._data:
            #self._data[None].name = self.name
        #print "[%.1f] %s: %d,%d,%d" % \
        #      (time.time(), self.name,
        #       generate_expression.clone_counter,
        #       generate_relational_expression.clone_counter,
        #       generate_intrinsic_function_expression.clone_counter)


    def pprint(self, ostream=None, verbose=False):
        """Print the objective value(s)"""
        if ostream is None:
            ostream = sys.stdout
        ostream.write("   "+self.name+" : ")
        if not self.doc is None:
            ostream.write(self.doc+'\n')
            ostream.write("  ")
        ostream.write("\tSize="+str(len(self._data.keys()))+' ')
        if isinstance(self._index, Set):
            ostream.write("\tIndex= %s\n" % self._index.name)
        else:
            ostream.write(" \n")
        for key in self._data:
            if not self._data[key].expr is None:
                ostream.write("\t")
                self._data[key].expr.pprint(ostream, verbose=verbose)
                ostream.write("\n")

    def display(self, prefix="", ostream=None):
        """Provide a verbose display of this object"""
        if ostream is None:
            ostream = sys.stdout
        ostream.write(prefix+"Objective "+self.name+" : ")
        ostream.write("Size="+str(len(self))+'\n')
        if None in self._data:
            if self._data[None].expr is None:
                val = 'none'
            else:
                val = pyutilib.misc.format_io(self._data[None].expr(exception=False))
            ostream.write('%s  Value=%s\n' % (prefix, val))
        else:
            for key in self._data:
                if not self._data[key].active:
                    continue
                val = self._data[key].expr(exception=False)
                ostream.write(prefix+"  "+str(key)+" : "+str(val)+'\n')


class _ObjectiveElement(Objective, _ObjectiveData):

    def __init__(self, *args, **kwd):
        _ObjectiveData.__init__(self, self, None)
        Objective.__init__(self, *args, **kwd)
        self._data[None] = self

    def __call__(self, exception=True):
        """Compute the value of the objective expression"""
        if self.expr is None:
            return None
        return value(self.expr)

    # Since this class derives from Component and Component.__getstate__
    # just packs up the entire __dict__ into the state dict, there s
    # nothng special that we need to do here.  We will just defer to the
    # super() get/set state.  Since all of our get/set state methods
    # rely on super() to traverse the MRO, this will automatically pick
    # up both the Component and Data base classes.
    #
    #def __getstate__(self):
    #    pass
    #
    #def __setstate__(self, state):
    #    pass

class _ObjectiveArray(Objective):

    def __call__(self, exception=True):
        """Compute the value of the objective body"""
        if exception:
            msg = 'Cannot compute the value of an array of objectives'
            raise ValueError(msg)


register_component(Objective, 'Expressions that are minimized or maximized in a model.')

