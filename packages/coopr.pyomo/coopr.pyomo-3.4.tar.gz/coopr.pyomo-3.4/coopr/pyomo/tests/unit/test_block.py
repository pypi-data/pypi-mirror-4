#
# Unit Tests for Elements of a Block
#

import os
import sys
from os.path import abspath, dirname
#sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
currdir = dirname(abspath(__file__))+os.sep

from coopr.pyomo.base import IntegerSet
from coopr.pyomo import *
from coopr.opt import *
from coopr.pyomo.base.var import _VarElement
import pyutilib.th as unittest
import pyutilib.services


class Test(unittest.TestCase):

    def setUp(self):
        #
        # Create block
        #
        self.block = Block()

    def tearDown(self):
        if os.path.exists("unknown.lp"):
            os.unlink("unknown.lp")
        pyutilib.services.TempfileManager.clear_tempfiles()

    def test_clear_attribute(self):
        """ Coverage of the _clear_attribute method """
        obj = Set()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

        obj = Var()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

        obj = Param()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

        obj = Objective()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

        obj = Constraint()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

        obj = Set()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

    def test_set_attr(self):
        self.block.x = Param(mutable=True)
        self.block.x = 5
        self.assertEqual(value(self.block.x), 5)
        self.block.x = 6
        self.assertEqual(value(self.block.x), 6)
        try:
            self.block.x = None
            self.fail("Expected exception assigning None to domain Any")
        except ValueError:
            pass

    def test_display(self):
        self.block.A = RangeSet(1,4)
        self.block.x = Var(self.block.A, bounds=(-1,1))
        def obj_rule(block):
            return summation(block.x)
        self.block.obj = Objective(rule=obj_rule)
        #self.instance = self.block.create()
        #self.block.pprint()
        #self.block.display()

    def Xtest_write2(self):
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

    def Xtest_write3(self):
        """Test that the summation works correctly, even though param 'w' has a default value"""
        self.model.J = RangeSet(1,4)
        self.model.w=Param(self.model.J, default=4)
        self.model.x=Var(self.model.J)
        def obj_rule(instance):
            return summation(instance.x, instance.w)
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.obj[None].expr._args), 4)

    def Xtest_solve1(self):
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
        solutions = opt.solve(self.instance, keepfiles=True)
        self.instance.load(solutions)
        self.instance.display(currdir+"solve1.out")
        self.assertFileEqualsBaseline(currdir+"solve1.out",currdir+"solve1.txt")
        #
        def d_rule(model):
            return model.x[1] > 0
        self.model.d = Constraint(rule=d_rule)
        self.model.d.deactivate()
        self.instance = self.model.create()
        solutions = opt.solve(self.instance, keepfiles=True)
        self.instance.load(solutions)
        self.instance.display(currdir+"solve1.out")
        self.assertFileEqualsBaseline(currdir+"solve1.out",currdir+"solve1.txt")
        #
        self.model.d.activate()
        self.instance = self.model.create()
        solutions = opt.solve(self.instance, keepfiles=True)
        self.instance.load(solutions)
        self.instance.display(currdir+"solve1.out")
        self.assertFileEqualsBaseline(currdir+"solve1.out",currdir+"solve1a.txt")
        #
        self.model.d.deactivate()
        def e_rule(i, model):
            return model.x[i] > 0
        self.model.e = Constraint(self.model.A, rule=e_rule)
        self.instance = self.model.create()
        for i in self.instance.A:
            self.instance.e[i].deactivate()
        solutions = opt.solve(self.instance, keepfiles=True)
        self.instance.load(solutions)
        self.instance.display(currdir+"solve1.out")
        self.assertFileEqualsBaseline(currdir+"solve1.out",currdir+"solve1b.txt")

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

    def Xtest_solve3(self):
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

    def Xtest_solve4(self):
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
        solutions = opt.solve(self.instance)
        self.instance.load(solutions.solution(0))
        self.instance.display(currdir+"solve1.out")
        self.assertFileEqualsBaseline(currdir+"solve1.out",currdir+"solve1.txt")

if __name__ == "__main__":
    unittest.main()
