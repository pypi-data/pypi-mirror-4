import sys
import os
from os.path import abspath, dirname, basename, join
from six import itervalues
import pyutilib.th as unittest
from pyutilib.misc.pyyaml_util import *
from pyutilib.misc import Options
import pyutilib
import coopr.pyomo.scripting.util as util
import coopr.plugins
from coopr.pyomo.base import Var, active_subcomponents_data_generator

yaml_available=False
try:
    import yaml
    yaml_available = True
except: 
    pass


currdir = dirname( abspath(__file__) )
os.sys.path.append(currdir)

problem_list = ['multidimen_sos2','sos2','multidimen_sos1','sos1','sos1_no_index','sos2_no_index']

def module_available(module):
    try:
        __import__(module)
        return True
    except ImportError:
        return False

def has_python(name):
    if module_available(name):
        return True
    return False

def has_gurobi_lp():
    try:
        gurobi = coopr.plugins.solvers.GUROBI(keepfiles=True)
        available = (not gurobi.executable() is None) and gurobi.available(False)
        return available
    except pyutilib.common.ApplicationError:
        return False

def has_gurobi_nl():
    try:
        gurobi = coopr.plugins.solvers.GUROBI(keepfiles=True)
        available = (not gurobi.executable() is None) and gurobi.available(False)
        asl = coopr.plugins.solvers.ASL(keepfiles=True, options={'solver':'gurobi_ampl'})
        return available and (not asl.executable() is None) and asl.available(False)
    except pyutilib.common.ApplicationError:
        return False

def has_cplex_lp():
    try:
        cplex = coopr.plugins.solvers.CPLEX(keepfiles=True)
        available = (not cplex.executable() is None) and cplex.available(False)
        return available
    except pyutilib.common.ApplicationError:
        return False
    
def has_cbc_lp():
    try:
        cbc = coopr.plugins.solvers.CBC(keepfiles=True)
        available = (not cbc.executable() is None) and cbc.available(False)
        return available
    except pyutilib.common.ApplicationError:
        return False
    
def has_pico_lp():
    try:
        PICO = coopr.plugins.solvers.PICO(keepfiles=True)
        available = (not PICO.executable() is None) and PICO.available(False)
        return available
    except pyutilib.common.ApplicationError:
        return False

def has_cplex_nl():
    try:
        cplex = coopr.plugins.solvers.CPLEX(keepfiles=True)
        available = (not cplex.executable() is None) and cplex.available(False)
        asl = coopr.plugins.solvers.ASL(keepfiles=True, options={'solver':'cplexamp'})
        return available and (not asl.executable() is None) and asl.available(False)
    except pyutilib.common.ApplicationError:
        return False

def has_glpk_lp():
    try:
        glpk = coopr.plugins.solvers.GLPK(keepfiles=True)
        available = (not glpk.executable() is None) and glpk.available(False)
        return available
    except pyutilib.common.ApplicationError:
        return False

# Here we are trying to test every writer that handles sos constraints:
# (1) LP 
# (2) NL
# (3) CPLEXDirect
# (4) gurobi_direct
writer_solver = []
if has_python('cplex'):
    writer_solver.append(('python','cplex',True))
else:
    writer_solver.append(('python','cplex',False))

if has_python('gurobipy'):
    writer_solver.append(('python','gurobi',True))
else:
    writer_solver.append(('python','gurobi',False))

if has_cplex_lp():
    writer_solver.append(('lp','cplex',True))
else:
    writer_solver.append(('lp','cplex',False))

if has_gurobi_lp():
    writer_solver.append(('lp','gurobi',True))
else:
    writer_solver.append(('lp','gurobi',False))
    
if has_cplex_nl():
    writer_solver.append(('nl','cplexamp',True))
else:
    writer_solver.append(('nl','cplexamp',False))
    
if has_gurobi_nl():
    writer_solver.append(('nl','gurobi_ampl',True))
else:
    writer_solver.append(('nl','gurobi_ampl',False))

def createTestMethod(pName,problem,solver,writer,do_test):
    
    
    message = solver+"_"+writer+" not available"
    
    @unittest.skipUnless(do_test,message)
    def testMethod(obj):
        # Since we are comparing solutions over different writers to a baseline,
        # we cannot use the .yml solution files as a basis. Therefore we must
        # check that individual variable values are the same. Currently, a 
        # pickled results object is used as the baseline solution.

        options = Options()
        options.solver = solver
        options.solver_io = writer
        options.quiet = True
        data = Options(options=options)

        model = obj.m[problem].define_model()
        instance = model.create()

        opt_data = util.apply_optimizer(data, instance=instance)
        
        instance.load(opt_data.results)
        
        baseline_results = obj.b[problem]
        
        for block in instance.all_blocks():
            for var in active_subcomponents_data_generator(block,Var):
                bF = baseline_results[var.cname()]
                F = var.value
                if abs(F-bF) > 0.000001:
                    raise IOError("Difference in baseline solution values and current solution values using:\n" + \
                                      "Problem: "+problem+".py\n" + \
                                      "Solver: "+solver+"\n" + \
                                      "Writer: "+writer+"\n" + \
                                      "Variable: "+name+"\n" + \
                                      "Solution: "+str(F)+"\n" + \
                                      "Baseline: "+str(bF)+"\n")

    return testMethod

def assignTests(cls):
    for PROBLEM in problem_list:
        for writer,solver,do_test in writer_solver:
            attrName = "test_sos_{0}_{1}_{2}".format(PROBLEM,solver,writer)
            setattr(cls,attrName,createTestMethod(attrName,PROBLEM,solver,writer,do_test))
            cls.m[PROBLEM] = __import__(PROBLEM)
            if yaml_available:
                with open(join(currdir,'baselines',PROBLEM+'_baseline_results.yml'),'r') as f:
                    baseline_results = yaml.load(f)
                    cls.b[PROBLEM] = baseline_results

@unittest.skipIf(writer_solver==[], "Can't find a solver.")
@unittest.skipUnless(yaml_available, "The PyYAML module is not available.")
class SOSTest(unittest.TestCase):
    m = {}
    b = {}

assignTests(SOSTest)

if __name__ == "__main__":
    unittest.main()
