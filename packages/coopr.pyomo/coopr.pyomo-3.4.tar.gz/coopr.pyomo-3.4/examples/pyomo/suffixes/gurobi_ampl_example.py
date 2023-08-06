# A Suffix example for the gurobi_ampl solver.
#
# This Pyomo example is formulated as a python script.
# To run this script execute the following command:
#
# $ coopr_python gurobi_ampl_example.py
#
# Execution of this script requires that the gurobi_ampl
# solver is in the current search path for executables
# on this system. This example was tested using Gurobi
# Solver 5.0.0

from coopr.pyomo import *
from coopr.opt import SolverFactory

### Create the gurobi_ampl solver plugin using the ASL interface
solver = 'gurobi_ampl'
solver_io = 'nl'
stream_solver = False     # True prints solver output to screen
keepfiles =     False     # True prints intermediate file names (.nl,.sol,...) 
opt = SolverFactory(solver,solver_io=solver_io)
opt.options['outlev'] = 1 # tell gurobi to be verbose with output
###

### Create a trivial example model
model = ConcreteModel()
model.s = Set(initialize=[1,2,3])
model.x = Var(model.s,within=NonNegativeReals)
model.obj = Objective(expr=summation(model.x))
model.con = Constraint(model.s, expr=lambda model,i: model.x[i] >= i-1)
###

### Declare all suffixes
# The variable solution status suffix
# (this suffix can be sent to the solver and loaded from the solution)
model.sstatus = Suffix(direction=Suffix.IMPORT_EXPORT,
                       datatype=str,
                       table={'bas':1,   # basic
                              'sup':2,   # superbasic
                              'low':3,   # nonbasic <= (normally =) lower bound
                              'upp':4,   # nonbasic >= (normally =) upper bound
                              'equ':5,   # nonbasic at equal lower and upper bounds
                              'btw':6} ) # nonbasic between bounds
model.dual = Suffix(direction=Suffix.IMPORT_EXPORT)

# Report the best known bound on the objective function
model.bestbound = Suffix(direction=Suffix.IMPORT)

# A few Gurobi variable solution sensitivity suffixes
model.senslblo = Suffix(direction=Suffix.IMPORT) # smallest variable lower bound
model.senslbhi = Suffix(direction=Suffix.IMPORT) # greatest variable lower bound
model.sensublo = Suffix(direction=Suffix.IMPORT) # smallest variable upper bound
model.sensubhi = Suffix(direction=Suffix.IMPORT) # greatest variable upper bound

# A Gurobi constraint solution sensitivity suffix
model.sensrhshi = Suffix(direction=Suffix.IMPORT) # greatest right-hand side value
###

# Tell gurobi_ampl to report solution sensitivities
# and bestbound via suffixes in the solution file
opt.options['solnsens'] = 1
opt.options['bestbound'] = 1

# Set one of the sstatus suffix values, which will be sent to the solver
model.sstatus.setValue(model.x[1],'low')

def print_model_suffixes(model):
    # Print all suffix values for all model components in a nice table
    print "\t",
    for name,suffix in active_import_suffix_generator(model):
            print "%8s" % (name,),
    print
    for i in model.s:
        print model.x[i],"\t",
        for name,suffix in active_import_suffix_generator(model):
            print "%8s" % (suffix.getValue(model.x[i]),),
        print
    for i in model.s:
        print model.con[i],"\t",
        for name,suffix in active_import_suffix_generator(model):
            print "%8s" % (suffix.getValue(model.con[i]),),
        print
    print model.obj.name,"\t",
    for name,suffix in active_import_suffix_generator(model):
        print "%8s" % (suffix.getValue(model.obj),),
    print
    print

print 
print "Suffixes Before Solve:"
print_model_suffixes(model)

### Generate the constraint expression trees if necessary
if solver_io != 'nl':
    # only required when not using the ASL interface
    model.preprocess()
###

### Send the model to gurobi_ampl and collect the solution
# The solver plugin will scan the model for all active suffixes
# valid for importing, which it will store into the results object
results = opt.solve(model,
                    keepfiles=keepfiles,
                    tee=stream_solver)
# load the results (including any values for previously declared
# IMPORT / IMPORT_EXPORT Suffix components found in the results object)
model.load(results)
###

print 
print "Suffixes After Solve:"
print_model_suffixes(model)

