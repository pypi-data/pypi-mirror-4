#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['BuildAction']

import logging
import types

from coopr.pyomo.base.component import register_component
from coopr.pyomo.base.indexed_component import IndexedComponent
from coopr.pyomo.base.misc import apply_indexed_rule

logger = logging.getLogger('coopr.pyomo')


class BuildAction(IndexedComponent):
    """A build action, which executes a rule for all valid indices.

    Constructor arguments:
        rule        The rule that is executed for every indice.

    Private class attributes:
        _rule       The rule that is executed for every indice.
    """

    def __init__(self, *args, **kwd):
        self._rule = kwd.pop('rule', None)
        kwd['ctype'] = BuildAction
        IndexedComponent.__init__(self, *args, **kwd)
        #
        if not type(self._rule) is types.FunctionType:
            raise ValueError("BuildAction must have an 'rule' option specified whose value is a function")

    def construct(self, data=None):
        """ Apply the rule to construct values in this set """
        if __debug__:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing Action, name="+self.name)
        #
        if self._constructed:
            return
        self._constructed=True
        #
        if None in self._index:
            # Singleton component
            self._rule(self._parent())
        else:
            # Indexed component
            for index in self._index:
                apply_indexed_rule(self, self._rule, self._parent(), index)


register_component(BuildAction, "This component is used to inject arbitrary actions into the model construction process.  The action rule is applied to every index value.")
