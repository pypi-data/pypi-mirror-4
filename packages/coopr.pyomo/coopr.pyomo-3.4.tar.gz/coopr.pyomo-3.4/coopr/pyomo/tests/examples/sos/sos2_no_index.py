from coopr.pyomo import *

PIECEWISE_PTS = [1,2,3]
F = lambda x: x**2

def define_model():

    model = ConcreteModel()

    def SOS_indices_init(model):
        return [i for i in xrange(len(PIECEWISE_PTS))]
    def ub_indices_init(model):
        return [i for i in xrange(len(PIECEWISE_PTS))]
    
    model.SOS_indices = Set(dimen=1, ordered=True, initialize=SOS_indices_init)
    model.ub_indices = Set(ordered=True, dimen=1, initialize=ub_indices_init)

    model.x = Var()
    model.Fx = Var()
    #Add SOS2 variable to model
    model.y = Var(model.ub_indices,within=NonNegativeReals)

    def constraint1_rule(model):
        return model.x == sum(model.y[i]*PIECEWISE_PTS[i] for i in xrange(len(PIECEWISE_PTS)) )
    def constraint2_rule(model):
        return model.Fx == sum(model.y[i]*F(PIECEWISE_PTS[i]) for i in xrange(len(PIECEWISE_PTS)) )
    def constraint3_rule(model):
        return sum(model.y[j] for j in xrange(len(PIECEWISE_PTS))) == 1

    model.obj = Objective(expr=summation(model.Fx), sense=maximize)
    model.constraint1 = Constraint(rule=constraint1_rule)
    model.constraint2 = Constraint(rule=constraint2_rule)
    model.constraint3 = Constraint(rule=constraint3_rule)
    model.SOS_set_constraint = SOSConstraint(var=model.y, set=model.SOS_indices, sos=2)

    #Fix the answer for testing purposes
    model.set_answer_constraint1 = Constraint(expr= model.x == 2.5)

    return model

model = define_model()
