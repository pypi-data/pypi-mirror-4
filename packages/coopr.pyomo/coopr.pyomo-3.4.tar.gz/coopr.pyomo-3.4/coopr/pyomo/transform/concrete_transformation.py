from coopr.pyomo import *
from coopr.pyomo.transform import Transformation

__all__ = ["ConcreteTransformation"]

class ConcreteTransformation(Transformation):
    """
    Base class for all model transformations that produce concrete
    models.
    """

    def __init__(self, **kwds):
        kwds["name"] = kwds.get("name", "concrete_transformation")
        super(ConcreteTransformation, self).__init__(**kwds)
