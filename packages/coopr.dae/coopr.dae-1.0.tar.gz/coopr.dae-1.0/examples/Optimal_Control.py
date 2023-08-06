# Sample Problem 1 (Ex 1 from Dynopt Guide)
#
#	min X2(tf)
#	s.t.	X1_dot = u			X1(0) = 1
#		X2_dot = X1^2 + u^2		X2(0) = 0
#		tf = 1

from coopr.pyomo import *
from coopr.dae import *

model = ConcreteModel()
model.t = DifferentialSet(bounds=(0,1)) 
model.x1 = Var(model.t,bounds=(0,1))
model.x2 = Var(model.t,bounds=(0,1))
model.u = Var(model.t,initialize=0)

# Benefit of declaring initial conditions this way
# is that they are all in one spot
def _init_conditions(model, i):
	yield model.x1[0] == 1
	yield model.x2[0] == 0
	yield ConstraintList.End
model.init_conditions = ConstraintList(rule=_init_conditions)

# Alternate way for declaring initial conditions
#def _x1init(model):
#	return model.x1[0] == 1
#model.x1init = Constraint(rule=_x1init)

#def _x2init(model):
#	return model.x2[0] == 0
#model.x2init = Constraint(rule=_x2init)

def _x1dot(model,i):
	return model.u[i]		# The RHS of the DE
model.x1dot = Differential(dvar=model.x1, rule=_x1dot)

def _x2dot(model,i):
	return model.x1[i]**2 + model.u[i]**2
model.x2dot = Differential(dvar=model.x2, rule=_x2dot)

def _obj(model):
	return model.x2[1]
model.obj = Objective(rule=_obj,sense=minimize)

