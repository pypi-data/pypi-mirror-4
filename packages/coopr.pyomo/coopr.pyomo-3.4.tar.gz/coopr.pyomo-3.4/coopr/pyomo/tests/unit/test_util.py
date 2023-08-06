#
# Unit Tests for Utility Functions
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
currdir = dirname(abspath(__file__))+os.sep

import pyutilib.th as unittest
from coopr.pyomo import *
from nose.tools import nottest
import pickle


def obj_rule(model):
    return sum(model.x[a] + model.y[a] for a in model.A)
def constr_rule(model,a):
    return model.x[a] >= model.y[a]

class Test(unittest.TestCase):

    def test_expr1(self):
        model = AbstractModel()
        model.A = Set(initialize=[1,2,3])
        model.B = Param(model.A,initialize={1:100,2:200,3:300}, mutable=True)
        model.x = Var(model.A)
        model.y = Var(model.A)
        instance=model.create()
        expr = dot_product(instance.x,instance.B,instance.y)
        OUTPUT=open(currdir+"test_expr1.out","w")
        expr.pprint(ostream=OUTPUT)
        OUTPUT.close()
        self.assertFileEqualsBaseline(currdir+"test_expr1.out",currdir+"test_expr1.txt")

    def test_expr2(self):
        model = AbstractModel()
        model.A = Set(initialize=[1,2,3])
        model.B = Param(model.A,initialize={1:100,2:200,3:300}, mutable=True)
        model.x = Var(model.A)
        model.y = Var(model.A)
        instance=model.create()
        expr = dot_product(instance.x,instance.B,instance.y, index=[1,3])
        OUTPUT=open(currdir+"test_expr2.out","w")
        expr.pprint(ostream=OUTPUT)
        OUTPUT.close()
        self.assertFileEqualsBaseline(currdir+"test_expr2.out",currdir+"test_expr2.txt")

    def test_expr3(self):
        model = AbstractModel()
        model.A = Set(initialize=[1,2,3])
        model.B = Param(model.A,initialize={1:100,2:200,3:300}, mutable=True)
        model.x = Var(model.A)
        model.y = Var(model.A)
        instance=model.create()
        expr = dot_product(instance.x,instance.B,denom=instance.y, index=[1,3])
        OUTPUT=open(currdir+"test_expr3.out","w")
        expr.pprint(ostream=OUTPUT)
        OUTPUT.close()
        self.assertFileEqualsBaseline(currdir+"test_expr3.out",currdir+"test_expr3.txt")

    def test_expr4(self):
        model = AbstractModel()
        model.A = Set(initialize=[1,2,3])
        model.B = Param(model.A,initialize={1:100,2:200,3:300}, mutable=True)
        model.x = Var(model.A)
        model.y = Var(model.A)
        instance=model.create()
        expr = dot_product(denom=[instance.y,instance.x])
        OUTPUT=open(currdir+"test_expr4.out","w")
        expr.pprint(ostream=OUTPUT)
        OUTPUT.close()
        self.assertFileEqualsBaseline(currdir+"test_expr4.out",currdir+"test_expr4.txt")

    def test_expr5(self):
        model = ConcreteModel()
        model.A = Set(initialize=[1,2,3], doc='set A')
        model.B = Param(model.A, initialize={1:100,2:200,3:300}, doc='param B', mutable=True)
        model.C = Param(initialize=3, doc='param C', mutable=True)
        model.x = Var(model.A, doc='var x')
        model.y = Var(doc='var y')
        model.o = Objective(expr=model.y, doc='obj o')
        model.c1 = Constraint(expr=model.x[1] >= 0, doc='con c1')
        def c2_rule(model, a):
            return model.B[a] * model.x[a] <= 1
        model.c2 = Constraint(model.A, doc='con c2')
        model.c3 = ConstraintList(doc='con c3')
        model.c3.add(model.y <= 0)
        #
        instance=model.create()
        OUTPUT=open(currdir+"test_expr5.out","w")
        instance.pprint(ostream=OUTPUT)
        OUTPUT.close()
        self.assertFileEqualsBaseline(currdir+"test_expr5.out",currdir+"test_expr5.txt")

if __name__ == "__main__":
    unittest.main()
