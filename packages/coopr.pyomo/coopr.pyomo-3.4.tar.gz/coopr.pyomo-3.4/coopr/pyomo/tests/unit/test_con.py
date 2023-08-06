#
# Unit Tests for Elements of a Model
#
# TestSimpleCon                Class for testing single constraint
# TestArrayCon                Class for testing array of constraint
#

import logging
import os
import sys
from six import StringIO
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
currdir = dirname(abspath(__file__))+os.sep

from coopr.pyomo.base import IntegerSet
from coopr.pyomo import *
from coopr.opt import *
from coopr.pyomo.base.var import _VarElement
import pyutilib.th as unittest
import pyutilib.services

class LogBuffer(object):
    def __init__(self, logger, logLevel=None):
        if isinstance(logger, logging.Logger):
            self.logger = logger
        else:
            self.logger = logging.getLogger(logger)
        self.buffer = StringIO()
        if logLevel is None:
            self.old_level = None
        else:
            self.old_level = self.logger.getEffectiveLevel()
            self.logger.setLevel(logLevel)
            
        self.logHandler = logging.StreamHandler(self.buffer)
        self.logger.addHandler(self.logHandler)

    def __del__(self):
        self.close()

    def close(self):
        if self.logger is None:
            return
        if self.old_level is not None:
            self.logger.setLevel(self.old_level)

        self.logger.removeHandler(self.logHandler)
        self.logHandler.flush()
        self.buffer.flush()
        self.logHandler = None
        self.logger = None

    def value(self):
        if self.logHandler is not None:
            self.logHandler.flush();
        self.buffer.flush()
        return self.buffer.getvalue()


class PyomoModel(unittest.TestCase):

    def setUp(self):
        self.model = AbstractModel()

    def construct(self,filename):
        self.instance = self.model.create(filename)


class TestConstraintCreation(unittest.TestCase):
    def setUp(self):
        self.model = AbstractModel()
        self.model.x = Var()
        self.model.y = Var()
        self.model.z = Var()

    def test_tuple_construct_equality(self):
        def rule(model):
            return (0.0, model.x)
        self.model.c = Constraint(rule=rule)
        instance=self.model.create()
        self.assertEqual(instance.c._equality,         True)
        self.assertEqual(instance.c.lower,             0)
        self.assertIs   (instance.c.body,              instance.x)
        self.assertEqual(instance.c.upper,             0)

        def rule(model):
            return (model.x, 0.0)
        self.model.c = Constraint(rule=rule)
        instance=self.model.create()
        self.assertEqual(instance.c._equality,         True)
        self.assertEqual(instance.c.lower,             0)
        self.assertIs   (instance.c.body,              instance.x)
        self.assertEqual(instance.c.upper,             0)

    def test_tuple_construct_inf_equality(self):
        def rule(model):
            return (model.x, float('inf'))
        self.model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, self.model.create)

        def rule(model):
            return (float('inf'), model.x)
        self.model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, self.model.create)


    def test_tuple_construct_1sided_inequality(self):
        def rule(model):
            return (None, model.y, 1)
        self.model.c = Constraint(rule=rule)
        instance=self.model.create()
        self.assertEqual(instance.c._equality,         False)
        self.assertEqual(instance.c.lower,             None)
        self.assertIs   (instance.c.body,              instance.y)
        self.assertEqual(instance.c.upper,             1)

        def rule(model):
            return (0, model.y, None)
        self.model.c = Constraint(rule=rule)
        instance=self.model.create()
        self.assertEqual(instance.c._equality,         False)
        self.assertEqual(instance.c.lower,             0)
        self.assertIs   (instance.c.body,              instance.y)
        self.assertEqual(instance.c.upper,             None)

    def test_tuple_construct_1sided_inf_inequality(self):
        def rule(model):
            return (float('-inf'), model.y, 1)
        self.model.c = Constraint(rule=rule)
        instance=self.model.create()
        self.assertEqual(instance.c._equality,         False)
        self.assertEqual(instance.c.lower,             None)
        self.assertIs   (instance.c.body,              instance.y)
        self.assertEqual(instance.c.upper,             1)

        def rule(model):
            return (0, model.y, float('inf'))
        self.model.c = Constraint(rule=rule)
        instance=self.model.create()
        self.assertEqual(instance.c._equality,         False)
        self.assertEqual(instance.c.lower,             0)
        self.assertIs   (instance.c.body,              instance.y)
        self.assertEqual(instance.c.upper,             None)

    def test_tuple_construct_unbounded_inequality(self):
        def rule(model):
            return (None, model.y, None)
        self.model.c = Constraint(rule=rule)
        instance = self.model.create()
        self.assertEqual(instance.c._equality,         False)
        self.assertEqual(instance.c.lower,             None)
        self.assertIs   (instance.c.body,              instance.y)
        self.assertEqual(instance.c.upper,             None)

        def rule(model):
            return (float('-inf'), model.y, float('inf'))
        self.model.c = Constraint(rule=rule)
        instance = self.model.create()
        self.assertEqual(instance.c._equality,         False)
        self.assertEqual(instance.c.lower,             None)
        self.assertIs   (instance.c.body,              instance.y)
        self.assertEqual(instance.c.upper,             None)

    def test_tuple_construct_invalid_1sided_inequality(self):
        def rule(model):
            return (model.x, model.y, None)
        self.model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, self.model.create)

        def rule(model):
            return (None, model.y, model.z)
        self.model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, self.model.create)


    def test_tuple_construct_2sided_inequality(self):
        def rule(model):
            return (0, model.y, 1)
        self.model.c = Constraint(rule=rule)
        instance=self.model.create()
        self.assertEqual(instance.c._equality,         False)
        self.assertEqual(instance.c.lower,             0)
        self.assertIs   (instance.c.body,              instance.y)
        self.assertEqual(instance.c.upper,             1)

    def test_tuple_construct_invalid_2sided_inequality(self):
        def rule(model):
            return (model.x, model.y, 1)
        self.model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, self.model.create)

        def rule(model):
            return (0, model.y, model.z)
        self.model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, self.model.create)



    def test_expr_construct_equality(self):
        def rule(model):
            return 0.0 == model.x
        self.model.c = Constraint(rule=rule)
        instance=self.model.create()
        self.assertEqual(instance.c._equality,         True)
        self.assertEqual(instance.c.lower,             0)
        self.assertIs   (instance.c.body,              instance.x)
        self.assertEqual(instance.c.upper,             0)

        def rule(model):
            return model.x == 0.0
        self.model.c = Constraint(rule=rule)
        instance=self.model.create()
        self.assertEqual(instance.c._equality,         True)
        self.assertEqual(instance.c.lower,             0)
        self.assertIs   (instance.c.body,              instance.x)
        self.assertEqual(instance.c.upper,             0)

    def test_expr_construct_inf_equality(self):
        def rule(model):
            return model.x == float('inf')
        self.model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, self.model.create)

        def rule(model):
            return float('inf') == model.x
        self.model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, self.model.create)


    def test_expr_construct_1sided_inequality(self):
        def rule(model):
            return model.y <= 1
        self.model.c = Constraint(rule=rule)
        instance=self.model.create()
        self.assertEqual(instance.c._equality,         False)
        self.assertEqual(instance.c.lower,             None)
        self.assertIs   (instance.c.body,              instance.y)
        self.assertEqual(instance.c.upper,             1)

        def rule(model):
            return 0 <= model.y
        self.model.c = Constraint(rule=rule)
        instance=self.model.create()
        self.assertEqual(instance.c._equality,         False)
        self.assertEqual(instance.c.lower,             0)
        self.assertIs   (instance.c.body,              instance.y)
        self.assertEqual(instance.c.upper,             None)

        def rule(model):
            return model.y >= 1
        self.model.c = Constraint(rule=rule)
        instance=self.model.create()
        self.assertEqual(instance.c._equality,         False)
        self.assertEqual(instance.c.lower,             1)
        self.assertIs   (instance.c.body,              instance.y)
        self.assertEqual(instance.c.upper,             None)

        def rule(model):
            return 0 >= model.y
        self.model.c = Constraint(rule=rule)
        instance=self.model.create()
        self.assertEqual(instance.c._equality,         False)
        self.assertEqual(instance.c.lower,             None)
        self.assertIs   (instance.c.body,              instance.y)
        self.assertEqual(instance.c.upper,             0)

    def test_expr_construct_unbounded_inequality(self):
        def rule(model):
            return model.y <= float('inf')
        self.model.c = Constraint(rule=rule)
        instance = self.model.create()
        self.assertEqual(instance.c._equality,         False)
        self.assertEqual(instance.c.lower,             None)
        self.assertIs   (instance.c.body,              instance.y)
        self.assertEqual(instance.c.upper,             None)

        def rule(model):
            return float('-inf') <= model.y
        self.model.c = Constraint(rule=rule)
        instance = self.model.create()
        self.assertEqual(instance.c._equality,         False)
        self.assertEqual(instance.c.lower,             None)
        self.assertIs   (instance.c.body,              instance.y)
        self.assertEqual(instance.c.upper,             None)

        def rule(model):
            return model.y >= float('-inf')
        self.model.c = Constraint(rule=rule)
        instance = self.model.create()
        self.assertEqual(instance.c._equality,         False)
        self.assertEqual(instance.c.lower,             None)
        self.assertIs   (instance.c.body,              instance.y)
        self.assertEqual(instance.c.upper,             None)

        def rule(model):
            return float('inf') >= model.y
        self.model.c = Constraint(rule=rule)
        instance = self.model.create()
        self.assertEqual(instance.c._equality,         False)
        self.assertEqual(instance.c.lower,             None)
        self.assertIs   (instance.c.body,              instance.y)
        self.assertEqual(instance.c.upper,             None)

    def test_expr_construct_invalid_unbounded_inequality(self):
        def rule(model):
            return model.y <= float('-inf')
        self.model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, self.model.create)

        def rule(model):
            return float('inf') <= model.y
        self.model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, self.model.create)

        def rule(model):
            return model.y >= float('inf')
        self.model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, self.model.create)

        def rule(model):
            return float('-inf') >= model.y
        self.model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, self.model.create)


class TestSimpleCon(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)

    def tearDown(self):
        pass

    def test_set_expr_explicit_multivariate(self):
        """Test expr= option (multivariate expression)"""
        model = ConcreteModel()
        model.x = Var(RangeSet(1,4),initialize=2)
        ans=0
        for i in model.x:
            ans = ans + model.x[i]
        ans = ans >= 0
        ans = ans <= 1
        model.c = Constraint(expr=ans)
        instance = model.create()
        self.assertEqual(instance.c(), 8)
        self.assertEqual(instance.c.body(), 8)
        self.assertEqual(value(instance.c.body), 8)

    def test_set_expr_explicit_univariate(self):
        """Test expr= option (univariate expression)"""
        model = ConcreteModel()
        model.x = Var(initialize=2)
        ans = model.x >= 0
        ans = ans <= 1
        model.c = Constraint(expr=ans)
        instance = model.create()
        self.assertEqual(instance.c(), 2)
        self.assertEqual(instance.c.body(), 2)
        self.assertEqual(value(instance.c.body), 2)

    def test_set_expr_undefined_univariate(self):
        """Test expr= option (univariate expression)"""
        model = AbstractModel()
        model.x = Var()
        ans = model.x >= 0
        ans = ans <= 1
        model.c = Constraint(expr=ans)
        instance = model.create()
        self.assertRaises(ValueError, instance.c)
        instance.x = 2
        self.assertEqual(instance.c(), 2)
        self.assertEqual(value(instance.c.body), 2)

    def test_set_expr_inline(self):
        """Test expr= option (inline expression)"""
        model = ConcreteModel()
        model.A = RangeSet(1,4)
        model.x = Var(model.A,initialize=2)
        model.c = Constraint(expr=0 <= sum(model.x[i] for i in model.A) <= 1)
        instance = model.create()
        self.assertEqual(instance.c(), 8)
        self.assertEqual(value(instance.c.body), 8)


    def test_rule1(self):
        """Test rule option"""
        def f(model):
            ans=0
            for i in model.x:
                ans = ans + model.x[i]
            ans = ans >= 0
            ans = ans <= 1
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c(), 8)
        self.assertEqual(value(self.instance.c.body), 8)

    def test_rule2(self):
        """Test rule option"""
        def f(model):
            ans=0
            for i in model.x:
                ans = ans + model.x[i]
            return (0,ans,1)
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c(), 8)
        self.assertEqual(value(self.instance.c.body), 8)

    def test_rule3(self):
        """Test rule option"""
        def f(model):
            ans=0
            for i in model.x:
                ans = ans + model.x[i]
            return (0,ans,None)
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c(), 8)
        self.assertEqual(value(self.instance.c.body), 8)

    def test_rule4(self):
        """Test rule option"""
        def f(model):
            ans=0
            for i in model.x:
                ans = ans + model.x[i]
            return (None,ans,1)
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c(), 8)
        self.assertEqual(value(self.instance.c.body), 8)

    def test_rule5(self):
        """Test rule option"""
        def f(model):
            ans=0
            for i in model.x:
                ans = ans + model.x[i]
            return (ans,1)
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c(), 8)
        self.assertEqual(value(self.instance.c.body), 8)

    def test_dim(self):
        """Test dim method"""
        self.model.c = Constraint(noruleinit=True)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c.dim(),0)

    def test_keys(self):
        """Test keys method"""
        self.model.c = Constraint(noruleinit=True)
        self.instance = self.model.create()
        self.assertEqual(list(self.instance.c.keys()),[])

    def test_len(self):
        """Test len method"""
        self.model.c = Constraint(noruleinit=True)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.c),0)


class TestArrayCon(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        self.model.A = Set(initialize=[1,2,3,4])

    def tearDown(self):
        pass

    def test_rule_option1(self):
        """Test rule option"""
        def f(model, i):
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans < 0
            ans = ans > 0
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(self.model.A,rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c[1](), 8)
        self.assertEqual(self.instance.c[2](), 16)
        self.assertEqual(len(self.instance.c), 4)

    def test_old_rule_option1(self):
        """Test rule option"""
        buffer = LogBuffer('coopr.pyomo', logging.WARNING)
        def f(model, i):
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans < 0
            ans = ans > 0
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(self.model.A,rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c[1](), 8)
        self.assertEqual(self.instance.c[2](), 16)
        self.assertEqual(len(self.instance.c), 4)
        #self.assertEqual(buffer.value(), """\
#DEPRECATION WARNING: Detected pre-3.0 style rule where the model argument appears last (Constraint c[1])
#DEPRECATION WARNING: Detected pre-3.0 style rule where the model argument appears last (Constraint c[2])
#DEPRECATION WARNING: Detected pre-3.0 style rule where the model argument appears last (Constraint c[3])
#DEPRECATION WARNING: Detected pre-3.0 style rule where the model argument appears last (Constraint c[4])
#""")

    def test_rule_option2(self):
        """Test rule option"""
        def f(model, i):
            if i%2 == 0:
                return Constraint.Skip
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans < 0
            ans = ans > 0
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(self.model.A,rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c[1](), 8)
        self.assertEqual(len(self.instance.c), 2)

    def test_rule_option3(self):
        """Test rule option"""
        def f(model, i):
            if i%2 == 0:
                return Constraint.Skip
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans < 0
            ans = ans > 0
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(self.model.A,rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c[1](), 8)
        self.assertEqual(len(self.instance.c), 2)

    def test_rule_option2a(self):
        """Test rule option"""
        @simple_constraint_rule
        def f(model, i):
            if i%2 == 0:
                return None
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans < 0
            ans = ans > 0
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(self.model.A,rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c[1](), 8)
        self.assertEqual(len(self.instance.c), 2)

    def test_rule_option3a(self):
        """Test rule option"""
        @simple_constraint_rule
        def f(model, i):
            if i%2 == 0:
                return None
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans < 0
            ans = ans > 0
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(self.model.A,rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c[1](), 8)
        self.assertEqual(len(self.instance.c), 2)

    def test_dim(self):
        """Test dim method"""
        self.model.c = Constraint(self.model.A, noruleinit=True)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c.dim(),1)

    def test_keys(self):
        """Test keys method"""
        self.model.c = Constraint(self.model.A, noruleinit=True)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.c.keys()),0)

    def test_len(self):
        """Test len method"""
        self.model.c = Constraint(self.model.A, noruleinit=True)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.c),0)
        """Test rule option"""
        def f(model):
            ans=0
            for i in model.x:
                ans = ans + model.x[i]
            ans = ans==2
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(rule=f)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.c),1)


class TestConList(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        self.model.A = Set(initialize=[1,2,3,4])

    def tearDown(self):
        pass

    def test_rule_option1(self):
        """Test rule option"""
        def f(model, i):
            if i > 4:
                return ConstraintList.End
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans < 0
            ans = ans > 0
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = ConstraintList(rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c[1](), 8)
        self.assertEqual(self.instance.c[2](), 16)
        self.assertEqual(len(self.instance.c), 4)

    def test_rule_option2(self):
        """Test rule option"""
        def f(model, i):
            if i > 2:
                return ConstraintList.End
            i = 2*i - 1
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans < 0
            ans = ans > 0
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = ConstraintList(rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c[1](), 8)
        self.assertEqual(len(self.instance.c), 2)

    def test_rule_option1a(self):
        """Test rule option"""
        @simple_constraintlist_rule
        def f(model, i):
            if i > 4:
                return None
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans < 0
            ans = ans > 0
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = ConstraintList(rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c[1](), 8)
        self.assertEqual(self.instance.c[2](), 16)
        self.assertEqual(len(self.instance.c), 4)

    def test_rule_option2a(self):
        """Test rule option"""
        @simple_constraintlist_rule
        def f(model, i):
            if i > 2:
                return None
            i = 2*i - 1
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans < 0
            ans = ans > 0
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = ConstraintList(rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c[1](), 8)
        self.assertEqual(len(self.instance.c), 2)

    def test_dim(self):
        """Test dim method"""
        self.model.c = ConstraintList(noruleinit=True)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c.dim(),1)

    def test_keys(self):
        """Test keys method"""
        self.model.c = ConstraintList(noruleinit=True)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.c.keys()),0)

    def test_len(self):
        """Test len method"""
        self.model.c = ConstraintList(noruleinit=True)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.c),0)


class Test2DArrayCon(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        self.model.A = Set(initialize=[1,2])

    def tearDown(self):
        pass

    def test_rule_option(self):
        """Test rule option"""
        def f(model, i, j):
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans < 0
            ans = ans > 0
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(self.model.A,self.model.A,rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c[1,1](), 8)
        self.assertEqual(self.instance.c[2,1](), 16)

    def test_old_rule_option(self):
        """Test rule option"""
        buffer = LogBuffer('coopr.pyomo', logging.WARNING)
        def f(model, i, j):
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans < 0
            ans = ans > 0
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(self.model.A,self.model.A,rule=f)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c[1,1](), 8)
        self.assertEqual(self.instance.c[2,1](), 16)
        #self.assertEqual(buffer.value(), """\
#DEPRECATION WARNING: Detected pre-3.0 style rule where the model argument appears last (Constraint c[1,1])
#DEPRECATION WARNING: Detected pre-3.0 style rule where the model argument appears last (Constraint c[1,2])
#DEPRECATION WARNING: Detected pre-3.0 style rule where the model argument appears last (Constraint c[2,1])
#DEPRECATION WARNING: Detected pre-3.0 style rule where the model argument appears last (Constraint c[2,2])
#""")

    def test_dim(self):
        """Test dim method"""
        self.model.c = Constraint(self.model.A,self.model.A, noruleinit=True)
        self.instance = self.model.create()
        self.assertEqual(self.instance.c.dim(),2)

    def test_keys(self):
        """Test keys method"""
        self.model.c = Constraint(self.model.A,self.model.A, noruleinit=True)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.c.keys()),0)

    def test_len(self):
        """Test len method"""
        self.model.c = Constraint(self.model.A,self.model.A, noruleinit=True)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.c),0)
        """Test rule option"""
        def f(model):
            ans=0
            for i in model.x:
                ans = ans + model.x[i]
            ans = ans==2
            return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(rule=f)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.c),1)

class MiscConTests(pyutilib.th.TestCase):

    def test_slack_methods(self):
        model = ConcreteModel()
        model.x = Var(initialize=2.0)
        L = -1.0
        U = 5.0
        model.cL = Constraint(expr=model.x**2 >= L)
        self.assertEqual(model.cL.lslack(), -5.0)
        self.assertEqual(model.cL.uslack(), float('inf'))
        model.cU = Constraint(expr=model.x**2 <= U)
        self.assertEqual(model.cU.lslack(), float('-inf'))
        self.assertEqual(model.cU.uslack(), 1.0)
        model.cR = Constraint(expr=L <= model.x**2 <= U)
        self.assertEqual(model.cR.lslack(), -5.0)
        self.assertEqual(model.cR.uslack(), 1.0)

    def test_constructor(self):
        a = Constraint(name="b", noruleinit=True)
        self.assertEqual(a.name,"b")
        try:
            a = Constraint(foo="bar", noruleinit=True)
            self.fail("Can't specify an unexpected constructor option")
        except ValueError:
            pass

    def test_contains(self):
        model=AbstractModel()
        model.a=Set(initialize=[1,2,3])
        model.b=Constraint(model.a)
        instance=model.create()
        self.assertEqual(2 in instance.b,False)
        tmp=[]
        for i in instance.b:
            tmp.append(i)
        self.assertEqual(len(tmp),0)

    def test_set_get(self):
        a = Constraint(noruleinit=True)
        #try:
            #a.value = 1
            #self.fail("Can't set value attribute")
        #except AttributeError:
            #pass
        self.assertEqual(a(),None)

    def test_rule(self):
        def rule1(model):
            return Constraint.Skip
        model=AbstractModel()
        model.o = Constraint(rule=rule1)
        instance=model.create()
        try:
            instance=model.create()
        except Exception:
            e = sys.exc_info()[1]
            self.fail("Failure to create empty constraint: %s" % str(e))
        #
        def rule1(model):
            return (0.0,model.x,2.0)
        model=AbstractModel()
        model.x = Var(initialize=1.1)
        model.o = Constraint(rule=rule1)
        instance=model.create()
        instance.reset()
        self.assertEqual(instance.o(),1.1)
        #
        def rule1(model, i):
            return Constraint.Skip
        model=AbstractModel()
        model.a=Set(initialize=[1,2,3])
        model.o = Constraint(model.a,rule=rule1)
        try:
            instance=model.create()
        except Exception:
            self.fail("Error generating empty objective")
        #
        def rule1(model):
            return (0.0,1.1,2.0,None)
        model=AbstractModel()
        model.o = Constraint(rule=rule1)
        try:
            instance=model.create()
            self.fail("Can only return tuples of length 2 or 3")
        except ValueError:
            pass

    def test_tuple_constraint_create(self):
        def rule1(model):
            return (0.0,model.x)
        model=AbstractModel()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        instance=model.create()
        #
        def rule1(model):
            return (model.y,model.x,model.z)
        model=AbstractModel()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(ValueError, model.create)
        #

    def test_expression_constructor_coverage(self):
        def rule1(model):
            expr=model.x
            expr = expr == 0.0
            expr = expr > 1.0
            return expr
        model=AbstractModel()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(TypeError, model.create)
        #
        def rule1(model):
            expr = model.U >= model.x
            expr = expr >= model.L
            return expr
        model=AbstractModel()
        model.x = Var()
        model.L = Param(initialize=0)
        model.U = Param(initialize=1)
        model.o = Constraint(rule=rule1)
        instance=model.create()
        #
        def rule1(model):
            expr = model.x <= model.z
            expr = expr >= model.y
            return expr
        model=AbstractModel()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(ValueError, model.create)
        #
        def rule1(model):
            expr = model.x >= model.z
            expr = model.y >= expr
            return expr
        model=AbstractModel()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(ValueError, model.create)
        #
        def rule1(model):
            expr = model.y <= model.x
            expr = model.y >= expr
            return expr
        model=AbstractModel()
        model.x = Var()
        model.y = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(ValueError, model.create)
        #
        def rule1(model):
            expr = model.x >= model.L
            return expr
        model=AbstractModel()
        model.x = Var()
        model.L = Param(initialize=0)
        model.o = Constraint(rule=rule1)
        instance=model.create()
        #
        def rule1(model):
            expr = model.U >= model.x
            return expr
        model=AbstractModel()
        model.x = Var()
        model.U = Param(initialize=0)
        model.o = Constraint(rule=rule1)
        instance=model.create()

        #
        def rule1(model):
            expr=model.x
            expr = expr == 0.0
            expr = expr < 1.0
            return expr
        model=AbstractModel()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(TypeError, model.create)
        #
        def rule1(model):
            expr = model.U <= model.x
            expr = expr <= model.L
            return expr
        model=AbstractModel()
        model.x = Var()
        model.L = Param(initialize=0)
        model.U = Param(initialize=1)
        model.o = Constraint(rule=rule1)
        instance=model.create()
        #
        def rule1(model):
            expr = model.x >= model.z
            expr = expr <= model.y
            return expr
        model=AbstractModel()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(ValueError, model.create)
        #
        def rule1(model):
            expr = model.x <= model.z
            expr = model.y <= expr
            return expr
        model=AbstractModel()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(ValueError, model.create)
        #
        def rule1(model):
            expr = model.y >= model.x
            expr = model.y <= expr
            return expr
        model=AbstractModel()
        model.x = Var()
        model.y = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(ValueError, model.create)
        #
        def rule1(model):
            expr = model.x <= model.L
            return expr
        model=AbstractModel()
        model.x = Var()
        model.L = Param(initialize=0)
        model.o = Constraint(rule=rule1)
        instance=model.create()
        #
        def rule1(model):
            expr = model.U <= model.x
            return expr
        model=AbstractModel()
        model.x = Var()
        model.U = Param(initialize=0)
        model.o = Constraint(rule=rule1)
        instance=model.create()

        #
        def rule1(model):
            return model.x+model.x
        model=AbstractModel()
        model.x = Var()
        model.o = Constraint(rule=rule1)
        try:
            instance=model.create()
            self.fail("Cannot return an unbounded expression")
        except ValueError:
            pass
        #

if __name__ == "__main__":
    unittest.main()
