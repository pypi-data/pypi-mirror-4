#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['IPyomoExpression', 'ExpressionFactory', 'ExpressionRegistration',
        'IPyomoSet', 'IModelComponent',
        'ModelComponentFactory',
        'register_component',
        'IPyomoPresolver', 'IPyomoPresolveAction',
        'DataManagerFactory',
        'IParamRepresentation',
        'ParamRepresentationFactory',
        'IModelTransformation',
        'apply_transformation',
        'IPyomoScriptPreprocess',
        'IPyomoScriptCreateModel',
        'IPyomoScriptCreateModelData',
        'IPyomoScriptModifyInstance',
        'IPyomoScriptPrintModel',
        'IPyomoScriptPrintInstance',
        'IPyomoScriptSaveInstance',
        'IPyomoScriptPrintResults',
        'IPyomoScriptSaveResults',
        'IPyomoScriptPostprocess'
        ]

from pyutilib.component.core import *


PluginGlobals.push_env('coopr.pyomo.scripting')

class IPyomoScriptPreprocess(Interface):

    def apply(self, **kwds):
        """Apply preprocessing step in the Pyomo script"""

class IPyomoScriptCreateModel(Interface):

    def apply(self, **kwds):
        """Apply model creation step in the Pyomo script"""

class IPyomoScriptModifyInstance(Interface):

    def apply(self, **kwds):
        """Modify and return the model instance"""

class IPyomoScriptCreateModelData(Interface):

    def apply(self, **kwds):
        """Apply model data creation step in the Pyomo script"""

class IPyomoScriptPrintModel(Interface):

    def apply(self, **kwds):
        """Apply model printing step in the Pyomo script"""

class IPyomoScriptPrintInstance(Interface):

    def apply(self, **kwds):
        """Apply instance printing step in the Pyomo script"""

class IPyomoScriptSaveInstance(Interface):

    def apply(self, **kwds):
        """Apply instance saving step in the Pyomo script"""

class IPyomoScriptPrintResults(Interface):

    def apply(self, **kwds):
        """Apply results printing step in the Pyomo script"""

class IPyomoScriptSaveResults(Interface):

    def apply(self, **kwds):
        """Apply results saving step in the Pyomo script"""

class IPyomoScriptPostprocess(Interface):

    def apply(self, **kwds):
        """Apply postprocessing step in the Pyomo script"""

PluginGlobals.pop_env()

class IPyomoPresolver(Interface):

    def get_actions(self):
        """Return a list of presolve actions, in the order in which
        they will be applied."""

    def activate_action(self, action):
        """Activate an action, but leave its default rank"""

    def deactivate_action(self, action):
        """Deactivate an action"""

    def set_actions(self, actions):
        """Set presolve action list"""

    def presolve(self, instance):
        """Apply the presolve actions to this instance, and return the
        revised instance"""


class IPyomoPresolveAction(Interface):

    def presolve(self, instance):
        """Apply the presolve action to this instance, and return the
        revised instance"""

    def rank(self):
        """Return an integer that is used to automatically order presolve actions,
        from low to high rank."""


class IPyomoExpression(Interface):

    def type(self):
        """Return the type of expression"""

    def create(self, args):
        """Create an instance of this expression type"""


class ExpressionRegistration(Plugin):

    implements(IPyomoExpression, service=False)

    def __init__(self, type, cls, swap=False):
        self._type = type
        self._cls = cls
        self._swap = swap

    def type(self):
        return self._type

    def create(self, args):
        if self._swap:
            args = list(args)
            args.reverse()
        return self._cls(args)

def ExpressionFactory(name=None, args=[]):
    ep = ExpressionFactory.ep
    if name is None:
        return map(lambda x:x.name, ep())
    return ep.service(name).create(args)
ExpressionFactory.ep = ExtensionPoint(IPyomoExpression)



class IPyomoSet(Interface):
    pass


class IModelComponent(Interface):
    pass

ModelComponentFactory = CreatePluginFactory(IModelComponent)

def register_component(cls, description):
    class TMP(Plugin):
        implements(IModelComponent, service=False)
        alias(cls.__name__, description)
        component = cls


class IDataManager(Interface):

    def initialize(self, filename, **kwds):
        """ Prepare to read a data file. """
        pass

    def add_options(self, **kwds):
        """ Add options """
        pass

    def open(self):
        """ Open the data file. """
        pass

    def close(self):
        """ Close the data file. """
        pass

    def read(self):
        """ Read the data file. """
        pass

    def process(self, model, data, default):
        """ Process the data. """
        pass

    def clear(self):
        """ Reset Plugin. """
        pass

DataManagerFactory = CreatePluginFactory(IDataManager)


class IModelTransformation(Interface):

    def apply(self, model, **kwds):
        """Apply a model transformation and return a new model instance"""

    def __call__(self, model, **kwds):
        """Use this plugin instance as a functor to apply a transformation"""
        return self.apply(model, **kwds)


def apply_transformation(*args, **kwds):
    ep = ExtensionPoint(IModelTransformation)
    if len(args) is 0:
        return map(lambda x:x.name, ep())
    service = ep.service(args[0])
    if len(args) == 1 or service is None:
        return service
    tmp=(args[1],)
    return service.apply(*tmp, **kwds)


class IParamRepresentation(Interface):
    pass

ParamRepresentationFactory = CreatePluginFactory(IParamRepresentation)
