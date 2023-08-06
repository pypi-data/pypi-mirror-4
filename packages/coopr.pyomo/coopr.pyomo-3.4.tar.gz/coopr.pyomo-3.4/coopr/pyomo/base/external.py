#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import types
from coopr.pyomo.base.numvalue import as_numeric
from coopr.pyomo.base.component import Component
from coopr.pyomo.base.expr import Expression, clone_expression, _ExternalFunctionExpression

__all__  = ( 'ExternalFunction', )


class ExternalFunction(Component):
    def __init__(self, **kwds):
        self._library = kwds.pop('library', None)
        self._function = kwds.pop('function', None)
        kwds.setdefault('ctype', ExternalFunction)
        Component.__init__(self, **kwds)
        self._constructed = True
        ### HACK ###
        # FIXME: We must declare an _index attribute because
        # block._add_temporary_set assumes ALL components define an
        # index.  Sigh.
        self._index = None

    def __call__(self, *args):
        idxs = range(len(args))
        idxs.reverse()
        for i in idxs:
            if type(args[i]) is types.GeneratorType:
                args = args[:i] + tuple(args[i]) + args[i+1:]
        return _ExternalFunctionExpression( self, tuple(
                _external_fcn__clone_if_needed(x) if isinstance(x, Expression)
                else x if isinstance(x, basestring)
                else as_numeric(x)
                for x in args ) )

    def cname(self, fully_qualified=False, name_buffer=None):
        if self.name:
            return super(ExternalFunction, self).cname(
                fully_qualified, name_buffer )
        else:
            return str(self._library) + ":" + str(self._function)
        
