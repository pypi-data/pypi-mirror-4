from coopr.pyomo import *
from coopr.pyomo.transform import Transformation

__all__ = ["LinearTransformation"]

class LinearTransformation(Transformation):
    """ Base class for all linear model transformations. """

    def __init__(self, **kwds):
        kwds["name"] = kwds.get("name", "linear_transform")
        super(LinearTransformation, self).__init__(**kwds)
