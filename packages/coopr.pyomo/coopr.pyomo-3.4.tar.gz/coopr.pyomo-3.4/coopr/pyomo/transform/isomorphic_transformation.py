from coopr.pyomo import *
from pyutilib.component.core import implements, Plugin, Interface
from coopr.pyomo.transform import Transformation

__all__ = ["IsomorphicTransformation"]

class IsomorphicTransformation(Transformation):
    """
    Base class for 'lossless' transformations for which a bijective
    mapping between optimal variable values and the optimal cost
    exists.
    """

    def __init__(self, **kwds):
        kwds["name"] = kwds.get("name", "isomorphic_transformation")
        super(IsomorphicTransformation, self).__init__(**kwds)
