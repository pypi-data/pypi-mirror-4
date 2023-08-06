#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['BuildCheck']

import logging
import types

from coopr.pyomo.base.component import register_component
from coopr.pyomo.base.indexed_component import IndexedComponent
from coopr.pyomo.base.misc import apply_indexed_rule

logger = logging.getLogger('coopr.pyomo')


class BuildCheck(IndexedComponent):
    """A build check, which executes a rule for all valid indices.

    Constructor arguments:
        rule         The rule that is executed for every indice.

    Private class attributes:
        _rule       The rule that is executed for every indice.
    """

    def __init__(self, *args, **kwd):
        self._rule = kwd.pop('rule', None)
        kwd['ctype'] = BuildCheck
        IndexedComponent.__init__(self, *args, **kwd)
        #
        if not type(self._rule) is types.FunctionType:
            raise ValueError("BuildAction must have an 'rule' option specified whose value is a function")

    def construct(self, data=None):
        """ Apply the rule to construct values in this set """
        if __debug__:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing Check, name="+self.name)
        #
        if self._constructed:
            return
        self._constructed=True
        #
        if None in self._index:
            # Singleton component
            res = self._rule(self._parent())
            if not res:
                raise ValueError("BuildCheck %r identified error" % self.name)
        else:
            # Indexed component
            for index in self._index:
                res = apply_indexed_rule(self, self._rule, self._parent(), index)
                if not res:
                    raise ValueError("BuildCheck %r identified error with index %r" % (self.name, str(index)))

register_component(BuildCheck, "This component is used to perform a test during the model construction process.  The action rule is applied to every index value, and if the function returns False an exception is raised.")
