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
from coopr.opt import *
from nose.tools import nottest

class TestVarSetBounds(unittest.TestCase):

    #Test within=RangeSet()
    def test_rangeset_domain(self):
        if not pyutilib.services.registered_executable("glpsol"):
            return
        self.model = ConcreteModel()
        self.model.s = RangeSet(3) #Set(initialize=[1,2,3])
        self.model.y = Var([1,2], within=self.model.s)
        
        self.model.obj = Objective(expr=self.model.y[1]-self.model.y[2])
        self.model.con1 = Constraint(expr=self.model.y[1] >= 1.1)
        self.model.con2 = Constraint(expr=self.model.y[2] <= 2.9)
        
        self.instance = self.model.create()
        self.opt = SolverFactory("glpk")
        self.results = self.opt.solve(self.instance)
        self.instance.load(self.results)

        self.assertEqual(self.instance.y[1],2)
        self.assertEqual(self.instance.y[2],2)
 

    def test_pyomo_Set_domain(self):
        if not pyutilib.services.registered_executable("glpsol"):
            return
        self.model = ConcreteModel()
        self.model.s = Set(initialize=[1,2,3])
        self.model.y = Var([1,2], within=self.model.s)
        
        self.model.obj = Objective(expr=self.model.y[1]-self.model.y[2])
        self.model.con1 = Constraint(expr=self.model.y[1] >= 1.1)
        self.model.con2 = Constraint(expr=self.model.y[2] <= 2.9)
        
        self.instance = self.model.create()
        self.opt = SolverFactory("glpk")
        self.results = self.opt.solve(self.instance)
        self.instance.load(self.results)

        self.assertEqual(self.instance.y[1],2)
        self.assertEqual(self.instance.y[2],2)
     

    #Bad pyomo Set for variable domain -- empty pyomo Set
    def test_pyomo_Set_domain_empty(self):
        with self.assertRaises(ValueError) as cm:
            self.model = ConcreteModel()
            self.model.s = Set(initialize=[])
            self.model.y = Var([1,2], within=self.model.s)


    #Bad pyomo Set for variable domain -- missing elements
    def test_pyomo_Set_domain_missing(self):
        with self.assertRaises(ValueError) as cm:
            self.model = ConcreteModel()
            self.model.s = Set(initialize=[1,4,5])
            self.model.y = Var([1,2], within=self.model.s)


    #Bad pyomo Set for variable domain -- noninteger elements
    def test_pyomo_Set_domain_duplicates(self):
        with self.assertRaises(ValueError) as cm:
            self.model = ConcreteModel()
            self.model.s = Set(initialize=[1.7,2,3])
            self.model.y = Var([1,2], within=self.model.s)
 

    def test_pyomo_Set_dat_file_domain(self):
        if not pyutilib.services.registered_executable("glpsol"):
            return
        self.model = AbstractModel()
        self.model.s = Set()
        self.model.y = Var([1,2], within=self.model.s)
       
        def obj_rule(model):
            return sum(model.y[i]*(-1)**(i-1) for i in model.y)
        self.model.obj = Objective(rule=obj_rule) #sum(self.model.y[i]*(-1)**(i-1) for i in self.model.y))
        self.model.con = Constraint([1,2],expr=lambda model, i : model.y[i]*(-1)**(i-1) >= (1.1)**(2-i) * (-2.9)**(i-1))
        
        self.instance = self.model.create(currdir+"vars_dat_file.dat")
        self.opt = SolverFactory("glpk")
        self.results = self.opt.solve(self.instance)
        self.instance.load(self.results)

        self.assertEqual(self.instance.y[1],2)
        self.assertEqual(self.instance.y[2],2)
     

    #Bad pyomo Set for variable domain -- empty pyomo Set
    def test_pyomo_Set_dat_file_domain_empty(self):
        with self.assertRaises(ValueError) as cm:
            self.model = AbstractModel()
            self.model.s = Set()
            self.model.y = Var([1,2], within=self.model.s)
            self.instance = self.model.create(currdir+"vars_dat_file_empty.dat")


    #Bad pyomo Set for variable domain -- missing elements
    def test_pyomo_Set_dat_file_domain_missing(self):
        with self.assertRaises(ValueError) as cm:
            self.model = AbstractModel()
            self.model.s = Set()
            self.model.y = Var([1,2], within=self.model.s)
            self.instance = self.model.create(currdir+"vars_dat_file_missing.dat")


    #Bad pyomo Set for variable domain -- noninteger elements
    def test_pyomo_Set_dat_file_domain_duplicates(self):
        with self.assertRaises(ValueError) as cm:
            self.model = AbstractModel()
            self.model.s = Set()
            self.model.y = Var([1,2], within=self.model.s)
            self.instance = self.model.create(currdir+"vars_dat_file_nonint.dat")
 

    #Test within=list -- this works for range() since range() returns a list
    def test_list_domain(self):
        if not pyutilib.services.registered_executable("glpsol"):
            return
        self.model = ConcreteModel()
        self.model.y = Var([1,2], within=[1,2,3])
        
        self.model.obj = Objective(expr=self.model.y[1]-self.model.y[2])
        self.model.con1 = Constraint(expr=self.model.y[1] >= 1.1)
        self.model.con2 = Constraint(expr=self.model.y[2] <= 2.9)
        
        self.instance = self.model.create()
        self.opt = SolverFactory("glpk")
        self.results = self.opt.solve(self.instance)
        self.instance.load(self.results)

        self.assertEqual(self.instance.y[1],2)
        self.assertEqual(self.instance.y[2],2)


    #Bad list for variable domain -- empty list
    def test_list_domain_empty(self):
        with self.assertRaises(ValueError) as cm:
            self.model = ConcreteModel()
            self.model.y = Var([1,2], within=[])


    #Bad list for variable domain -- missing elements
    def test_list_domain_bad_missing(self):
        with self.assertRaises(ValueError) as cm:
            self.model = ConcreteModel()
            self.model.y = Var([1,2], within=[1,4,5])


    #Bad list for variable domain -- duplicate elements
    def test_list_domain_bad_duplicates(self):
        with self.assertRaises(ValueError) as cm:
            self.model = ConcreteModel()
            self.model.y = Var([1,2], within=[1,1,2,3])


    #Bad list for variable domain -- noninteger elements
    def test_list_domain_bad_duplicates(self):
        with self.assertRaises(ValueError) as cm:
            self.model = ConcreteModel()
            self.model.y = Var([1,2], within=[1.7,2,3])
   

    #Test within=set() -- python native set, not pyomo Set object
    def test_set_domain(self):
        if not pyutilib.services.registered_executable("glpsol"):
            return
        self.model = ConcreteModel()
        self.model.y = Var([1,2], within=set([1,2,3]))
        
        self.model.obj = Objective(expr=self.model.y[1]-self.model.y[2])
        self.model.con1 = Constraint(expr=self.model.y[1] >= 1.1)
        self.model.con2 = Constraint(expr=self.model.y[2] <= 2.9)
        
        self.instance = self.model.create()
        self.opt = SolverFactory("glpk")
        self.results = self.opt.solve(self.instance)
        self.instance.load(self.results)

        self.assertEqual(self.instance.y[1],2)
        self.assertEqual(self.instance.y[2],2)


    #Bad set for variable domain -- empty set
    def test_set_domain_empty(self):
        with self.assertRaises(ValueError) as cm:
            self.model = ConcreteModel()
            self.model.y = Var([2,2], within=set([]))


    #Bad set for variable domain -- missing elements
    def test_set_domain_bad_missing(self):
        with self.assertRaises(ValueError) as cm:
            self.model = ConcreteModel()
            self.model.y = Var([1,2], within=set([1,4,5]))


    #Bad set for variable domain -- duplicate elements
    def test_set_domain_bad_duplicates(self):
        with self.assertRaises(ValueError) as cm:
            self.model = ConcreteModel()
            self.model.y = Var([1,2], within=set([1,1,2,3]))


    #Bad set for variable domain -- noninteger elements
    def test_set_domain_bad_duplicates(self):
        with self.assertRaises(ValueError) as cm:
            self.model = ConcreteModel()
            self.model.y = Var([1,2], within=set([1.7,2,3]))
   

    #Test within=xrange()
    def test_rangeset_domain(self):
        if not pyutilib.services.registered_executable("glpsol"):
            return
        self.model = ConcreteModel()
        self.model.y = Var([1,2], within=xrange(4))
        
        self.model.obj = Objective(expr=self.model.y[1]-self.model.y[2])
        self.model.con1 = Constraint(expr=self.model.y[1] >= 1.1)
        self.model.con2 = Constraint(expr=self.model.y[2] <= 2.9)
        
        self.instance = self.model.create()
        self.opt = SolverFactory("glpk")
        self.results = self.opt.solve(self.instance)
        self.instance.load(self.results)

        self.assertEqual(self.instance.y[1],2)
        self.assertEqual(self.instance.y[2],2)




if __name__ == "__main__":
    unittest.main()

