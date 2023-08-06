#
# Unit Tests for Elements of a Model
#
# TestSimpleObj                Class for testing single objective
# TestArrayObj                Class for testing array of objective
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
currdir = dirname(abspath(__file__))+os.sep

from coopr.pyomo.base import IntegerSet
from coopr.pyomo import *
from coopr.opt import *
from coopr.pyomo.base.var import _VarElement
import pyutilib.th as unittest
import pyutilib.services

class PyomoModel(unittest.TestCase):

    def setUp(self):
        self.model = AbstractModel()

    def construct(self,filename):
        self.instance = self.model.create(filename)


class TestSimpleObj(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)

    def tearDown(self):
        pass

    def test_numeric_expr(self):
        """Test expr option with a single numeric constant"""
        model = ConcreteModel()
        model.obj = Objective(expr=0.0)
        instance = model.create()
        self.assertEqual(instance.obj(), 0.0)
        self.assertEqual(value(instance.obj), 0.0)
        self.assertEqual(value(instance.obj._data[None]), 0.0)

    def test_mutable_param_expr(self):
        """Test expr option with a single mutable param"""
        model = ConcreteModel()
        model.p = Param(initialize=1.0,mutable=True)
        model.obj = Objective(expr=model.p)
        instance = model.create()
        self.assertEqual(instance.obj(), 1.0)
        self.assertEqual(value(instance.obj), 1.0)
        self.assertEqual(value(instance.obj._data[None]), 1.0)

    def test_immutable_param_expr(self):
        """Test expr option a single immutable param"""
        model = ConcreteModel()
        model.p = Param(initialize=1.0,mutable=False)
        model.obj = Objective(expr=model.p)
        instance = model.create()
        self.assertEqual(instance.obj(), 1.0)
        self.assertEqual(value(instance.obj), 1.0)
        self.assertEqual(value(instance.obj._data[None]), 1.0)

    def test_var_expr(self):
        """Test expr option with a single var"""
        model = ConcreteModel()
        model.x = Var(initialize=1.0)
        model.obj = Objective(expr=model.x)
        instance = model.create()
        self.assertEqual(instance.obj(), 1.0)
        self.assertEqual(value(instance.obj), 1.0)
        self.assertEqual(value(instance.obj._data[None]), 1.0)

    def test_expr1_option(self):
        """Test expr option"""
        model = ConcreteModel()
        model.x = Var(RangeSet(1,4),initialize=2)
        ans=0
        for i in model.x.keys():
            ans = ans + model.x[i]
        model.obj = Objective(expr=ans)
        instance = model.create()
        self.assertEqual(instance.obj(), 8)
        self.assertEqual(value(instance.obj), 8)
        self.assertEqual(value(instance.obj._data[None]), 8)

    def test_expr2_option(self):
        """Test expr option"""
        model = ConcreteModel()
        model.x = Var(initialize=2)
        model.obj = Objective(expr=model.x)
        instance = model.create()
        instance.x.reset()
        #print 'X',type(instance.obj.rule)
        self.assertEqual(instance.obj(), 2)
        self.assertEqual(value(instance.obj), 2)
        self.assertEqual(value(instance.obj._data[None]), 2)

    def test_rule_option(self):
        """Test rule option"""
        def f(model):
            ans=0
            for i in model.x.keys():
                ans = ans + model.x[i]
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.obj = Objective(rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.obj(), 8)
        self.assertEqual(value(self.instance.obj), 8)
        self.assertEqual(value(self.instance.obj._data[None]), 8)

    def test_arguments(self):
        """Test that arguments notare of type _SetContainer"""
        def rule(model):
            return 1
        try:
            self.model.obj = Objective(self.model, rule=rule)
        except TypeError:
            pass
        else:
            self.fail("Objective should only accept '_SetContainer's")


    def test_sense_option(self):
        """Test sense option"""
        def rule(model):
            return 1.0
        self.model.obj = Objective(sense=maximize, rule=rule)
        self.instance = self.model.create()
        self.assertEqual(self.instance.obj.sense, maximize)
        self.assertEqual(self.instance.obj.is_minimizing(), False)

    def test_dim(self):
        """Test dim method"""
        def rule(model):
            return 1
        self.model.obj = Objective(rule=rule)
        self.instance = self.model.create()
        self.assertEqual(self.instance.obj.dim(),0)

    def test_keys(self):
        """Test keys method"""
        def rule(model):
            return 1
        self.model.obj = Objective(rule=rule)
        self.instance = self.model.create()
        self.assertEqual(list(self.instance.obj.keys()),[None])

    def test_len(self):
        """Test len method"""
        def rule(model):
            return 1.0
        self.model.obj = Objective(rule=rule)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.obj),1)
        """Test rule option"""
        def f(model):
            ans=0
            for i in model.x.keys():
                ans = ans + model.x[i]
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.obj = Objective(rule=f)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.obj),1)


class TestArrayObj(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        self.model.A = Set(initialize=[1,2])

    def tearDown(self):
        pass

    def test_rule_option1(self):
        """Test rule option"""
        def f(model, i):
            ans=0
            for j in model.x.keys():
                ans = ans + model.x[j]
            ans *= i
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.obj = Objective(self.model.A,rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.obj[1](), 8)
        self.assertEqual(self.instance.obj[2](), 16)
        self.assertEqual(value(self.instance.obj[1]), 8)
        self.assertEqual(value(self.instance.obj[2]), 16)

    def test_rule_option2(self):
        """Test rule option"""
        def f(model, i):
            if i == 1:
                return Objective.Skip
            ans=0
            for j in model.x.keys():
                ans = ans + model.x[j]
            ans *= i
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.obj = Objective(self.model.A,rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.obj[2](), 16)
        self.assertEqual(value(self.instance.obj[2]), 16)

    def test_rule_option3(self):
        """Test rule option"""
        @simple_objective_rule
        def f(model, i):
            if i == 1:
                return None
            ans=0
            for j in model.x.keys():
                ans = ans + model.x[j]
            ans *= i
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.obj = Objective(self.model.A,rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.obj[2](), 16)
        self.assertEqual(value(self.instance.obj[2]), 16)

    def test_rule_numeric_expr(self):
        """Test rule option with returns a single numeric constant for the expression"""
        def f(model, i):
            return 1.0
        self.model.obj = Objective(self.model.A,rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.obj[2](), 1.0)
        self.assertEqual(value(self.instance.obj[2]), 1.0)

    def test_rule_immutable_param_expr(self):
        """Test rule option that returns a single immutable param for the expression"""
        def f(model, i):
            return model.p[i]
        self.model.p = Param(RangeSet(1,4),initialize=1.0,mutable=False)
        self.model.x = Var()
        self.model.obj = Objective(self.model.A,rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.obj[2](), 1.0)
        self.assertEqual(value(self.instance.obj[2]), 1.0)

    def test_rule_mutable_param_expr(self):
        """Test rule option that returns a single mutable param for the expression"""
        def f(model, i):
            return model.p[i]
        self.model.r = RangeSet(1,4)
        self.model.p = Param(self.model.r,initialize=1.0,mutable=True)
        self.model.x = Var()
        self.model.obj = Objective(self.model.A,rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.obj[2](), 1.0)
        self.assertEqual(value(self.instance.obj[2]), 1.0)

    def test_rule_var_expr(self):
        """Test rule option that returns a single var for the expression"""
        def f(model, i):
            return model.x[i]
        self.model.r = RangeSet(1,4)
        self.model.x = Var(self.model.r,initialize=1.0)
        self.model.obj = Objective(self.model.A,rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.obj[2](), 1.0)
        self.assertEqual(value(self.instance.obj[2]), 1.0)

    def test_sense_option(self):
        """Test sense option"""
        self.model.obj = Objective(self.model.A,sense=maximize)
        self.instance = self.model.create()
        self.assertEqual(self.instance.obj.sense, maximize)
        self.assertEqual(self.instance.obj.is_minimizing(), False)
        for i in self.instance.obj:
            self.assertEqual(self.instance.obj[i].is_minimizing(), False)

    def test_dim(self):
        """Test dim method"""
        self.model.obj = Objective(self.model.A)
        self.instance = self.model.create()
        self.assertEqual(self.instance.obj.dim(),1)

    def test_keys(self):
        """Test keys method"""
        def A_rule(model, i):
            return model.x
        self.model.x = Var()
        self.model.obj = Objective(self.model.A, rule=A_rule)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.obj.keys()),2)

    def test_len(self):
        """Test len method"""
        self.model.obj = Objective(self.model.A)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.obj),0)
        """Test rule option"""
        def f(model):
            ans=0
            for i in model.x.keys():
                ans = ans + model.x[i]
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.obj = Objective(rule=f)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.obj),1)


class Test2DArrayObj(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        self.model.A = Set(initialize=[1,2])

    def tearDown(self):
        pass

    def test_rule_option1(self):
        """Test rule option"""
        def f(model, i, k):
            ans=0
            for j in model.x.keys():
                ans = ans + model.x[j]
            ans *= i
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.obj = Objective(self.model.A,self.model.A, rule=f)
        self.instance = self.model.create()
        try:
            self.assertEqual(self.instance.obj(),None)
            self.fail("Expected ValueError")
        except ValueError:
            pass
        self.instance.x.reset()
        self.assertEqual(self.instance.obj[1,1](), 8)
        self.assertEqual(self.instance.obj[2,1](), 16)
        self.assertEqual(value(self.instance.obj[1,1]), 8)
        self.assertEqual(value(self.instance.obj[2,1]), 16)

    def test_sense_option(self):
        """Test sense option"""
        self.model.obj = Objective(self.model.A,self.model.A,sense=maximize)
        self.instance = self.model.create()
        self.assertEqual(self.instance.obj.sense, maximize)
        self.assertEqual(self.instance.obj.is_minimizing(), False)
        for i in self.instance.obj:
            self.assertEqual(self.instance.obj[i].is_minimizing(), False)

    def test_dim(self):
        """Test dim method"""
        self.model.obj = Objective(self.model.A,self.model.A)
        self.instance = self.model.create()
        self.assertEqual(self.instance.obj.dim(),2)

    def test_keys(self):
        """Test keys method"""
        def A_rule(model, i, j):
            return model.x
        self.model.x = Var()
        self.model.obj = Objective(self.model.A,self.model.A, rule=A_rule)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.obj.keys()),4)

    def test_len(self):
        """Test len method"""
        self.model.obj = Objective(self.model.A,self.model.A)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.obj),0)
        """Test rule option"""
        def f(model):
            ans=0
            for i in model.x.keys():
                ans = ans + model.x[i]
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.obj = Objective(rule=f)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.obj),1)


class MiscObjTests(pyutilib.th.TestCase):

    def test_constructor(self):
        a = Objective(name="b")
        self.assertEqual(a.name,"b")
        try:
            a = Objective(foo="bar")
            self.fail("Can't specify an unexpected constructor option")
        except ValueError:
            pass

    def test_contains(self):
        model=AbstractModel()
        model.a=Set(initialize=[1,2,3])
        model.x=Var()
        def b_rule(model, i):
            return model.x
        model.b=Objective(model.a, rule=b_rule)
        instance=model.create()
        self.assertEqual(2 in instance.b,True)
        tmp=[]
        for i in instance.b:
            tmp.append(i)
        self.assertEqual(len(tmp),3)

    def test_set_get(self):
        a = Objective()
        #try:
            #a.value = 1
            #self.fail("Can't set value attribute")
        #except AttributeError:
            #pass
        self.assertEqual(a(),None)
        #
        model=AbstractModel()
        model.x = Var(initialize=1)
        model.y = Var(initialize=2)
        model.obj = Objective()
        model.obj.expr = model.x+model.y
        instance = model.create()
        instance.reset()
        self.assertEqual(instance.obj(),3)

    def test_rule(self):
        def rule1(model):
            return []
        model=AbstractModel()
        model.o = Objective(rule=rule1)
        try:
            instance=model.create()
            self.fail("Error generating objective")
        except Exception:
            pass
        #
        def rule1(model):
            return 1.1
        model=AbstractModel()
        model.o = Objective(rule=rule1)
        instance=model.create()
        self.assertEqual(instance.o(),1.1)
        #
        def rule1(model, i):
            return 1.1
        model=AbstractModel()
        model.a=Set(initialize=[1,2,3])
        model.o = Objective(model.a,rule=rule1)
        instance=model.create()
        try:
            instance=model.create()
        except Exception:
            self.fail("Error generating objective")


if __name__ == "__main__":
    unittest.main()
