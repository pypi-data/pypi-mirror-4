#
# Unit Tests for Elements of a Model
#
# Test             Class to test the Model class
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


class Test(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)

    def tearDown(self):
        if os.path.exists("unknown.lp"):
            os.unlink("unknown.lp")
        pyutilib.services.TempfileManager.clear_tempfiles()

    def test_clear_attribute(self):
        """ Coverage of the _clear_attribute method """
        obj = Set()
        self.model.A = obj
        self.assertEqual(self.model.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.model.A)

        obj = Var()
        self.model.A = obj
        self.assertEqual(self.model.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.model.A)

        obj = Param()
        self.model.A = obj
        self.assertEqual(self.model.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.model.A)

        obj = Objective()
        self.model.A = obj
        self.assertEqual(self.model.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.model.A)

        obj = Constraint()
        self.model.A = obj
        self.assertEqual(self.model.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.model.A)

        obj = Set()
        self.model.A = obj
        self.assertEqual(self.model.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.model.A)

    def test_set_attr(self):
        self.model.x = Param(mutable=True)
        self.model.x = 5
        self.assertEqual(value(self.model.x), 5)
        self.model.x = 6
        self.assertEqual(value(self.model.x), 6)
        try:
            self.model.x = None
            self.fail("Expected exception assigning None to domain Any")
        except ValueError:
            pass

    def test_write(self):
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        self.instance.write()

    def test_write2(self):
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        self.model.obj = Objective(rule=obj_rule)
        def c_rule(model):
            return (1, model.x[1]+model.x[2], 2)
        self.model.c = Constraint(rule=c_rule)
        self.instance = self.model.create()
        self.instance.write()

    def test_write3(self):
        """Test that the summation works correctly, even though param 'w' has a default value"""
        self.model.J = RangeSet(1,4)
        self.model.w=Param(self.model.J, default=4)
        self.model.x=Var(self.model.J)
        def obj_rule(instance):
            return summation(instance.w, instance.x)
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.obj[None].expr._args), 4)

    def test_solve1(self):
        if not pyutilib.services.registered_executable("glpsol"):
            return
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        self.model.obj = Objective(rule=obj_rule)
        def c_rule(model):
            expr = 0
            for i in model.A:
                expr += i*model.x[i]
            return expr == 0
        self.model.c = Constraint(rule=c_rule)
        self.instance = self.model.create()
        #self.instance.pprint()
        opt = SolverFactory('glpk')
        results = opt.solve(self.instance, keepfiles=True, symbolic_solver_labels=True)
        results.write(filename=currdir+"solve1.out", format='json')
        self.assertMatchesJsonBaseline(currdir+"solve1.out",currdir+"solve1.txt", tolerance=1e-4)
        #
        def d_rule(model):
            return model.x[1] > 0
        self.model.d = Constraint(rule=d_rule)
        self.model.d.deactivate()
        self.instance = self.model.create()
        results = opt.solve(self.instance, keepfiles=True)
        results.write(filename=currdir+"solve1x.out", format='json')
        self.assertMatchesJsonBaseline(currdir+"solve1x.out",currdir+"solve1.txt", tolerance=1e-4)
        #
        self.model.d.activate()
        self.instance = self.model.create()
        results = opt.solve(self.instance, keepfiles=True)
        results.write(filename=currdir+"solve1a.out", format='json')
        self.assertMatchesJsonBaseline(currdir+"solve1a.out",currdir+"solve1a.txt", tolerance=1e-4)
        #
        self.model.d.deactivate()
        def e_rule(model, i):
            return model.x[i] > 0
        self.model.e = Constraint(self.model.A, rule=e_rule)
        self.instance = self.model.create()
        for i in self.instance.A:
            self.instance.e[i].deactivate()
        results = opt.solve(self.instance, keepfiles=True)
        results.write(filename=currdir+"solve1b.out", format='json')
        self.assertMatchesJsonBaseline(currdir+"solve1b.out",currdir+"solve1b.txt", tolerance=1e-4)

    def Xtest_load1(self):
        """Testing loading of vector solutions"""
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        self.model.obj = Objective(rule=obj_rule)
        def c_rule(model):
            expr = 0
            for i in model.A:
                expr += i*model.x[i]
            return expr == 0
        self.model.c = Constraint(rule=c_rule)
        self.instance = self.model.create()
        ans = [0.75]*4
        self.instance.load(ans)
        self.instance.display(currdir+"solve1.out")
        self.assertFileEqualsBaseline(currdir+"solve1.out",currdir+"solve1c.txt")

    def Xtest_solve2(self):
        """
        WEH - this is disabled because glpk appears to work fine
        on this example.  I'm not quite sure what has changed that has
        impacted this test...
        """
        if not pyutilib.services.registered_executable("glpsol"):
            return
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            expr = 0
            for i in model.A:
                expr += model.x[i]
            return expr
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        #self.instance.pprint()
        opt = solvers.GLPK(keepfiles=True)
        solutions = opt.solve(self.instance)
        solutions.write()
        sys.exit(1)
        try:
            self.instance.load(solutions)
            self.fail("Cannot load a solution with a bad solver status")
        except ValueError:
            pass

    def test_solve3(self):
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            expr = 0
            for i in model.A:
                expr += model.x[i]
            return expr
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        self.instance.display(currdir+"solve3.out")
        self.assertFileEqualsBaseline(currdir+"solve3.out",currdir+"solve3.txt")

    def test_solve4(self):
        if not pyutilib.services.registered_executable("glpsol"):
            return
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        self.model.obj = Objective(rule=obj_rule)
        def c_rule(model):
            expr = 0
            for i in model.A:
                expr += i*model.x[i]
            return expr == 0
        self.model.c = Constraint(rule=c_rule)
        self.instance = self.model.create()
        #self.instance.pprint()
        opt = SolverFactory('glpk', keepfiles=True)
        results = opt.solve(self.instance, symbolic_solver_labels=True)
        results.write(filename=currdir+'solve4.out', format='json')
        self.assertMatchesJsonBaseline(currdir+"solve4.out",currdir+"solve1.txt", tolerance=1e-4)

    def Xtest_solve5(self):
        """ A draft test for the option to select an objective """
        if not pyutilib.services.registered_executable("glpsol"):
            return
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj1_rule(model):
            expr = 0
            for i in model.A:
                expr += model.x[i]
            return expr
        self.model.obj1 = Objective(rule=obj1_rule)
        def obj2_rule(model):
            expr = 0
            tmp=-1
            for i in model.A:
                expr += tmp*i*model.x[i]
                tmp *= -1
            return expr
        self.model.obj2 = Objective(rule=obj2_rule)
        self.instance = self.model.create()
        opt = SolverFactory('glpk', keepfiles=True)
        results = opt.solve(self.instance, objective='obj2')
        results.write(filename=currdir+"solve5.out", format='json')
        self.assertMatchesJsonBaseline(currdir+"solve5.out",currdir+"solve5a.txt", tolerance=1e-4)

if __name__ == "__main__":
    unittest.main()
