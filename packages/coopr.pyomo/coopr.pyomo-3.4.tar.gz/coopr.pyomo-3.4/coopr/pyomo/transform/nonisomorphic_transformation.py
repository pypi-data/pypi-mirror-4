from coopr.pyomo import *
from pyutilib.component.core import implements, Plugin, Interface
from coopr.pyomo.transform import Transformation

__all__ = ["NonIsomorphicTransformation"]

class NonIsomorphicTransformation(Transformation):
    """
    Base class for 'lossy' transformations for which a bijective
    mapping between optimal variable values and the optimal cost does
    not  exist.
    """

    def __init__(self, **kwds):
        kwds["name"] = kwds.get("name", "isomorphic_transformation")
        super(IsomorphicTransformation, self).__init__(**kwds)
