from coopr.pyomo import *
from coopr.pyomo.transform import Transformation

__all__ = ["AbstractTransformation"]

class AbstractTransformation(Transformation):
    """
    Base class for all model transformations that produce abstract
    models.
    """

    def __init__(self, **kwds):
        kwds["name"] = kwds.get("name", "concrete_transformation")
        super(AbstractTransformation, self).__init__(**kwds)
