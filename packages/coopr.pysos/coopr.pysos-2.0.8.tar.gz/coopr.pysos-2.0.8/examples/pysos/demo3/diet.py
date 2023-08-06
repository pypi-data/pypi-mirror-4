#
# Imports
#
from coopr.pyomo import *

#
# Setup
#

model = AbstractModel()
model.NUTR = Set()
model.FOOD = Set()

model.new_cost = Param(within=NonNegativeReals, initialize=3.0)
model.cost = Param(model.FOOD, within=NonNegativeReals)

model.f_min = Param(model.FOOD, within=NonNegativeReals)

def f_max_valid (value, j, model):
    return model.f_max[j] > model.f_min[j]
model.f_max = Param(model.FOOD, validate=f_max_valid)

model.n_min = Param(model.NUTR, within=NonNegativeReals)

def paramn_max (i, model):
    model.n_max[i] > model.n_min[i]
    return model.n_max[i]
model.n_max = Param(model.NUTR, initialize=paramn_max)

# ***********************************

model.new_amt = Param(model.NUTR, within=NonNegativeReals, initialize=0)
model.amt = Param(model.NUTR, model.FOOD, within=NonNegativeReals)

model.new_Buy = Var(bounds=(0.0,100.0))
def Buy_bounds(i,model):
    return (model.f_min[i].value,model.f_max[i].value)
model.Buy = Var(model.FOOD, bounds=Buy_bounds)

def Objective_rule(model):
    ans = 0
    for j in model.FOOD:
        ans = ans + model.cost[j] * model.Buy[j]
    ans = ans + model.new_cost * model.new_Buy
    return ans
model.totalcost = Objective(rule=Objective_rule)

def Diet_rule(i, model):
    expr = 0
    for j in model.FOOD:
        expr = expr + model.amt[i,j] * model.Buy[j]
    expr = expr + model.new_amt[i] * model.new_Buy
    expr = expr > model.n_min[i]
    expr = expr < model.n_max[i]
    return expr
model.Diet = Constraint(model.NUTR, rule=Diet_rule)
