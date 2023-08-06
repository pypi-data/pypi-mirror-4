from six import iteritems
import pyutilib
import coopr
from coopr.opt import SolverFactory

cplex_available = False
cplexamp_available = False
cplexpy_available = False
try:
    cplex = coopr.plugins.solvers.CPLEX(keepfiles=True)
    cplex_available = (not cplex.executable() is None) and cplex.available(False)
    asl = coopr.plugins.solvers.ASL(keepfiles=True, options={'solver':'cplexamp'})
    cplexamp_available = cplex_available and (not asl.executable() is None) and asl.available(False)
    try:
        import cplex
        cplexpy_available = True
    except ImportError:
        cplexpy_available = False
except pyutilib.common.ApplicationError:
    cplexamp_available=False

gurobi_available = False
gurobi_ampl_available = False
gurobipy_available = False
try:
    gurobi = coopr.plugins.solvers.GUROBI(keepfiles=True)
    gurobi_available = (not gurobi.executable() is None) and gurobi.available(False)
    asl = coopr.plugins.solvers.ASL(keepfiles=True, options={'solver':'gurobi_ampl'})
    gurobi_ampl_available = gurobi_available and (not asl.executable() is None) and asl.available(False)
    try:
        import gurobipy
        gurobipy_available = True
    except ImportError:
        gurobipy_available = False
except pyutilib.common.ApplicationError:
    gurobi_ampl_available=False

glpk_available = False
glpkpy_available = False
glpk_old = False
try:
    glpk = coopr.plugins.solvers.GLPK(keepfiles=True)
    glpk_available = (not glpk.executable() is None) and glpk.available(False)
    if 'GLPKSHELL_old' in str(glpk.__class__):
        glpk_old = True
    try:
        import glpk
        glpkpy_available = True
    except ImportError:
        glpkpy_available = False
except pyutilib.common.ApplicationError:
    pass

cbc_available = False
cbc_ampl_available = False
try:
    cbc = coopr.plugins.solvers.CBC(keepfiles=True)
    cbc_available = (not cbc.executable() is None) and cbc.available(False)
    cbc_ampl = coopr.plugins.solvers.CBC(keepfiles=True,solver_io='nl')
    cbc_ampl_available = (not cbc_ampl is None) and (not cbc_ampl.executable() is None) and cbc_ampl.available(False)
except pyutilib.common.ApplicationError:
    pass

pico_available = False
pico_ampl_available = False
try:
    pico = coopr.plugins.solvers.PICO(keepfiles=True)
    pico_available = (not pico.executable() is None) and pico.available(False)
    pico_ampl = coopr.plugins.solvers.PICO(keepfiles=True,solver_io='nl')
    pico_ampl_available = (not pico_ampl is None) and (not pico_ampl.executable() is None) and pico_ampl.available(False)
except pyutilib.common.ApplicationError:
    pass

xpress_available = False
try:
    xpress = coopr.plugins.solvers.XPRESS(keepfiles=True)
    xpress_available = (not xpress.executable() is None) and xpress.available(False)
except pyutilib.common.ApplicationError:
    pass

ipopt_available = False
try:
    asl = coopr.plugins.solvers.ASL(keepfiles=True, options={'solver':'ipopt'})
    ipopt_available = (not asl.executable() is None) and asl.available(False)
except pyutilib.common.ApplicationError:
    ipopt_available=False

scip_available = False
try:
    scip = coopr.plugins.solvers.SCIPAMPL(keepfiles=True)
    scip_available = (not scip.executable() is None) and scip.available(False)
except pyutilib.common.ApplicationError:
    scip_available = False

class SolverTestCase(object):

    def __init__(self,name=None,io=None,available=False,**kwds):
        assert (name is not None) and (type(name) is str)
        assert (io is not None) and (type(io) is str)
        assert (available in [True,False])
        self.name = name
        self.io = io
        self.available = available 
        self.capabilities = kwds.pop('capabilities',[])
        self.export_suffixes = kwds.pop('export_suffixes',[])
        self.import_suffixes = kwds.pop('import_suffixes',[])
        self.options = kwds.pop('options',{})
        assert type(self.capabilities) in [list,tuple]
        assert type(self.export_suffixes) in [list,tuple]
        assert type(self.import_suffixes) in [list,tuple]
        assert type(self.options) is dict
        for tag in self.capabilities:
            assert type(tag) is str
        for tag in self.export_suffixes:
            assert type(tag) is str
        for tag in self.import_suffixes:
            assert type(tag) is str
        self.solver = None

    def initialize(self):
        self.solver = None
        opt = SolverFactory(self.name,solver_io=self.io)
        if opt is not None:
            for key,value in iteritems(self.options):
                opt.options[key] = value
        self.solver = opt

    def has_capability(self,tag):
        if tag in self.capabilities:
            return True
        return False

    def __str__(self):
        tmp  = "SolverTestCase:\n"
        tmp += "\tname = "+self.name+"\n"
        tmp += "\tio = "+self.io+"\n"
        tmp += "\tavailable = "+str(self.available)+"\n"
        if self.solver is not None:
            tmp += "\tversion = "+str(self.solver.version())+"\n"
        else:
            tmp += "\tversion = unknown\n"
        tmp += "\tcapabilities: "
        if len(self.capabilities):
            tmp += "\n"
            for tag in self.capabilities:
                tmp += "\t   - "+tag+"\n"
        else:
            tmp += "None\n"
        tmp += "\tsuffixes: \n"
        tmp += "\t  export: "
        if len(self.export_suffixes):
            tmp += "\n"
            for tag in self.export_suffixes:
                tmp += "\t   - "+tag+"\n"
        else:
            tmp += "None\n"
        tmp += "\t  import: "
        if len(self.import_suffixes):
            tmp += "\n"
            for tag in self.import_suffixes:
                tmp += "\t   - "+tag+"\n"
        else:
            tmp += "None\n"
        return tmp
        

# The capabilities listed below should be what is
# advertised by the solver and not the Pyomo plugin
# But we are testing that they match
testCases = []

#
#    ADD CPLEX TEST CASES
#
cplex_capabilities = ['linear',
                      'integer',
                      'quadratic_objective',
                      'quadratic_constraint',
                      'sos1',
                      'sos2']
testCases.append( SolverTestCase(name='cplex',
                                 io='lp',
                                 capabilities=cplex_capabilities,
                                 import_suffixes=['slack'], #dual, rc
                                 available=cplex_available) )
testCases.append( SolverTestCase(name='cplexamp',
                                 io='nl',
                                 capabilities=cplex_capabilities,
                                 import_suffixes=[], #dual
                                 available=cplexamp_available) )
testCases.append( SolverTestCase(name='cplex',
                                 io='python',
                                 capabilities=cplex_capabilities,
                                 import_suffixes=['slack'], #dual, rc
                                 available=cplexpy_available) )


#
#    ADD GUROBI TEST CASES
#
gurobi_capabilities = ['linear',
                       'integer',
                       'quadratic_objective',
                       'quadratic_constraint',
                       'sos1',
                       'sos2']
# **NOTE: Gurobi does not handle quadratic constraints before
#         Major Version 5
testCases.append( SolverTestCase(name='gurobi',
                                 io='lp',
                                 capabilities=gurobi_capabilities,
                                 import_suffixes=['rc','dual','slack'],
                                 available=gurobi_available) )
testCases.append( SolverTestCase(name='gurobi_ampl',
                                 io='nl',
                                 capabilities=gurobi_capabilities,
                                 import_suffixes=['dual'],
                                 available=gurobi_ampl_available,
                                 options={'qcpdual':1,'simplex':1}) )
testCases.append( SolverTestCase(name='gurobi',
                                 io='python',
                                 capabilities=gurobi_capabilities,
                                 import_suffixes=['rc','dual','slack'],
                                 available=gurobipy_available) )

#
#    ADD GLPK TEST CASES
#
glpk_capabilities = ['linear',
                     'integer']
if glpk_old is True:
    glpk_import_suffixes = ['dual']
else:
    glpk_import_suffixes = ['rc','dual']
testCases.append( SolverTestCase(name='glpk',
                                 io='lp',
                                 capabilities=glpk_capabilities,
                                 import_suffixes=glpk_import_suffixes,
                                 available=glpk_available) )
testCases.append( SolverTestCase(name='glpk',
                                 io='python',
                                 capabilities=glpk_capabilities,
                                 import_suffixes=[],
                                 available=glpkpy_available) )


#
#    ADD CBC TEST CASES
#
cbc_capabilities = ['linear',
                    'integer']
testCases.append( SolverTestCase(name='cbc',
                                 io='lp',
                                 capabilities=cbc_capabilities,
                                 import_suffixes=['rc','dual'],
                                 available=cbc_available) )
testCases.append( SolverTestCase(name='cbc',
                                 io='nl',
                                 capabilities=cbc_capabilities,
                                 import_suffixes=['dual'],
                                 available=cbc_ampl_available) )

#
#    ADD PICO TEST CASES
#
pico_capabilities = ['linear',
                     'integer']
testCases.append( SolverTestCase(name='pico',
                                 io='lp',
                                 capabilities=pico_capabilities,
                                 import_suffixes=['dual'],
                                 available=pico_available) )
testCases.append( SolverTestCase(name='pico',
                                 io='nl',
                                 capabilities=pico_capabilities,
                                 import_suffixes=['dual'],
                                 available=pico_ampl_available) )

#
#    ADD XPRESS TEST CASES
#
xpress_capabilities = ['linear',
                     'integer',
                     'quadratic_objective',
                     'quadratic_constraint',
                     'sos1',
                     'sos2']
testCases.append( SolverTestCase(name='xpress',
                                 io='lp',
                                 capabilities=xpress_capabilities,
                                 import_suffixes=['rc','dual','slack'],
                                 available=xpress_available) )

#
#    ADD IPOPT TEST CASES
#
ipopt_capabilities = ['linear',
                      'quadratic_objective',
                      'quadratic_constraint']
testCases.append( SolverTestCase(name='ipopt',
                                 io='nl',
                                 capabilities=ipopt_capabilities,
                                 import_suffixes=['dual'],
                                 available=ipopt_available) )

#
#    ADD SCIP TEST CASES
#
scip_capabilities = ['linear',
                         'integer',
                         'quadratic_objective',
                         'quadratic_constraint',
#                         'sos1', # scip does not handle these currently, I've reported this bug to SCIP
                         'sos2']
testCases.append( SolverTestCase(name='scip',
                                 io='nl',
                                 capabilities=scip_capabilities,
                                 import_suffixes=[],
                                 available=scip_available) )


if __name__ == "__main__":

    for case in testCases:
        case.initialize()
        print(case)
