from coopr.pyomo import *
from pyutilib.component.core import implements, Plugin, Interface
from coopr.pyomo.base import IModelTransformation

__all__ = ["Transformation"]

class Transformation(Plugin):
    """
    Base class for all model transformations.
    """

    implements(IModelTransformation)

    def __init__(self, **kwds):
        kwds["name"] = kwds.get("name", "transformation")
        super(Transformation, self).__init__(**kwds)

    def __call__(self, model, **kwds):
        """ Apply the transformation """

    def apply(self, model, **kwds):
        """ Alias for __call__ """
