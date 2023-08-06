#
# Unit Tests for nontrivial Bounds (_SumExpression, _ProductExpression)
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
currdir = dirname(abspath(__file__))+os.sep

import pyutilib.th as unittest
from coopr.pyomo import *
from nose.tools import nottest

class Test(unittest.TestCase):

    #Test constraint bounds
    def test_constr_lower(self):
        self.model = AbstractModel()
        self.model.A = Param(default=2.0, mutable=True)
        self.model.B = Param(default=1.5, mutable=True)
        self.model.C = Param(default=2.5, mutable=True)
        self.model.X = Var()

        def constr_rule(model):
            return (self.model.A*(self.model.B+self.model.C),self.model.X)
        self.model.constr = Constraint(rule=constr_rule)

        self.instance = self.model.create()
        self.instance.pprint()
        self.assertEqual(self.instance.constr.lower(),8.0)

    def test_constr_upper(self):
        self.model = AbstractModel()
        self.model.A = Param(default=2.0, mutable=True)
        self.model.B = Param(default=1.5, mutable=True)
        self.model.C = Param(default=2.5, mutable=True)
        self.model.X = Var()

        def constr_rule(model):
            return (self.model.X,self.model.A*(self.model.B+self.model.C))
        self.model.constr = Constraint(rule=constr_rule)

        self.instance = self.model.create()

        self.assertEqual(self.instance.constr.upper(),8.0)

    def test_constr_both(self):
        self.model = AbstractModel()
        self.model.A = Param(default=2.0, mutable=True)
        self.model.B = Param(default=1.5, mutable=True)
        self.model.C = Param(default=2.5, mutable=True)
        self.model.X = Var()

        def constr_rule(model):
            return (self.model.A*(self.model.B-self.model.C),self.model.X,self.model.A*(self.model.B+self.model.C))
        self.model.constr = Constraint(rule=constr_rule)

        self.instance = self.model.create()

        self.assertEqual(self.instance.constr.lower(),-2.0)
        self.assertEqual(self.instance.constr.upper(),8.0)


    #Test variable bounds
    #JPW: Disabled until we are convinced that we want to support complex parametric expressions for variable bounds.
    def test_var_bounds(self):
        self.model = AbstractModel()
        self.model.A = Param(default=2.0, mutable=True)
        self.model.B = Param(default=1.5, mutable=True)
        self.model.C = Param(default=2.5, mutable=True)

        def X_bounds_rule(model):
            return (self.model.A*(self.model.B-self.model.C),self.model.A*(self.model.B+self.model.C))
        self.model.X = Var(bounds=X_bounds_rule)

        self.instance = self.model.create()

        self.assertEqual(self.instance.X.lb(),-2.0)
        self.assertEqual(self.instance.X.ub(),8.0)
   

if __name__ == "__main__":
    unittest.main()

