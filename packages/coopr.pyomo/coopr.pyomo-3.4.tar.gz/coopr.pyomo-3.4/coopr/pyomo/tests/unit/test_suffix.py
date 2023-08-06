#
# Unit Tests for Suffix
#

import os
import sys
import copy
import itertools
import pickle
from os.path import abspath, dirname
currdir = dirname(abspath(__file__))+os.sep

from coopr.pyomo import *
from coopr.pyomo.base.suffix import active_export_suffix_generator, \
                                    export_suffix_generator, \
                                    active_import_suffix_generator, \
                                    import_suffix_generator, \
                                    active_local_suffix_generator, \
                                    local_suffix_generator, \
                                    active_suffix_generator, \
                                    suffix_generator
import pyutilib.th as unittest

from six import StringIO

def simple_con_rule(model,i):
    return model.x[i] == 1
def simple_obj_rule(model,i):
    return model.x[i]

class TestSuffixMethods(unittest.TestCase):
    
    # test __init__
    def test_init(self):
        model = ConcreteModel()
        # no keywords
        model.junk = Suffix()
        del model.junk
        
        table = {'a':1}
        for direction,datatype in itertools.product(Suffix.SuffixDirections,Suffix.SuffixDatatypes):
            if datatype is str:
                model.junk = Suffix(direction=direction,datatype=datatype,table=table)
            else:
                model.junk = Suffix(direction=direction,datatype=datatype)
            del model.junk
            
        # no table should raise an exception for datatype=str
        try:
            model.junk = Suffix(datatype=str)
        except ValueError:
            pass
        else:
            self.fail("A symbolic (str) suffix should fail when no table is supplied")

    # test importEnabled
    def test_importEnabled(self):
        model = ConcreteModel()
        model.test_local = Suffix(direction=Suffix.LOCAL)
        self.assertTrue(model.test_local.importEnabled() is False)

        model.test_out = Suffix(direction=Suffix.IMPORT)
        self.assertTrue(model.test_out.importEnabled() is True)

        model.test_in = Suffix(direction=Suffix.EXPORT)
        self.assertTrue(model.test_in.importEnabled() is False)

        model.test_inout = Suffix(direction=Suffix.IMPORT_EXPORT)        
        self.assertTrue(model.test_inout.importEnabled() is True)

    # test exportEnabled
    def test_exportEnabled(self):
        model = ConcreteModel()

        model.test_local = Suffix(direction=Suffix.LOCAL)        
        self.assertTrue(model.test_local.exportEnabled() is False)

        model.test_out = Suffix(direction=Suffix.IMPORT)
        self.assertTrue(model.test_out.exportEnabled() is False)

        model.test_in = Suffix(direction=Suffix.EXPORT)
        self.assertTrue(model.test_in.exportEnabled() is True)

        model.test_inout = Suffix(direction=Suffix.IMPORT_EXPORT)
        self.assertTrue(model.test_inout.exportEnabled() is True)

    # test setNumericValue
    def test_setNumericValue(self):
        model = ConcreteModel()
        model.a = Var()
        model.junk = Suffix(datatype=float)
        model.junk.setNumericValue(model.a,1.0)
        self.assertEqual(model.junk.getValue(model.a), 1.0)
        self.assertEqual(model.junk.getNumericValue(model.a), 1.0)

        del model.junk
        model.junk = Suffix(datatype=str,table={'j':1})
        model.junk.setNumericValue(model.a,1)
        self.assertEqual(model.junk.getValue(model.a), 'j')
        self.assertEqual(model.junk.getNumericValue(model.a), 1)

    # test getNumericValue
    def test_getNumericValue(self):
        model = ConcreteModel()
        model.a = Var()
        model.junk = Suffix(datatype=float)
        model.junk.setValue(model.a,1.0)
        self.assertEqual(model.junk.getValue(model.a), 1.0)
        self.assertEqual(model.junk.getNumericValue(model.a), 1.0)

        del model.junk
        model.junk = Suffix(datatype=str,table={'j':1})
        model.junk.setValue(model.a,'j')
        self.assertEqual(model.junk.getValue(model.a), 'j')
        self.assertEqual(model.junk.getNumericValue(model.a), 1)

    # test setValue with wrong number of args
    def test_setValue_wrongnumberargs(self):
        model = ConcreteModel()
        model.junk = Suffix()
        model.x = Var()
        try:
            model.junk.setValue()
        except TypeError:
            pass
        else:
            self.fail("Trying to call setValue with wrong number of arguments should fail.")
        try:
            model.junk.setValue(1,2,3)
        except TypeError:
            pass
        else:
            self.fail("Trying to call setValue with wrong number of arguments should fail.")

    # test clearValue with wrong number of args
    def test_clearValue_wrongnumberargs(self):
        model = ConcreteModel()
        model.junk = Suffix()
        model.x = Var()
        model.junk.clearValue(model.x)
        try:
            model.junk.clearValue(model.x,1.0)
        except TypeError:
            pass
        else:
            self.fail("Trying to call clearValue with wrong number of arguments should fail.")

    # test setValue and getValue and the use of default
    # and if the search hierarchy correctly interacts with Var
    def test_setValue_getValue_Var(self):
        model = ConcreteModel()
        model.junk_w_default = Suffix(default=0.0)
        model.junk = Suffix()
        model.x = Var()
        model.X = Var([1,2,3])

        for suf in (model.junk_w_default,model.junk):
            suf.setValue(model.X,1.0)
            suf.setValue(model.X[1],2.0)

        for suf in (model.junk_w_default,model.junk):
            self.assertEqual(suf.getValue(model.X), 1.0)
            self.assertEqual(suf.getValue(model.X[1]), 2.0)

        self.assertEqual(model.junk_w_default.getValue(model.X[2]), 1.0)
        self.assertEqual(model.junk.getValue(model.X[2]), 1.0)

        self.assertEqual(model.junk_w_default.getValue(model.x), 0.0)
        self.assertTrue(model.junk.getValue(model.x) is None)

        for suf in (model.junk_w_default,model.junk):
            suf.setValue(model.x,3.0)
            suf.setValue(model.X[2],3.0)

        for suf in (model.junk_w_default,model.junk):
            self.assertEqual(suf.getValue(model.X), 1.0)
            self.assertEqual(suf.getValue(model.X[1]), 2.0)
            self.assertEqual(suf.getValue(model.X[2]), 3.0)
            self.assertEqual(suf.getValue(model.x), 3.0)

    # test setValue and getValue and the use of default
    # and if the search hierarchy correctly interacts with Constraint
    def test_setValue_getValue_Constraint(self):
        model = ConcreteModel()
        model.junk_w_default = Suffix(default=0.0)
        model.junk = Suffix()
        model.x = Var()
        model.X = Var([1,2,3])
        model.c = Constraint(expr=model.x>=1)
        model.C = Constraint([1,2,3],expr=lambda model,i: model.X[i]>=1)

        for suf in (model.junk_w_default,model.junk):
            suf.setValue(model.C,1.0)
            suf.setValue(model.C[1],2.0)

        for suf in (model.junk_w_default,model.junk):
            self.assertEqual(suf.getValue(model.C), 1.0)
            self.assertEqual(suf.getValue(model.C[1]), 2.0)

        self.assertEqual(model.junk_w_default.getValue(model.C[2]), 1.0)
        self.assertEqual(model.junk.getValue(model.C[2]), 1.0)

        self.assertEqual(model.junk_w_default.getValue(model.c), 0.0)
        self.assertTrue(model.junk.getValue(model.c) is None)

        for suf in (model.junk_w_default,model.junk):
            suf.setValue(model.c,3.0)
            suf.setValue(model.C[2],3.0)

        for suf in (model.junk_w_default,model.junk):
            self.assertEqual(suf.getValue(model.C), 1.0)
            self.assertEqual(suf.getValue(model.C[1]), 2.0)
            self.assertEqual(suf.getValue(model.C[2]), 3.0)
            self.assertEqual(suf.getValue(model.c), 3.0)

    # test setValue and getValue and the use of default
    # and if the search hierarchy correctly interacts with Objective
    def test_setValue_getValue_Objective(self):
        model = ConcreteModel()
        model.junk_w_default = Suffix(default=0.0)
        model.junk = Suffix()
        model.x = Var()
        model.X = Var([1,2,3])
        model.obj = Objective(expr=summation(model.X)+model.x)
        model.OBJ = Objective([1,2,3],expr=lambda model,i: model.X[i])

        for suf in (model.junk_w_default,model.junk):
            suf.setValue(model.OBJ,1.0)
            suf.setValue(model.OBJ[1],2.0)

        for suf in (model.junk_w_default,model.junk):
            self.assertEqual(suf.getValue(model.OBJ), 1.0)
            self.assertEqual(suf.getValue(model.OBJ[1]), 2.0)

        self.assertEqual(model.junk_w_default.getValue(model.OBJ[2]), 1.0)
        self.assertEqual(model.junk.getValue(model.OBJ[2]), 1.0)

        self.assertEqual(model.junk_w_default.getValue(model.obj), 0.0)
        self.assertTrue(model.junk.getValue(model.obj) is None)

        for suf in (model.junk_w_default,model.junk):
            suf.setValue(model.obj,3.0)
            suf.setValue(model.OBJ[2],3.0)

        for suf in (model.junk_w_default,model.junk):
            self.assertEqual(suf.getValue(model.OBJ), 1.0)
            self.assertEqual(suf.getValue(model.OBJ[1]), 2.0)
            self.assertEqual(suf.getValue(model.OBJ[2]), 3.0)
            self.assertEqual(suf.getValue(model.obj), 3.0)

    # test setValue and getValue and the use of default
    # and if the search hierarchy correctly interacts with Param
    def Xtest_setValue_getValue_Param(self):
        model = ConcreteModel()
        model.junk_w_default = Suffix(default=0.0)
        model.junk = Suffix()
        model.x = Var()
        model.X = Var([1,2,3])
        model.p = Param(initialize=1.0,mutable=True)
        model.P = Param([1,2,3],initialize=1.0,mutable=True)

        for suf in (model.junk_w_default,model.junk):
            suf.setValue(model.P,1.0)
            suf.setValue(model.P[1],2.0)

        for suf in (model.junk_w_default,model.junk):
            self.assertEqual(suf.getValue(model.P), 1.0)
            self.assertEqual(suf.getValue(model.P[1]), 2.0)

        self.assertEqual(model.junk_w_default.getValue(model.P[2]), 1.0)
        self.assertEqual(model.junk.getValue(model.P[2]), 1.0)

        self.assertEqual(model.junk_w_default.getValue(model.p), 0.0)
        self.assertTrue(model.junk.getValue(model.p) is None)

        for suf in (model.junk_w_default,model.junk):
            suf.setValue(model.p,3.0)
            suf.setValue(model.P[2],3.0)

        for suf in (model.junk_w_default,model.junk):
            self.assertEqual(suf.getValue(model.P), 1.0)
            self.assertEqual(suf.getValue(model.P[1]), 2.0)
            self.assertEqual(suf.getValue(model.P[2]), 3.0)
            self.assertEqual(suf.getValue(model.p), 3.0)

    # test setValue and getValue and the use of default
    # and if the search hierarchy correctly interacts with Set
    def Xtest_setValue_getValue_Set(self):
        model = ConcreteModel()
        model.junk_w_default = Suffix(default=0.0)
        model.junk = Suffix()
        model.x = Var()
        model.X = Var([1,2,3])
        model.s = Set(initialize=[1,2,3])
        model.S = Set([1,2,3],initialize={1:[1,2,3],2:[1,2,3],3:[1,2,3]})

        for suf in (model.junk_w_default,model.junk):
            suf.setValue(model.S,1.0)
            suf.setValue(model.S[1],2.0)

        for suf in (model.junk_w_default,model.junk):
            self.assertEqual(suf.getValue(model.S), 1.0)
            self.assertEqual(suf.getValue(model.S[1]), 2.0)

        self.assertEqual(model.junk_w_default.getValue(model.S[2]), 1.0)
        self.assertEqual(model.junk.getValue(model.S[2]), 1.0)

        self.assertEqual(model.junk_w_default.getValue(model.s), 0.0)
        self.assertTrue(model.junk.getValue(model.s) is None)

        for suf in (model.junk_w_default,model.junk):
            suf.setValue(model.s,3.0)
            suf.setValue(model.S[2],3.0)

        for suf in (model.junk_w_default,model.junk):
            self.assertEqual(suf.getValue(model.S), 1.0)
            self.assertEqual(suf.getValue(model.S[1]), 2.0)
            self.assertEqual(suf.getValue(model.S[2]), 3.0)
            self.assertEqual(suf.getValue(model.s), 3.0)

    # test setValue and getValue and the use of default
    # and if the search hierarchy correctly interacts with Block
    def test_setValue_getValue_Block(self):
        model = ConcreteModel()
        model.junk_w_default = Suffix(default=0.0)
        model.junk = Suffix()
        model.b = Block()
        model.B = Block([1,2,3])

        for suf in (model.junk_w_default,model.junk):
            suf.setValue(model.B,1.0)
            suf.setValue(model.B[1],2.0)

        for suf in (model.junk_w_default,model.junk):
            self.assertEqual(suf.getValue(model.B), 1.0)
            self.assertEqual(suf.getValue(model.B[1]), 2.0)

        self.assertEqual(model.junk_w_default.getValue(model.B[2]), 1.0)
        self.assertEqual(model.junk.getValue(model.B[2]), 1.0)

        self.assertEqual(model.junk_w_default.getValue(model.b), 0.0)
        self.assertTrue(model.junk.getValue(model.b) is None)

        for suf in (model.junk_w_default,model.junk):
            suf.setValue(model.b,3.0)
            suf.setValue(model.B[2],3.0)

        for suf in (model.junk_w_default,model.junk):
            self.assertEqual(suf.getValue(model.B), 1.0)
            self.assertEqual(suf.getValue(model.B[1]), 2.0)
            self.assertEqual(suf.getValue(model.B[2]), 3.0)
            self.assertEqual(suf.getValue(model.b), 3.0)

    # Test that trying to call setValue with something
    # not compatable with the suffix dataype will fail
    def test_setValue_badcast(self):
        model = ConcreteModel()
        model.junk_w_default = Suffix(default=0.0)
        model.junk = Suffix()
        model.X = Var()
        try:
            model.junk_w_default.setValue(model.X,'a')
        except ValueError:
            pass
        else:
            self.fail("Trying to set the value to something not castable to the suffix datatype should fail.")

        try:
            model.junk.setValue(model.X,'a')
        except ValueError:
            pass
        else:
            self.fail("Trying to set the value to something not castable to the suffix datatype should fail.")

    # test setValue with no component argument
    def test_setValue_nocomponent(self):
        model = ConcreteModel()
        model.junk_w_default = Suffix(default=0.0)
        model.junk = Suffix()
        model.x = Var()
        model.y = Var([1,2,3])
        model.z = Var([1,2,3])

        model.junk_w_default.setValue(model.y[2],1.0)
        model.junk.setValue(model.y[2],1.0)
        model.junk_w_default.setValue(model.z,2.0)
        model.junk.setValue(model.z,2.0)
        
        self.assertEqual(model.junk_w_default.getValue(model.x), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.y), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.y[1]), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.y[2]), 1.0)
        self.assertEqual(model.junk_w_default.getValue(model.z), 2.0)
        self.assertEqual(model.junk_w_default.getValue(model.z[1]), 2.0)

        self.assertTrue(model.junk.getValue(model.x) is None)
        self.assertTrue(model.junk.getValue(model.y) is None)
        self.assertTrue(model.junk.getValue(model.y[1]) is None)
        self.assertEqual(model.junk.getValue(model.y[2]), 1.0)
        self.assertEqual(model.junk.getValue(model.z), 2.0)
        self.assertEqual(model.junk.getValue(model.z[1]), 2.0)
        
        model.junk_w_default.setValue(3.0)
        model.junk.setValue(3.0)

        self.assertEqual(model.junk_w_default.getDefault(), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.x), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.y), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.y[1]), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.y[2]), 3.0)
        self.assertEqual(model.junk_w_default.getValue(model.z), 3.0)
        self.assertEqual(model.junk_w_default.getValue(model.z[1]), 3.0)

        self.assertTrue(model.junk.getDefault() is None)
        self.assertTrue(model.junk.getValue(model.x) is None)
        self.assertTrue(model.junk.getValue(model.y) is None)
        self.assertTrue(model.junk.getValue(model.y[1]) is None)
        self.assertEqual(model.junk.getValue(model.y[2]), 3.0)
        self.assertEqual(model.junk.getValue(model.z), 3.0)
        self.assertEqual(model.junk.getValue(model.z[1]), 3.0)

        try:
            model.junk_w_default.setValue('a')
        except ValueError:
            pass
        else:
            self.fail("Trying to set the value to something not castable to the suffix datatype should fail.")

        try:
            model.junk.setValue('a')
        except ValueError:
            pass
        else:
            self.fail("Trying to set the value to something not castable to the suffix datatype should fail.")

    # test updateValues
    def test_updateValues(self):
        model = ConcreteModel()
        model.junk = Suffix()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.junk.setValue(model.x,0.0)
        self.assertEqual(model.junk.getValue(model.x),0.0)
        self.assertEqual(model.junk.getValue(model.y),None)
        self.assertEqual(model.junk.getValue(model.z),None)
        model.junk.updateValues([(model.x,1.0),(model.y,2.0),(model.z,3.0)])
        self.assertEqual(model.junk.getValue(model.x),1.0)
        self.assertEqual(model.junk.getValue(model.y),2.0)
        self.assertEqual(model.junk.getValue(model.z),3.0)


    # test clearValue 
    def test_clearValue(self):
        model = ConcreteModel()
        model.junk_w_default = Suffix(default=0.0)
        model.junk = Suffix()
        model.x = Var()
        model.y = Var([1,2,3])
        model.z = Var([1,2,3])

        model.junk_w_default.setValue(model.x,-1.0)
        model.junk.setValue(model.x,-1.0)
        model.junk_w_default.setValue(model.y,-2.0)
        model.junk.setValue(model.y,-2.0)
        model.junk_w_default.setValue(model.y[2],1.0)
        model.junk.setValue(model.y[2],1.0)
        model.junk_w_default.setValue(model.z,2.0)
        model.junk.setValue(model.z,2.0)
        model.junk_w_default.setValue(model.z[1],4.0)
        model.junk.setValue(model.z[1],4.0)
        
        self.assertEqual(model.junk_w_default.getValue(model.x), -1.0)
        self.assertEqual(model.junk_w_default.getValue(model.y), -2.0)
        self.assertEqual(model.junk_w_default.getValue(model.y[1]), -2.0)
        self.assertEqual(model.junk_w_default.getValue(model.y[2]), 1.0)
        self.assertEqual(model.junk_w_default.getValue(model.z), 2.0)
        self.assertEqual(model.junk_w_default.getValue(model.z[1]), 4.0)

        self.assertTrue(model.junk.getValue(model.x) == -1.0)
        self.assertTrue(model.junk.getValue(model.y) == -2.0)
        self.assertTrue(model.junk.getValue(model.y[1]) == -2.0)
        self.assertEqual(model.junk.getValue(model.y[2]), 1.0)
        self.assertEqual(model.junk.getValue(model.z), 2.0)
        self.assertEqual(model.junk.getValue(model.z[1]), 4.0)

        model.junk_w_default.clearValue(model.x)
        model.junk_w_default.clearValue(model.y)
        model.junk_w_default.clearValue(model.z[1])
        model.junk.clearValue(model.y)
        model.junk.clearValue(model.x)
        model.junk.clearValue(model.z[1])

        self.assertEqual(model.junk_w_default.getValue(model.x), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.y), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.y[1]), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.y[2]), 1.0)
        self.assertEqual(model.junk_w_default.getValue(model.z), 2.0)
        self.assertEqual(model.junk_w_default.getValue(model.z[1]), 2.0)

        self.assertTrue(model.junk.getValue(model.x) is None)
        self.assertTrue(model.junk.getValue(model.y) is None)
        self.assertTrue(model.junk.getValue(model.y[1]) is None)
        self.assertEqual(model.junk.getValue(model.y[2]), 1.0)
        self.assertEqual(model.junk.getValue(model.z), 2.0)
        self.assertEqual(model.junk.getValue(model.z[1]), 2.0)

    # test clearValue no args
    def test_clearValue_noargs(self):
        model = ConcreteModel()
        model.junk_w_default = Suffix(default=0.0)
        model.junk = Suffix()
        model.x = Var()
        model.y = Var([1,2,3])
        model.z = Var([1,2,3])

        model.junk_w_default.setValue(model.y[2],1.0)
        model.junk.setValue(model.y[2],1.0)
        model.junk_w_default.setValue(model.z,2.0)
        model.junk.setValue(model.z,2.0)
        
        self.assertEqual(model.junk_w_default.getValue(model.x), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.y), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.y[1]), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.y[2]), 1.0)
        self.assertEqual(model.junk_w_default.getValue(model.z), 2.0)
        self.assertEqual(model.junk_w_default.getValue(model.z[1]), 2.0)

        self.assertTrue(model.junk.getValue(model.x) is None)
        self.assertTrue(model.junk.getValue(model.y) is None)
        self.assertTrue(model.junk.getValue(model.y[1]) is None)
        self.assertEqual(model.junk.getValue(model.y[2]), 1.0)
        self.assertEqual(model.junk.getValue(model.z), 2.0)
        self.assertEqual(model.junk.getValue(model.z[1]), 2.0)

        model.junk_w_default.clearValue()
        model.junk.clearValue()

        self.assertEqual(model.junk_w_default.getValue(model.x), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.y), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.y[1]), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.y[2]), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.z), 0.0)
        self.assertEqual(model.junk_w_default.getValue(model.z[1]), 0.0)

        self.assertTrue(model.junk.getValue(model.x) is None)
        self.assertTrue(model.junk.getValue(model.y) is None)
        self.assertTrue(model.junk.getValue(model.y[1]) is None)
        self.assertTrue(model.junk.getValue(model.y[2]) is None)
        self.assertTrue(model.junk.getValue(model.z) is None)
        self.assertTrue(model.junk.getValue(model.z[1]) is None)

    # test setTable and getTable
    def test_setTable_getTable(self):
        model = ConcreteModel()
        try:
            model.junk = Suffix(datatype=str)
        except ValueError:
            pass
        else:
            self.fail("Initializing a symbolic (str) suffix without a table should fail")

        model.junk = Suffix()
        try:
            model.junk.setDatatype(str)
        except ValueError:
            pass
        else:
            self.fail("Providing no table to a symbolic (str) suffix should fail")
        del model.junk

        model.junk = Suffix(datatype=str,table={'a':1})
        try:
            model.junk.setTable(None)
        except ValueError:
            pass
        else:
            self.fail("Providing no table to a symbolic (str) suffix should fail")
        del model.junk

        tmp_dict = {'a':1,'b':2}
        model.junk = Suffix(datatype=str,table=copy.deepcopy(tmp_dict))
        self.assertEqual(tmp_dict, model.junk.getTable())

        new_tmp_dict = {'a':2,'c':1}
        new_tmp_dict_copy = copy.deepcopy(new_tmp_dict)
        model.junk.setTable(new_tmp_dict)
        self.assertEqual(new_tmp_dict_copy, model.junk.getTable())
        new_tmp_dict['d'] = 5
        self.assertEqual(new_tmp_dict_copy, model.junk.getTable())

    # test getReverseTable
    def test_getReverseTable(self):
        model = ConcreteModel()
        tmp_dict = {'a':1,'b':2}
        model.junk = Suffix(datatype=str,table=tmp_dict)
        self.assertEqual(tmp_dict, model.junk.getTable())
        self.assertEqual({1:'a',2:'b'}, model.junk.getReverseTable())

        tmp_dict = {'a':1,'b':2,'c':2}
        try:
            model.junk.setTable(tmp_dict)
        except:
            pass
        else:
            self.fail("Setting a noninvertable suffix table should fail.")

    # test calling setTable with a dictionary with bad datatypes for
    # the keys or the values
    def test_setTable_badtypes(self):
        model = ConcreteModel()
        try:
            model.junk = Suffix(table={1.0:1.0})
        except TypeError:
            pass
        else:
            self.fail("Trying to set a suffix table with non-integer type values should fail.")

        
        try:
            model.junk = Suffix(table={'a':1})
        except TypeError:
            pass
        else:
            self.fail("Trying to set a suffix table who's keys do not match the "\
                      "suffix datatype should fail.")

    # test setDatatype and getDatatype
    def test_setDatatype_getDatatype(self):
        model = ConcreteModel()
        model.junk = Suffix(datatype=float)
        self.assertTrue(model.junk.getDatatype() is float)
        model.junk.setDatatype(bool)
        self.assertTrue(model.junk.getDatatype() is bool)
        model.junk.setDatatype(int)
        self.assertTrue(model.junk.getDatatype() is int)
        model.junk.setDatatype(str,table={'a':1})
        self.assertTrue(model.junk.getDatatype() is str)

    # test that calling setDatatype with a bad value fails
    def test_setDatatype_badvalue(self):
        model = ConcreteModel()
        model.junk = Suffix()
        try:
            model.junk.setDatatype(1.0)
        except ValueError:
            pass
        else:
            self.fail("Calling setDatatype with a bad type should fail.")

    # test setDirection and getDirection
    def test_setDirection_getDirection(self):
        model = ConcreteModel()
        model.junk = Suffix(direction=Suffix.LOCAL)
        self.assertTrue(model.junk.getDirection() is Suffix.LOCAL)
        model.junk.setDirection(Suffix.EXPORT)
        self.assertTrue(model.junk.getDirection() is Suffix.EXPORT)
        model.junk.setDirection(Suffix.IMPORT)
        self.assertTrue(model.junk.getDirection() is Suffix.IMPORT)
        model.junk.setDirection(Suffix.IMPORT_EXPORT)
        self.assertTrue(model.junk.getDirection() is Suffix.IMPORT_EXPORT)
        
    # test setDefault and getDefault
    def test_setDefault_getDefault(self):
        model = ConcreteModel()
        model.junk = Suffix(default=1.0)
        self.assertEqual(model.junk.getDefault(), 1.0)
        model.junk.setDefault(2.0)
        self.assertEqual(model.junk.getDefault(), 2.0)
        try:
            model.junk.setDefault('a')
        except:
            pass
        else:
            self.fail("Trying to set the default value something not castable to the suffix datatype should faile.")

    # test that calling setDirection with a bad value fails
    def test_setDirection_badvalue(self):
        model = ConcreteModel()
        model.junk = Suffix()
        try:
            model.junk.setDirection('a')
        except ValueError:
            pass
        else:
            self.fail("Calling setDatatype with a bad type should fail.")    

    # test __str__
    def test_str(self):
        model = ConcreteModel()
        model.junk = Suffix()
        self.assertEqual(model.junk.__str__(), "junk")

    # test pprint()
    def test_pprint(self):
        model = ConcreteModel()
        model.junk = Suffix(default=1.0,direction=Suffix.EXPORT,table={1.0:1},datatype=float)
        output = StringIO()
        model.junk.pprint(ostream=output)
        model.junk.setDirection(Suffix.IMPORT)
        model.junk.pprint(ostream=output)
        model.junk.setDirection(Suffix.LOCAL)
        model.junk.pprint(ostream=output)
        model.junk.setDirection(Suffix.IMPORT_EXPORT)
        model.junk.pprint(ostream=output)
        model.pprint(ostream=output)

    # test pprint(verbose=True)
    def test_pprint_verbose(self):
        model = ConcreteModel()
        model.junk_w_default = Suffix(default=0.0)
        model.junk = Suffix()
        model.s = Block()
        model.s.b = Block()
        model.s.B = Block([1,2,3])

        for suf in (model.junk_w_default,model.junk):
            suf.setValue(model.s.B,1.0)
            suf.setValue(model.s.B[1],2.0)

        for suf in (model.junk_w_default,model.junk):
            suf.setValue(model.s.b,3.0)
            suf.setValue(model.s.B[2],3.0)

        output = StringIO()
        model.junk_w_default.pprint(ostream=output,verbose=True)
        model.junk.pprint(ostream=output,verbose=True)
        model.pprint(ostream=output,verbose=True)

    def test_active_export_suffix_generator(self):
        model = ConcreteModel()
        model.junk_EXPORT_int = Suffix(direction=Suffix.EXPORT,datatype=int)
        model.junk_EXPORT_float = Suffix(direction=Suffix.EXPORT,datatype=float)
        model.junk_IMPORT_EXPORT_float = Suffix(direction=Suffix.IMPORT_EXPORT,datatype=float)
        model.junk_IMPORT = Suffix(direction=Suffix.IMPORT,datatype=None)
        model.junk_LOCAL = Suffix(direction=Suffix.LOCAL,datatype=None)

        suffixes = dict(active_export_suffix_generator(model))
        self.assertTrue('junk_EXPORT_int' in suffixes)
        self.assertTrue('junk_EXPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)
        self.assertTrue('junk_LOCAL' not in suffixes)

        model.junk_EXPORT_float.deactivate()
        suffixes = dict(active_export_suffix_generator(model))
        self.assertTrue('junk_EXPORT_int' in suffixes)
        self.assertTrue('junk_EXPORT_float' not in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)
        self.assertTrue('junk_LOCAL' not in suffixes)
        model.junk_EXPORT_float.activate()

        suffixes = dict(active_export_suffix_generator(model,datatype=float))
        self.assertTrue('junk_EXPORT_int' not in suffixes)
        self.assertTrue('junk_EXPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)
        self.assertTrue('junk_LOCAL' not in suffixes)

        model.junk_EXPORT_float.deactivate()
        suffixes = dict(active_export_suffix_generator(model,datatype=float))
        self.assertTrue('junk_EXPORT_int' not in suffixes)
        self.assertTrue('junk_EXPORT_float' not in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)
        self.assertTrue('junk_LOCAL' not in suffixes)

    def test_export_suffix_generator(self):
        model = ConcreteModel()
        model.junk_EXPORT_int = Suffix(direction=Suffix.EXPORT,datatype=int)
        model.junk_EXPORT_float = Suffix(direction=Suffix.EXPORT,datatype=float)
        model.junk_IMPORT_EXPORT_float = Suffix(direction=Suffix.IMPORT_EXPORT,datatype=float)
        model.junk_IMPORT = Suffix(direction=Suffix.IMPORT,datatype=None)
        model.junk_LOCAL = Suffix(direction=Suffix.LOCAL,datatype=None)

        suffixes = dict(export_suffix_generator(model))
        self.assertTrue('junk_EXPORT_int' in suffixes)
        self.assertTrue('junk_EXPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)
        self.assertTrue('junk_LOCAL' not in suffixes)

        model.junk_EXPORT_float.deactivate()
        suffixes = dict(export_suffix_generator(model))
        self.assertTrue('junk_EXPORT_int' in suffixes)
        self.assertTrue('junk_EXPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)
        self.assertTrue('junk_LOCAL' not in suffixes)
        model.junk_EXPORT_float.activate()

        suffixes = dict(export_suffix_generator(model,datatype=float))
        self.assertTrue('junk_EXPORT_int' not in suffixes)
        self.assertTrue('junk_EXPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)
        self.assertTrue('junk_LOCAL' not in suffixes)

        model.junk_EXPORT_float.deactivate()
        suffixes = dict(export_suffix_generator(model,datatype=float))
        self.assertTrue('junk_EXPORT_int' not in suffixes)
        self.assertTrue('junk_EXPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)
        self.assertTrue('junk_LOCAL' not in suffixes)

    def test_active_import_suffix_generator(self):
        model = ConcreteModel()
        model.junk_IMPORT_int = Suffix(direction=Suffix.IMPORT,datatype=int)
        model.junk_IMPORT_float = Suffix(direction=Suffix.IMPORT,datatype=float)
        model.junk_IMPORT_EXPORT_float = Suffix(direction=Suffix.IMPORT_EXPORT,datatype=float)
        model.junk_EXPORT = Suffix(direction=Suffix.EXPORT,datatype=None)
        model.junk_LOCAL = Suffix(direction=Suffix.LOCAL,datatype=None)

        suffixes = dict(active_import_suffix_generator(model))
        self.assertTrue('junk_IMPORT_int' in suffixes)
        self.assertTrue('junk_IMPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT_float' in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_LOCAL' not in suffixes)

        model.junk_IMPORT_float.deactivate()
        suffixes = dict(active_import_suffix_generator(model))
        self.assertTrue('junk_IMPORT_int' in suffixes)
        self.assertTrue('junk_IMPORT_float' not in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT_float' in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_LOCAL' not in suffixes)
        model.junk_IMPORT_float.activate()

        suffixes = dict(active_import_suffix_generator(model,datatype=float))
        self.assertTrue('junk_IMPORT_int' not in suffixes)
        self.assertTrue('junk_IMPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT_float' in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_LOCAL' not in suffixes)

        model.junk_IMPORT_float.deactivate()
        suffixes = dict(active_import_suffix_generator(model,datatype=float))
        self.assertTrue('junk_IMPORT_int' not in suffixes)
        self.assertTrue('junk_IMPORT_float' not in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT_float' in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_LOCAL' not in suffixes)

    def test_import_suffix_generator(self):
        model = ConcreteModel()
        model.junk_IMPORT_int = Suffix(direction=Suffix.IMPORT,datatype=int)
        model.junk_IMPORT_float = Suffix(direction=Suffix.IMPORT,datatype=float)
        model.junk_IMPORT_EXPORT_float = Suffix(direction=Suffix.IMPORT_EXPORT,datatype=float)
        model.junk_EXPORT = Suffix(direction=Suffix.EXPORT,datatype=None)
        model.junk_LOCAL = Suffix(direction=Suffix.LOCAL,datatype=None)

        suffixes = dict(import_suffix_generator(model))
        self.assertTrue('junk_IMPORT_int' in suffixes)
        self.assertTrue('junk_IMPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT_float' in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_LOCAL' not in suffixes)

        model.junk_IMPORT_float.deactivate()
        suffixes = dict(import_suffix_generator(model))
        self.assertTrue('junk_IMPORT_int' in suffixes)
        self.assertTrue('junk_IMPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT_float' in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_LOCAL' not in suffixes)
        model.junk_IMPORT_float.activate()

        suffixes = dict(import_suffix_generator(model,datatype=float))
        self.assertTrue('junk_IMPORT_int' not in suffixes)
        self.assertTrue('junk_IMPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT_float' in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_LOCAL' not in suffixes)

        model.junk_IMPORT_float.deactivate()
        suffixes = dict(import_suffix_generator(model,datatype=float))
        self.assertTrue('junk_IMPORT_int' not in suffixes)
        self.assertTrue('junk_IMPORT_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT_float' in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_LOCAL' not in suffixes)

    def test_active_local_suffix_generator(self):
        model = ConcreteModel()
        model.junk_LOCAL_int = Suffix(direction=Suffix.LOCAL,datatype=int)
        model.junk_LOCAL_float = Suffix(direction=Suffix.LOCAL,datatype=float)
        model.junk_IMPORT_EXPORT = Suffix(direction=Suffix.IMPORT_EXPORT,datatype=None)
        model.junk_EXPORT = Suffix(direction=Suffix.EXPORT,datatype=None)
        model.junk_IMPORT = Suffix(direction=Suffix.IMPORT,datatype=None)

        suffixes = dict(active_local_suffix_generator(model))
        self.assertTrue('junk_LOCAL_int' in suffixes)
        self.assertTrue('junk_LOCAL_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT' not in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)

        model.junk_LOCAL_float.deactivate()
        suffixes = dict(active_local_suffix_generator(model))
        self.assertTrue('junk_LOCAL_int' in suffixes)
        self.assertTrue('junk_LOCAL_float' not in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT' not in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)
        model.junk_LOCAL_float.activate()

        suffixes = dict(active_local_suffix_generator(model,datatype=float))
        self.assertTrue('junk_LOCAL_int' not in suffixes)
        self.assertTrue('junk_LOCAL_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT' not in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)

        model.junk_LOCAL_float.deactivate()
        suffixes = dict(active_local_suffix_generator(model,datatype=float))
        self.assertTrue('junk_LOCAL_int' not in suffixes)
        self.assertTrue('junk_LOCAL_float' not in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT' not in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)

    def test_local_suffix_generator(self):
        model = ConcreteModel()
        model.junk_LOCAL_int = Suffix(direction=Suffix.LOCAL,datatype=int)
        model.junk_LOCAL_float = Suffix(direction=Suffix.LOCAL,datatype=float)
        model.junk_IMPORT_EXPORT = Suffix(direction=Suffix.IMPORT_EXPORT,datatype=None)
        model.junk_EXPORT = Suffix(direction=Suffix.EXPORT,datatype=None)
        model.junk_IMPORT = Suffix(direction=Suffix.IMPORT,datatype=None)

        suffixes = dict(local_suffix_generator(model))
        self.assertTrue('junk_LOCAL_int' in suffixes)
        self.assertTrue('junk_LOCAL_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT' not in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)

        model.junk_LOCAL_float.deactivate()
        suffixes = dict(local_suffix_generator(model))
        self.assertTrue('junk_LOCAL_int' in suffixes)
        self.assertTrue('junk_LOCAL_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT' not in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)
        model.junk_LOCAL_float.activate()

        suffixes = dict(local_suffix_generator(model,datatype=float))
        self.assertTrue('junk_LOCAL_int' not in suffixes)
        self.assertTrue('junk_LOCAL_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT' not in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)

        model.junk_LOCAL_float.deactivate()
        suffixes = dict(local_suffix_generator(model,datatype=float))
        self.assertTrue('junk_LOCAL_int' not in suffixes)
        self.assertTrue('junk_LOCAL_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT' not in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)

    def test_active_suffix_generator(self):
        model = ConcreteModel()
        model.junk_LOCAL_int = Suffix(direction=Suffix.LOCAL,datatype=int)
        model.junk_LOCAL_float = Suffix(direction=Suffix.LOCAL,datatype=float)
        model.junk_IMPORT_EXPORT = Suffix(direction=Suffix.IMPORT_EXPORT,datatype=None)
        model.junk_EXPORT = Suffix(direction=Suffix.EXPORT,datatype=None)
        model.junk_IMPORT = Suffix(direction=Suffix.IMPORT,datatype=None)

        suffixes = dict(active_suffix_generator(model))
        self.assertTrue('junk_LOCAL_int' in suffixes)
        self.assertTrue('junk_LOCAL_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT' in suffixes)
        self.assertTrue('junk_EXPORT' in suffixes)
        self.assertTrue('junk_IMPORT' in suffixes)

        model.junk_LOCAL_float.deactivate()
        suffixes = dict(active_suffix_generator(model))
        self.assertTrue('junk_LOCAL_int' in suffixes)
        self.assertTrue('junk_LOCAL_float' not in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT' in suffixes)
        self.assertTrue('junk_EXPORT' in suffixes)
        self.assertTrue('junk_IMPORT' in suffixes)
        model.junk_LOCAL_float.activate()

        suffixes = dict(active_suffix_generator(model,datatype=float))
        self.assertTrue('junk_LOCAL_int' not in suffixes)
        self.assertTrue('junk_LOCAL_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT' not in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)

        model.junk_LOCAL_float.deactivate()
        suffixes = dict(active_suffix_generator(model,datatype=float))
        self.assertTrue('junk_LOCAL_int' not in suffixes)
        self.assertTrue('junk_LOCAL_float' not in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT' not in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)

    def test_suffix_generator(self):
        model = ConcreteModel()
        model.junk_LOCAL_int = Suffix(direction=Suffix.LOCAL,datatype=int)
        model.junk_LOCAL_float = Suffix(direction=Suffix.LOCAL,datatype=float)
        model.junk_IMPORT_EXPORT = Suffix(direction=Suffix.IMPORT_EXPORT,datatype=None)
        model.junk_EXPORT = Suffix(direction=Suffix.EXPORT,datatype=None)
        model.junk_IMPORT = Suffix(direction=Suffix.IMPORT,datatype=None)

        suffixes = dict(suffix_generator(model))
        self.assertTrue('junk_LOCAL_int' in suffixes)
        self.assertTrue('junk_LOCAL_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT' in suffixes)
        self.assertTrue('junk_EXPORT' in suffixes)
        self.assertTrue('junk_IMPORT' in suffixes)

        model.junk_LOCAL_float.deactivate()
        suffixes = dict(suffix_generator(model))
        self.assertTrue('junk_LOCAL_int' in suffixes)
        self.assertTrue('junk_LOCAL_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT' in suffixes)
        self.assertTrue('junk_EXPORT' in suffixes)
        self.assertTrue('junk_IMPORT' in suffixes)
        model.junk_LOCAL_float.activate()

        suffixes = dict(suffix_generator(model,datatype=float))
        self.assertTrue('junk_LOCAL_int' not in suffixes)
        self.assertTrue('junk_LOCAL_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT' not in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)

        model.junk_LOCAL_float.deactivate()
        suffixes = dict(suffix_generator(model,datatype=float))
        self.assertTrue('junk_LOCAL_int' not in suffixes)
        self.assertTrue('junk_LOCAL_float' in suffixes)
        self.assertTrue('junk_IMPORT_EXPORT' not in suffixes)
        self.assertTrue('junk_EXPORT' not in suffixes)
        self.assertTrue('junk_IMPORT' not in suffixes)

    def test_reset(self):
        model = ConcreteModel()
        model.x = Var()
        model.y = Var()
        model.junk_no_rule = Suffix()
        self.assertEqual(model.junk_no_rule.getValue(model.x),None)
        self.assertEqual(model.junk_no_rule.getValue(model.y),None)
        model.junk_no_rule.setValue(model.x,1)
        model.junk_no_rule.setValue(model.y,2)
        self.assertEqual(model.junk_no_rule.getValue(model.x),1)
        self.assertEqual(model.junk_no_rule.getValue(model.y),2)
        model.junk_no_rule.reset()
        self.assertEqual(model.junk_no_rule.getValue(model.x),None)
        self.assertEqual(model.junk_no_rule.getValue(model.y),None)
        
        del model.junk_no_rule

        def _junk_rule(model):
            model.junk_rule.setValue(model.x,1)
        model.junk_rule = Suffix(rule=_junk_rule)
        self.assertEqual(model.junk_rule.getValue(model.x),1)
        self.assertEqual(model.junk_rule.getValue(model.y),None)
        model.junk_rule.setValue(model.y,2)
        self.assertEqual(model.junk_rule.getValue(model.x),1)
        self.assertEqual(model.junk_rule.getValue(model.y),2)
        model.junk_rule.reset()
        self.assertEqual(model.junk_rule.getValue(model.x),1)
        self.assertEqual(model.junk_rule.getValue(model.y),None)

class TestSuffixCloneUsage(unittest.TestCase):

    def test_clone_VarElement(self):
        model = ConcreteModel()
        model.x = Var()
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.x),None)
        model.junk.setValue(model.x,1.0)
        self.assertEqual(model.junk.getValue(model.x),1.0)
        inst = model.clone()
        self.assertEqual(inst.junk.getValue(model.x),None)
        self.assertEqual(inst.junk.getValue(inst.x),1.0)

    def test_clone_VarArray(self):
        model = ConcreteModel()
        model.x = Var([1,2,3])
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.x),None)
        model.junk.setValue(model.x,1.0)
        self.assertEqual(model.junk.getValue(model.x),1.0)
        inst = model.clone()
        self.assertEqual(inst.junk.getValue(model.x),None)
        self.assertEqual(inst.junk.getValue(inst.x),1.0)

    def test_clone_VarData(self):
        model = ConcreteModel()
        model.x = Var([1,2,3])
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.x[1]),None)
        model.junk.setValue(model.x[1],1.0)
        self.assertEqual(model.junk.getValue(model.x[1]),1.0)
        inst = model.clone()
        self.assertEqual(inst.junk.getValue(model.x[1]),None)
        self.assertEqual(inst.junk.getValue(inst.x[1]),1.0)

    def test_clone_ConstraintElement(self):
        model = ConcreteModel()
        model.x = Var()
        model.c = Constraint(expr=model.x == 1.0)
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.c),None)
        model.junk.setValue(model.c,1.0)
        self.assertEqual(model.junk.getValue(model.c),1.0)
        inst = model.clone()
        self.assertEqual(inst.junk.getValue(model.c),None)
        self.assertEqual(inst.junk.getValue(inst.c),1.0)

    def test_clone_ConstraintArray(self):
        model = ConcreteModel()
        model.x = Var([1,2,3])
        model.c = Constraint([1,2,3],expr=lambda model,i: model.x[i] == 1.0)
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.c),None)
        model.junk.setValue(model.c,1.0)
        self.assertEqual(model.junk.getValue(model.c),1.0)
        inst = model.clone()
        self.assertEqual(inst.junk.getValue(model.c),None)
        self.assertEqual(inst.junk.getValue(inst.c),1.0)

    def test_clone_ConstraintData(self):
        model = ConcreteModel()
        model.x = Var([1,2,3])
        model.c = Constraint([1,2,3],expr=lambda model,i: model.x[i] == 1.0)
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.c[1]),None)
        model.junk.setValue(model.c[1],1.0)
        self.assertEqual(model.junk.getValue(model.c[1]),1.0)
        inst = model.clone()
        self.assertEqual(inst.junk.getValue(model.c[1]),None)
        self.assertEqual(inst.junk.getValue(inst.c[1]),1.0)

    def test_clone_ObjectiveElement(self):
        model = ConcreteModel()
        model.x = Var()
        model.obj = Objective(expr=model.x)
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.obj),None)
        model.junk.setValue(model.obj,1.0)
        self.assertEqual(model.junk.getValue(model.obj),1.0)
        inst = model.clone()
        self.assertEqual(inst.junk.getValue(model.obj),None)
        self.assertEqual(inst.junk.getValue(inst.obj),1.0)

    def test_clone_ObjectiveArray(self):
        model = ConcreteModel()
        model.x = Var([1,2,3])
        model.obj = Objective([1,2,3],expr=lambda model,i: model.x[i])
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.obj),None)
        model.junk.setValue(model.obj,1.0)
        self.assertEqual(model.junk.getValue(model.obj),1.0)
        inst = model.clone()
        self.assertEqual(inst.junk.getValue(model.obj),None)
        self.assertEqual(inst.junk.getValue(inst.obj),1.0)

    def test_clone_ObjectiveData(self):
        model = ConcreteModel()
        model.x = Var([1,2,3])
        model.obj = Objective([1,2,3],expr=lambda model,i: model.x[i])
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.obj[1]),None)
        model.junk.setValue(model.obj[1],1.0)
        self.assertEqual(model.junk.getValue(model.obj[1]),1.0)
        inst = model.clone()
        self.assertEqual(inst.junk.getValue(model.obj[1]),None)
        self.assertEqual(inst.junk.getValue(inst.obj[1]),1.0)

    def test_clone_SingletonBlock(self):
        model = ConcreteModel()
        model.b = Block()
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.b),None)
        model.junk.setValue(model.b,1.0)
        self.assertEqual(model.junk.getValue(model.b),1.0)
        inst = model.clone()
        self.assertEqual(inst.junk.getValue(model.b),None)
        self.assertEqual(inst.junk.getValue(inst.b),1.0)

    def test_clone_IndexedBlock(self):
        model = ConcreteModel()
        model.b = Block([1,2,3])
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.b),None)
        model.junk.setValue(model.b,1.0)
        self.assertEqual(model.junk.getValue(model.b),1.0)
        inst = model.clone()
        self.assertEqual(inst.junk.getValue(model.b),None)
        self.assertEqual(inst.junk.getValue(inst.b),1.0)

    def test_clone_BlockData(self):
        model = ConcreteModel()
        model.b = Block([1,2,3])
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.b[1]),None)
        model.junk.setValue(model.b[1],1.0)
        self.assertEqual(model.junk.getValue(model.b[1]),1.0)
        inst = model.clone()
        self.assertEqual(inst.junk.getValue(model.b[1]),None)
        self.assertEqual(inst.junk.getValue(inst.b[1]),1.0)

    def test_clone_model(self):
        model = ConcreteModel()
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model),None)
        model.junk.setValue(model,1.0)
        self.assertEqual(model.junk.getValue(model),1.0)
        inst = model.clone()
        self.assertEqual(inst.junk.getValue(model),None)
        self.assertEqual(inst.junk.getValue(inst),1.0)

class TestSuffixPickleUsage(unittest.TestCase):

    def test_pickle_VarElement(self):
        model = ConcreteModel()
        model.x = Var()
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.x),None)
        model.junk.setValue(model.x,1.0)
        self.assertEqual(model.junk.getValue(model.x),1.0)
        inst = pickle.loads(pickle.dumps(model))
        self.assertEqual(inst.junk.getValue(model.x),None)
        self.assertEqual(inst.junk.getValue(inst.x),1.0)

    def test_pickle_VarArray(self):
        model = ConcreteModel()
        model.x = Var([1,2,3])
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.x),None)
        model.junk.setValue(model.x,1.0)
        self.assertEqual(model.junk.getValue(model.x),1.0)
        inst = pickle.loads(pickle.dumps(model))
        self.assertEqual(inst.junk.getValue(model.x),None)
        self.assertEqual(inst.junk.getValue(inst.x),1.0)

    def test_pickle_VarData(self):
        model = ConcreteModel()
        model.x = Var([1,2,3])
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.x[1]),None)
        model.junk.setValue(model.x[1],1.0)
        self.assertEqual(model.junk.getValue(model.x[1]),1.0)
        inst = pickle.loads(pickle.dumps(model))
        self.assertEqual(inst.junk.getValue(model.x[1]),None)
        self.assertEqual(inst.junk.getValue(inst.x[1]),1.0)

    def test_pickle_ConstraintElement(self):
        model = ConcreteModel()
        model.x = Var()
        model.c = Constraint(expr=model.x == 1.0)
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.c),None)
        model.junk.setValue(model.c,1.0)
        self.assertEqual(model.junk.getValue(model.c),1.0)
        inst = pickle.loads(pickle.dumps(model))
        self.assertEqual(inst.junk.getValue(model.c),None)
        self.assertEqual(inst.junk.getValue(inst.c),1.0)

    def test_pickle_ConstraintArray(self):
        model = ConcreteModel()
        model.x = Var([1,2,3])
        model.c = Constraint([1,2,3],rule=simple_con_rule)
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.c),None)
        model.junk.setValue(model.c,1.0)
        self.assertEqual(model.junk.getValue(model.c),1.0)
        inst = pickle.loads(pickle.dumps(model))
        self.assertEqual(inst.junk.getValue(model.c),None)
        self.assertEqual(inst.junk.getValue(inst.c),1.0)

    def test_pickle_ConstraintData(self):
        model = ConcreteModel()
        model.x = Var([1,2,3])
        model.c = Constraint([1,2,3],rule=simple_con_rule)
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.c[1]),None)
        model.junk.setValue(model.c[1],1.0)
        self.assertEqual(model.junk.getValue(model.c[1]),1.0)
        inst = pickle.loads(pickle.dumps(model))
        self.assertEqual(inst.junk.getValue(model.c[1]),None)
        self.assertEqual(inst.junk.getValue(inst.c[1]),1.0)

    def test_pickle_ObjectiveElement(self):
        model = ConcreteModel()
        model.x = Var()
        model.obj = Objective(expr=model.x)
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.obj),None)
        model.junk.setValue(model.obj,1.0)
        self.assertEqual(model.junk.getValue(model.obj),1.0)
        inst = pickle.loads(pickle.dumps(model))
        self.assertEqual(inst.junk.getValue(model.obj),None)
        self.assertEqual(inst.junk.getValue(inst.obj),1.0)

    def test_pickle_ObjectiveArray(self):
        model = ConcreteModel()
        model.x = Var([1,2,3])
        model.obj = Objective([1,2,3],rule=simple_obj_rule)
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.obj),None)
        model.junk.setValue(model.obj,1.0)
        self.assertEqual(model.junk.getValue(model.obj),1.0)
        inst = pickle.loads(pickle.dumps(model))
        self.assertEqual(inst.junk.getValue(model.obj),None)
        self.assertEqual(inst.junk.getValue(inst.obj),1.0)

    def test_pickle_ObjectiveData(self):
        model = ConcreteModel()
        model.x = Var([1,2,3])
        model.obj = Objective([1,2,3],rule=simple_obj_rule)
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.obj[1]),None)
        model.junk.setValue(model.obj[1],1.0)
        self.assertEqual(model.junk.getValue(model.obj[1]),1.0)
        inst = pickle.loads(pickle.dumps(model))
        self.assertEqual(inst.junk.getValue(model.obj[1]),None)
        self.assertEqual(inst.junk.getValue(inst.obj[1]),1.0)

    def test_pickle_SingletonBlock(self):
        model = ConcreteModel()
        model.b = Block()
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.b),None)
        model.junk.setValue(model.b,1.0)
        self.assertEqual(model.junk.getValue(model.b),1.0)
        inst = pickle.loads(pickle.dumps(model))
        self.assertEqual(inst.junk.getValue(model.b),None)
        self.assertEqual(inst.junk.getValue(inst.b),1.0)

    def test_pickle_IndexedBlock(self):
        model = ConcreteModel()
        model.b = Block([1,2,3])
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.b),None)
        model.junk.setValue(model.b,1.0)
        self.assertEqual(model.junk.getValue(model.b),1.0)
        inst = pickle.loads(pickle.dumps(model))
        self.assertEqual(inst.junk.getValue(model.b),None)
        self.assertEqual(inst.junk.getValue(inst.b),1.0)

    def test_pickle_BlockData(self):
        model = ConcreteModel()
        model.b = Block([1,2,3])
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model.b[1]),None)
        model.junk.setValue(model.b[1],1.0)
        self.assertEqual(model.junk.getValue(model.b[1]),1.0)
        inst = pickle.loads(pickle.dumps(model))
        self.assertEqual(inst.junk.getValue(model.b[1]),None)
        self.assertEqual(inst.junk.getValue(inst.b[1]),1.0)

    def test_pickle_model(self):
        model = ConcreteModel()
        model.junk = Suffix()
        self.assertEqual(model.junk.getValue(model),None)
        model.junk.setValue(model,1.0)
        self.assertEqual(model.junk.getValue(model),1.0)
        inst = pickle.loads(pickle.dumps(model))
        self.assertEqual(inst.junk.getValue(model),None)
        self.assertEqual(inst.junk.getValue(inst),1.0)


if __name__ == "__main__":
    unittest.main()
