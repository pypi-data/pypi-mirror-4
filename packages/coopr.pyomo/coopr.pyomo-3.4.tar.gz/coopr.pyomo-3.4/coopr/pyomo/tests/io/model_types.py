import os
from os.path import join, dirname, abspath

from coopr.pyomo import *

import json

thisDir = dirname(abspath( __file__ ))

class _ModelClassBase(object):
    """
    The base class for all model classifications
    """
    def __init__(self):
        self.linear = False
        self.integer = False
        self.quadratic_objective = False
        self.quadratic_constraint = False
        self.sos1 = False
        self.sos2 = False
        self.model = None
        self.results_file = None
        self.diff_tol = 1e-5

    def generateModel():
        raise NotImplementedError

    def saveCurrentSolution(self,filename,**kwds):
        assert self.model is not None
        model = self.model
        suffixes = dict((suffix,getattr(model,suffix)) for suffix in kwds.pop('suffixes',[]))
        for suf in suffixes.values():
            assert isinstance(suf,Suffix)
            assert suf.importEnabled() is True
        with open(filename,'w') as f:
            soln = {}
            for block in model.all_blocks():
                soln[block.cname(True)] = {}
                for suffix_name, suffix in suffixes.items():
                    if suffix.getValue(block) is not None:
                        soln[block.cname(True)][suffix_name] = suffix.getValue(block)
            for block in model.all_blocks():
                for var in active_subcomponents_data_generator(block,Var):
                    soln[var.cname(True)] = {}
                    soln[var.cname(True)]['value'] = value(var)
                    for suffix_name, suffix in suffixes.items():
                        if suffix.getValue(var) is not None:
                            soln[var.cname(True)][suffix_name] = suffix.getValue(var)
            for block in model.all_blocks():
                for con in active_subcomponents_data_generator(block,Constraint):
                    soln[con.cname(True)] = {}
                    soln[con.cname(True)]['value'] = con()
                    for suffix_name, suffix in suffixes.items():
                        if suffix.getValue(con) is not None:
                            soln[con.cname(True)][suffix_name] = suffix.getValue(con)
            for block in model.all_blocks():
                for obj in active_subcomponents_data_generator(block,Objective):
                    soln[obj.cname(True)] = {}
                    soln[obj.cname(True)]['value'] = value(obj)
                    for suffix_name, suffix in suffixes.items():
                        if suffix.getValue(obj) is not None:
                            soln[obj.cnaxme(True)][suffix_name] = suffix.getValue(obj)
            json.dump(soln, f, indent=2)

    def validateCurrentSolution(self,**kwds):
        assert self.model is not None
        assert self.results_file is not None
        model = self.model
        suffixes = dict((suffix,getattr(model,suffix)) for suffix in kwds.pop('suffixes',[]))
        for suf in suffixes.values():
            assert isinstance(suf,Suffix)
            assert suf.importEnabled() is True
        solution = None
        error_str = "Difference in solution for {0}.{1}:\n\tBaseline - {2}\n\tCurrent - {3}"
        with open(self.results_file,'r') as f:
            try:
                solution = json.load(f)
            except:
                return (False,"Problem reading file "+self.results_file)
        for block in model.all_blocks():
            for var in active_subcomponents_data_generator(block,Var):
                if not abs(solution[var.cname(True)]['value'] - value(var)) < self.diff_tol:
                    return (False, error_str.format(var.cname(True),'value',solution[var.cname(True)]['value'],value(var)))
                for suffix_name, suffix in suffixes.items():
                    if suffix_name in solution[var.cname(True)].keys():
                        if suffix.getValue(var) is None:
                            if not(solution[var.cname(True)][suffix_name] in solution["suffix defaults"][suffix_name]):
                                return (False, error_str.format(var.cname(True),suffix,solution[var.cname(True)][suffix_name],"none defined"))
                        elif not abs(solution[var.cname(True)][suffix_name] - suffix.getValue(var)) < self.diff_tol:
                            return (False, error_str.format(var.cname(True),suffix,solution[var.cname(True)][suffix_name],suffix.getValue(var)))
        for block in model.all_blocks():
            for con in active_subcomponents_data_generator(block,Constraint):
                if not abs(solution[con.cname(True)]['value'] - con()) < self.diff_tol:
                    return (False, error_str.format(con.cname(True),'value',solution[con.cname(True)]['value'],con()))
                for suffix_name, suffix in suffixes.items():
                    if suffix_name in solution[con.cname(True)].keys():
                        if suffix.getValue(con) is None:
                            if not (solution[con.cname(True)][suffix_name] in solution["suffix defaults"][suffix_name]):
                                return (False, error_str.format(con.cname(True),suffix,solution[con.cname(True)][suffix_name],"none defined"))
                        elif not abs(solution[con.cname(True)][suffix_name] - suffix.getValue(con)) < self.diff_tol:
                            return (False, error_str.format(con.cname(True),suffix,solution[con.cname(True)][suffix_name],suffix.getValue(con)))
        for block in model.all_blocks():
            for obj in active_subcomponents_data_generator(block,Objective):
                if not abs(solution[obj.cname(True)]['value'] - value(obj)) < self.diff_tol:
                    return (False, error_str.format(obj.cname(True),'value',solution[obj.cname(True)]['value'],value(obj)))
                for suffix_name, suffix in suffixes.items():
                    if suffix_name in solution[obj.cname(True)].keys(): 
                        if suffix.getValue(obj) is None:
                            if not(solution[obj.cname(True)][suffix_name] in solution["suffix defaults"][suffix_name]):
                                return (False, error_str.format(obj.cname(True),suffix,solution[obj.cname(True)][suffix_name],"none defined"))
                        elif not abs(solution[obj.cname(True)][suffix_name] - suffix.getValue(obj)) < self.diff_tol:
                            return (False, error_str.format(obj.cname(True),suffix,solution[obj.cname(True)][suffix_name],suffix.getValue(obj)))
        for block in model.all_blocks():
            for suffix_name, suffix in suffixes.items():
                if (solution[block.cname(True)] is not None) and (suffix in solution[block.cname(True)].keys()): 
                    if suffix.getValue(block) is None:
                        if not(solution[block.cname(True)][suffix_name] in solution["suffix defaults"][suffix_name]):
                            return (False, error_str.format(block.cname(True),suffix,solution[block.cname(True)][suffix_name],"none defined"))
                    elif not abs(solution[block.cname(True)][suffix_name] - suffix.getValue(block)) < sefl.diff_tol:
                        return (False, error_str.format(block.cname(True),suffix,solution[block.cname(True)][suffix_name],suffix.getValue(block)))
        return (True,"")
            
    def descrStr(self):
        raise NotImplementedError
    
    def validateCapabilities(self,opt):
        if (self.linear is True) and (not opt.has_capability('linear') is True):
            return False
        if (self.integer is True) and (not opt.has_capability('integer') is True):
            return False
        if (self.quadratic_objective is True) and (not opt.has_capability('quadratic_objective') is True):
            return False
        if (self.quadratic_constraint is True) and (not opt.has_capability('quadratic_constraint') is True):
            return False
        if (self.sos1 is True) and (not opt.has_capability('sos1') is True):
            return False
        if (self.sos2 is True) and (not opt.has_capability('sos2') is True):
            return False
        return True

class simple_LP(_ModelClassBase):
    """
    A continuous linear model
    """
    def __init__(self):
        _ModelClassBase.__init__(self)
        self.linear = True
        self.results_file = join(thisDir,"simple_LP.results")

    def descrStr(self):
        return "simple_LP"

    def generateModel(self):
        self.model = None
        self.model = ConcreteModel()
        model = self.model
        model.name = self.descrStr()
        
        model.a = Param(initialize=1.0)
        model.x = Var(within=NonNegativeReals)
        model.y = Var(within=NonNegativeReals)
        
        model.obj = Objective(expr=model.x + 3.0*model.y)
        model.c1 = Constraint(expr=model.a <= model.y)
        model.c2 = Constraint(expr=2.0 <= model.x/model.a - model.y <= 10)

class block_LP(_ModelClassBase):
    """
    A continuous linear model with nested blocks
    """
    def __init__(self):
        _ModelClassBase.__init__(self)
        self.linear = True
        self.results_file = join(thisDir,"block_LP.results")

    def descrStr(self):
        return "block_LP"

    def generateModel(self):
        self.model = None
        self.model = ConcreteModel()
        model = self.model
        model.name = self.descrStr()
        
        model.b = Block()
        model.B = Block([1,2,3])
        model.a = Param(initialize=1.0)
        model.b.x = Var(within=NonNegativeReals)
        model.B[1].x = Var(within=NonNegativeReals)
        
        model.obj = Objective(expr=model.b.x + 3.0*model.B[1].x)
        model.B[2].c = Constraint(expr=model.a <= model.B[1].x)
        model.B[3].c = Constraint(expr=2.0 <= model.b.x/model.a - model.B[1].x <= 10)

class inactive_index_LP(_ModelClassBase):
    """
    A continuous linear model where component subindices have been deactivated
    """
    def __init__(self):
        _ModelClassBase.__init__(self)
        self.linear = True
        self.results_file = join(thisDir,"inactive_index_LP.results")

    def descrStr(self):
        return "inactive_index_LP"

    def generateModel(self):
        self.model = None
        self.model = ConcreteModel()
        model = self.model
        model.name = self.descrStr()
        
        model.s = Set(initialize=[1,2])
        model.x = Var()
        model.y = Var()
        
        def obj_rule(model,i):
            if i == 1:
                return model.x-model.y
            else:
                return -model.x+model.y
        model.obj = Objective(model.s,rule=obj_rule)
        model.OBJ = Objective(expr=model.x+model.y)
        model.obj[1].deactivate()
        model.OBJ.deactivate()
        model.c1 = ConstraintList()
        model.c1.add(model.x<=1)   # index=1
        model.c1.add(model.x>=-1)  # index=2
        model.c1.add(model.y<=1)   # index=3
        model.c1.add(model.y>=-1)  # index=4
        model.c1[1].deactivate()
        model.c1[4].deactivate()
        def c2_rule(model,i):
            if i == 1:
                return model.y >= -2
            else:
                return model.x <= 2
        model.c2 = Constraint(model.s)

class simple_MILP(_ModelClassBase):
    """
    A mixed-integer linear model
    """
    def __init__(self):
        _ModelClassBase.__init__(self)
        self.linear = True
        self.integer = True
        self.results_file = join(thisDir,"simple_MILP.results")

    def descrStr(self):
        return "simple_MILP"

    def generateModel(self):
        self.model = None
        self.model = ConcreteModel()
        model = self.model
        model.name = self.descrStr()
    
        model.a = Param(initialize=1.0)
        model.x = Var(within=NonNegativeReals)
        model.y = Var(within=Binary)
        
        model.obj = Objective(expr=model.x + 3.0*model.y)
        model.c1 = Constraint(expr=model.a <= model.y)
        model.c2 = Constraint(expr=2.0 <= model.x/model.a - model.y <= 10)

class simple_QP(_ModelClassBase):
    """
    A continuous model with a quadratic objective and linear constraints
    """
    def __init__(self):
        _ModelClassBase.__init__(self)
        self.linear = True
        self.quadratic_objective = True
        self.results_file = join(thisDir,"simple_QP.results")

    def descrStr(self):
        return "simple_QP"

    def generateModel(self):
        self.model = None
        self.model = ConcreteModel()
        model = self.model
        model.name = self.descrStr()
        
        model.a = Param(initialize=1.0)
        model.x = Var(within=NonNegativeReals)
        model.y = Var(within=NonNegativeReals)
        
        model.obj = Objective(expr=model.x**2 + 3.0*model.y**2)
        model.c1 = Constraint(expr=model.a <= model.y)
        model.c2 = Constraint(expr=2.0 <= model.x/model.a - model.y <= 10)

class simple_MIQP(_ModelClassBase):
    """
    A mixed-integer model with a quadratic objective and linear constraints
    """
    def __init__(self):
        _ModelClassBase.__init__(self)
        self.linear = True
        self.integer = True
        self.quadratic_objective = True
        self.results_file = join(thisDir,"simple_MIQP.results")

    def descrStr(self):
        return "simple_MIQP"

    def generateModel(self):
        self.model = None
        self.model = ConcreteModel()
        model = self.model
        model.name = self.descrStr()
        
        model.a = Param(initialize=1.0)
        model.x = Var(within=NonNegativeReals)
        model.y = Var(within=Binary)
        
        model.obj = Objective(expr=model.x**2 + 3.0*model.y**2)
        model.c1 = Constraint(expr=model.a <= model.y)
        model.c2 = Constraint(expr=2.0 <= model.x/model.a - model.y <= 10)

class simple_QCP(_ModelClassBase):
    """
    A continuous model with a quadratic objective and quadratics constraints
    """
    def __init__(self):
        _ModelClassBase.__init__(self)
        self.linear = True
        self.quadratic_objective = True
        self.quadratic_constraint = True
        self.results_file = join(thisDir,"simple_QCP.results")

    def descrStr(self):
        return "simple_QCP"

    def generateModel(self):
        self.model = None
        self.model = ConcreteModel()
        model = self.model
        model.name = self.descrStr()

        model.x = Var(within=NonNegativeReals)
        model.y = Var(within=NonNegativeReals)
        model.z = Var(within=NonNegativeReals)

        model.obj = Objective(expr=model.x,sense=maximize)
        model.c0 = Constraint(expr=model.x+model.y+model.z == 1)
        model.qc0 = Constraint(expr=model.x**2 + model.y**2 <= model.z**2)
        model.qc1 = Constraint(expr=model.x**2 <= model.y*model.z)

class simple_MIQCP(_ModelClassBase):
    """
    A mixed-integer model with a quadratic objective and quadratic constraints
    """
    def __init__(self):
        _ModelClassBase.__init__(self)
        self.linear = True
        self.integer = True
        self.quadratic_objective = True
        self.quadratic_constraint = True
        self.results_file = join(thisDir,"simple_MIQCP.results")

    def descrStr(self):
        return "simple_MIQCP"

    def generateModel(self):
        self.model = None
        self.model = ConcreteModel()
        model = self.model
        model.name = self.descrStr()

        model.x = Var(within=Binary)
        model.y = Var(within=Binary)
        model.z = Var(within=Binary)

        model.obj = Objective(expr=model.x,sense=maximize)
        model.c0 = Constraint(expr=model.x+model.y+model.z == 1)
        model.qc0 = Constraint(expr=model.x**2 + model.y**2 <= model.z**2)
        model.qc1 = Constraint(expr=model.x**2 <= model.y*model.z)

class simple_SOS1(_ModelClassBase):
    """
    A discrete linear model with sos1 constraints
    """
    def __init__(self):
        _ModelClassBase.__init__(self)
        self.linear = True
        self.integer = True
        self.sos1 = True
        self.results_file = join(thisDir,"simple_SOS1.results")

    def descrStr(self):
        return "simple_SOS1"

    def generateModel(self):
        self.model = None
        self.model = ConcreteModel()
        model = self.model
        model.name = self.descrStr()

        model.a = Param(initialize=0.1)
        model.x = Var(within=NonNegativeReals)
        model.y = Var([1,2],within=NonNegativeReals)
        
        model.obj = Objective(expr=model.x + model.y[1]+2*model.y[2])
        model.c1 = Constraint(expr=model.a <= model.y[2])
        model.c2 = Constraint(expr=2.0 <= model.x <= 10.0)
        model.c3 = SOSConstraint(var=model.y, set=[1,2], sos=1)
        model.c4 = Constraint(expr=summation(model.y) == 1)

class simple_SOS2(_ModelClassBase):
    """
    A discrete linear model with sos2 constraints
    """
    def __init__(self):
        _ModelClassBase.__init__(self)
        self.linear = True
        self.integer = True
        self.sos2 = True
        self.results_file = join(thisDir,"simple_SOS2.results")

    def descrStr(self):
        return "simple_SOS2"

    def generateModel(self):
        self.model = None
        self.model = ConcreteModel()
        model = self.model
        model.name = self.descrStr()

        model.f = Var()
        model.x = Var(bounds=(1,3))
        model.fi = Param([1,2,3],mutable=True)
        model.fi[1] = 1.0
        model.fi[2] = 2.0
        model.fi[3] = 0.0
        model.xi = Param([1,2,3],mutable=True)
        model.xi[1] = 1.0
        model.xi[2] = 2.0
        model.xi[3] = 3.0
        model.p = Var(within=NonNegativeReals)
        model.n = Var(within=NonNegativeReals)
        model.lmbda = Var([1,2,3])
        model.obj = Objective(expr=model.p+model.n)
        model.c1 = ConstraintList()
        model.c1.add(0.0 <= model.lmbda[1] <= 1.0)
        model.c1.add(0.0 <= model.lmbda[2] <= 1.0)
        model.c1.add(0.0 <= model.lmbda[3])
        model.c2 = SOSConstraint(var=model.lmbda, set=[1,2,3], sos=2)
        model.c3 = Constraint(expr=summation(model.lmbda) == 1)
        model.c4 = Constraint(expr=model.f==summation(model.fi,model.lmbda))
        model.c5 = Constraint(expr=model.x==summation(model.xi,model.lmbda))
        model.x = 2.75
        model.x.fixed = True

class duals_maximize(_ModelClassBase):
    """
    A discrete linear model with sos2 constraints
    """
    def __init__(self):
        _ModelClassBase.__init__(self)
        self.linear = True
        self.results_file = join(thisDir,"duals_maximize.results")

    def descrStr(self):
        return "duals_maximize"

    def generateModel(self):
        self.model = None
        self.model = ConcreteModel()
        model = self.model
        model.name = self.descrStr()

        model.x = Var(RangeSet(1,12))
        model.x[1].setlb(-1)
        model.x[1].setub(1)
        model.x[2].setlb(-1)
        model.x[2].setub(1)
        model.obj = Objective(expr=sum(model.x[i]*((-1)**(i)) for i in model.x.index_set()),sense=maximize)
        model.c = ConstraintList()
        # to make the variable used in the constraint match the name
        model.c.add(Constraint.Skip)
        model.c.add(Constraint.Skip)
        model.c.add(model.x[3]>=-1.)
        model.c.add(model.x[4]<=1.)
        model.c.add(model.x[5]==-1.)
        model.c.add(model.x[6]==-1.)
        model.c.add(model.x[7]==1.)
        model.c.add(model.x[8]==1.)
        model.c.add((-1.,model.x[9],-1.))
        model.c.add((-1.,model.x[10],-1.))
        model.c.add((1.,model.x[11],1.))
        model.c.add((1.,model.x[12],1.))

        model.c_inactive = ConstraintList()
        # to make the variable used in the constraint match the name
        model.c_inactive.add(Constraint.Skip)
        model.c_inactive.add(Constraint.Skip)
        model.c_inactive.add(model.x[3]>=-2.)
        model.c_inactive.add(model.x[4]<=2.)

class duals_minimize(_ModelClassBase):
    """
    A discrete linear model with sos2 constraints
    """
    def __init__(self):
        _ModelClassBase.__init__(self)
        self.linear = True
        self.results_file = join(thisDir,"duals_minimize.results")

    def descrStr(self):
        return "duals_minimize"

    def generateModel(self):
        self.model = None
        self.model = ConcreteModel()
        model = self.model
        model.name = self.descrStr()

        model.x = Var(RangeSet(1,12))
        model.x[1].setlb(-1)
        model.x[1].setub(1)
        model.x[2].setlb(-1)
        model.x[2].setub(1)
        model.obj = Objective(expr=sum(model.x[i]*((-1)**(i+1)) for i in model.x.index_set()))
        model.c = ConstraintList()
        # to make the variable used in the constraint match the name
        model.c.add(Constraint.Skip)
        model.c.add(Constraint.Skip)
        model.c.add(model.x[3]>=-1.)
        model.c.add(model.x[4]<=1.)
        model.c.add(model.x[5]==-1.)
        model.c.add(model.x[6]==-1.)
        model.c.add(model.x[7]==1.)
        model.c.add(model.x[8]==1.)
        model.c.add((-1.,model.x[9],-1.))
        model.c.add((-1.,model.x[10],-1.))
        model.c.add((1.,model.x[11],1.))
        model.c.add((1.,model.x[12],1.))

        model.c_inactive = ConstraintList()
        # to make the variable used in the constraint match the name
        model.c_inactive.add(Constraint.Skip)
        model.c_inactive.add(Constraint.Skip)
        model.c_inactive.add(model.x[3]>=-2.)
        model.c_inactive.add(model.x[4]<=2.)

if __name__ == "__main__":
    from coopr.opt import *
    M = simple_QP()
    M.generateModel()
    model = M.model
    model.dual = Suffix(direction=Suffix.IMPORT)
    model.rc = Suffix(direction=Suffix.IMPORT)
    #model.slack = Suffix(direction=Suffix.IMPORT)

    model.preprocess()
    model.write(format=None,filename="junk.nl",symbolic_solver_labels=True)
    
    opt = SolverFactory("cplexamp")
    
    
    
    results = opt.solve(model)#,keepfiles=True,symbolic_solver_labels=True,tee=True)
    
    #print(results)
    #print(model.update_results(results))
    #model.load(results)
    #M.saveCurrentSolution("junk",suffixes=['dual','rc','slack'])
    #print(M.validateCurrentSolution(suffixes=['dual','rc','slack']))


