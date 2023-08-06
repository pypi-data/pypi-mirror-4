#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['SOSConstraint']

import sys
import logging
import weakref

from coopr.pyomo.base.constraint import _ConstraintData
from coopr.pyomo.base.component import register_component
from coopr.pyomo.base.indexed_component import IndexedComponent
from coopr.pyomo.base.misc import create_name, apply_indexed_rule


logger = logging.getLogger('coopr.pyomo')



class SOSConstraint(IndexedComponent):
    """
    Represents an SOS-n constraint.

    Usage:
    model.C1 = SOSConstraint(
                             [...],
                             var=VAR,
                             [set=SET OR index=SET],
                             [sos=N OR level=N]
                             )
        [...] Any number of sets used to index SET
        VAR   The set of variables making up the SOS. Indexed by SET.
        SET   The set used to index VAR. SET is optionally indexed by
              the [...] sets. If SET is not specified, VAR is indexed
              over the set(s) it was defined with.
        N     This constraint is an SOS-N constraint. Defaults to 1.

    Example:

      model = AbstractModel()
      model.A = Set()
      model.B = Set(A)
      model.X = Set(B)

      model.C1 = SOSConstraint(model.A, var=model.X, set=model.B, sos=1)

    This constraint actually creates one SOS-1 constraint for each
    element of model.A (e.g., if |A| == N, there are N constraints).
    In each constraint, model.X is indexed by the elements of
    model.D[a], where 'a' is the current index of model.A.

      model = AbstractModel()
      model.A = Set()
      model.X = Var(model.A)

      model.C2 = SOSConstraint(var=model.X, sos=2)

    This produces exactly one SOS-2 constraint using all the variables
    in model.X.
    """


    def __init__(self, *args, **kwargs):
        name = kwargs.get('name', 'unknown')

        # Get the 'var' parameter
        sosVars = kwargs.pop('var', None)

        # Get the 'set' or 'index' parameters
        if 'set' in kwargs and 'index' in kwargs:
            raise TypeError("Specify only one of 'set' and 'index' -- " \
                  "they are equivalent parameters")
        sosSet = kwargs.pop('set', None)
        sosSet = kwargs.pop('index', sosSet)

        # Get the 'sos' or 'level' parameters
        if 'sos' in kwargs and 'index' in kwargs:
            raise TypeError("Specify only one of 'sos' and 'level' -- " \
                  "they are equivalent parameters")
        sosLevel = kwargs.pop('sos', None)
        sosLevel = kwargs.pop('level', sosLevel)

        # Make sure sosLevel has been set
        if sosLevel is None:
            raise TypeError("SOSConstraint() requires that either the " \
                  "'sos' or 'level' keyword arguments be set to indicate " \
                  "the type of SOS.")

        # Make sure we have a variable
        if sosVars is None:
            raise TypeError("SOSConstraint() requires the 'var' keyword " \
                  "be specified")

        # Find the default sets for sosVars if sosSets is None
        if sosSet is None:
            sosSet = sosVars.index_set()

        # Construct parents
        kwargs['ctype'] = kwargs.get('ctype', SOSConstraint)
        IndexedComponent.__init__(self, *args, **kwargs)

        # Set member attributes
        self._sosVars = sosVars
        self._sosSet = sosSet
        self._sosLevel = sosLevel

        # TODO figure out why exactly the code expects this to be defined
        # likely due to Numericvalue
        self.domain = None

        # TODO should variables be ordered?

    def construct(self, *args, **kwds):
        """
        A quick hack to call add after data has been loaded. construct
        doesn't actually need to do anything.
        """
        if self._constructed is True:
            return
        self._constructed = True
        self.add()

    def add(self, *args):
        """
        Mimics Constraint.add, but is only used to alert preprocessors
        to the existence of the SOS variables.

        Ignores all arguments passed to it.
        """

        # self._data is a _ConstraintData object, which has a member
        # .body.  .body needs to have a 3-tuple of expressions
        # containing the variables that are referenced by this
        # constraint. We only use one index, None. I have no
        # particular reason to use None, it just seems consistent with
        # what Constraint objects do.

        # For simplicity, we sum over the variables.

        vars = self.sos_vars()

        expr = sum(vars[i] for i in vars._index)

        self._data[None] = _ConstraintData(self)
        self._data[None].body = expr

    def sos_level(self):
        """ Return n, where this class is an SOS-n constraint """
        return self._sosLevel

    def sos_vars(self):
        """ Return the variables in the SOS """
        return self._sosVars

    def sos_set(self):
        """ Return the set used to index the variables """
        return self._sosSet

    def sos_set_set(self):
        """ Return the sets used to index the sets indexing the variables """
        return self._index
    
    def reset(self):            #pragma:nocover
        pass                    #pragma:nocover

    def pprint(self, ostream=None, verbose=False):
        if ostream is None:
            ostream = sys.stdout
        ostream.write("  "+self.name+" :")
        if not self.doc is None:
            ostream.write(self.doc+'\n')
            ostream.write("  ")
        ostream.write("Type="+str(self._sosLevel)+'\n')
        ostream.write("\tVariable: "+self._sosVars.name+'\n')
        ostream.write("\tIndices: ")
        for i in self._sosSet:
            ostream.write(str(i)+" ")
        ostream.write("\n")


register_component(SOSConstraint, "SOS constraint expressions in a model.")

