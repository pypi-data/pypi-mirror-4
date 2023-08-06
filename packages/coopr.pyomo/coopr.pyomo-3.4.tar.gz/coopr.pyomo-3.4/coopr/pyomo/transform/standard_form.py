from pyutilib.component.core import implements, Plugin, alias

from coopr.pyomo import *
from coopr.pyomo.base import Var
from coopr.pyomo.transform.isomorphic_transformation import IsomorphicTransformation
from coopr.pyomo.transform.nonnegative_transform import *
from coopr.pyomo.transform.equality_transform import *

__all__ = ["StandardForm"]


class StandardForm(IsomorphicTransformation):
    """
    Creates a standard form Pyomo model that is equivalent to another model
    """

    alias("standard_form")

    def __init__(self, **kwds):
        kwds['name'] = "standard_form"
        super(StandardForm, self).__init__(**kwds)

    def __call__(self, model, **kwds):
        """
        Tranform a model to standard form
        """
        return self.apply(model, **kwds)

    def apply(self, model, **kwds):
        """
        Tranform a model to standard form
        """

        # Optional naming schemes to pass to EqualityTransform
        eq_kwds = {}
        eq_kwds["slack_names"] = kwds.pop("slack_names", "auxiliary_slack")
        eq_kwds["excess_names"] = kwds.pop("excess_names", "auxiliary_excess")
        eq_kwds["lb_names"] = kwds.pop("lb_names", "_lower_bound")
        eq_kwds["ub_names"] = kwds.pop("ub_names", "_upper_bound")

        # Optional naming schemes to pass to NonNegativeTransformation
        nn_kwds = {}
        nn_kwds["pos_suffix"] = kwds.pop("pos_suffix", "_plus")
        nn_kwds["neg_suffix"] = kwds.pop("neg_suffix", "_minus")

        nonneg = NonNegativeTransformation()
        equality = EqualityTransform()

        # Since NonNegativeTransform introduces new constraints
        # (that aren't equality constraints) we call it first.
        #
        # EqualityTransform introduces new variables, but they are#
        # constrainted to be nonnegative.
        sf = nonneg(model, **nn_kwds)
        sf = equality(sf, **eq_kwds)

        return sf
