from coopr.pyomo import *

PIECEWISE_PTS = [1,2,3]
F = lambda x: x**2

def define_model():
    model = ConcreteModel()

    def SOS_indices_init(model):
        return [i for i in xrange(1,len(PIECEWISE_PTS))]
    def ub_indices_init(model):
        return [i for i in xrange(1,len(PIECEWISE_PTS))]
    
    model.SOS_indices = Set(dimen=1, ordered=True, initialize=SOS_indices_init)
    model.ub_indices = Set(ordered=True, dimen=1,initialize=ub_indices_init)

    model.x = Var()
    model.Fx = Var()
    #Add SOS1 variable to model
    model.y = Var(model.ub_indices,within=NonNegativeReals)

    def constraint1_rule(model,i):
        return model.Fx - (F(PIECEWISE_PTS[i-1]) + ((F(PIECEWISE_PTS[i])-F(PIECEWISE_PTS[i-1]))/(PIECEWISE_PTS[i]-PIECEWISE_PTS[i-1]))*(model.x-PIECEWISE_PTS[i-1])) <= 25.0*(1-model.y[i])
    def constraint2_rule(model):
        return sum(model.y[j] for j in xrange(1,len(PIECEWISE_PTS))) == 1

    model.obj = Objective(expr=summation(model.Fx), sense=maximize)
    model.constraint1 = Constraint(model.ub_indices,rule=constraint1_rule)
    model.constraint2 = Constraint(rule=constraint2_rule)
    model.SOS_set_constraint = SOSConstraint(var=model.y, set=model.SOS_indices, sos=1)

    #Fix the answer for testing purposes
    model.set_answer_constraint1 = Constraint(expr= model.x == 2.5)

    return model

model = define_model()
