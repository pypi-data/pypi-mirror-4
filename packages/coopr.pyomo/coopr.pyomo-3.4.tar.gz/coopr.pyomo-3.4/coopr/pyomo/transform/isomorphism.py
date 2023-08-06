from coopr.pyomo import *
from pyutilib.component.core import implements, Plugin, Interface
from coopr.pyomo.base import IModelTransformation, Var

__all__ = ["IIsomophicTransformation", "IsomorphicTransormation"]

class IIsomorphicTransformation(Interface):


    def __call__(self, model, **kwds):
        """
        Apply the transformation. Returns a (model, variable_mapping) tuple.
        """

    def apply(self, model, **kwds):
        """
        Apply the transformation. Returns a (model, variable_mapping) tuple.
        """

class IsomorphicTransformation(Plugin):
    """
    This class represents transformations that create equivalent
    models. The values of original variables can be recovered after
    solving a problem created by a series of isomorphic
    transformations via a TransformTracker object.
    """

    implements(IIsomorphicTransformation)

    def __init__(self, **kwds):
        kwds["name"] = kwds.pop("name", "isomorphic_transform")
        Plugin.__init__(self, **kwds)

class IdentityTransformation(IsomorphicTransformation):
    """
    Returns a clone of the model.
    """

    def __call__(self, model, **kwds):
        m = model.clone()

        # Create the variable mapping
        varmap = {}

        for c in model.active_components():
            if isinstance(c, Var):
                pass

    def apply(self, model, **kwds):
        return self.__call__(model, **kwds)
