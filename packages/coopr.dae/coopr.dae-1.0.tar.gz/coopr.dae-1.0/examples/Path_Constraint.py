# Sample Problem 3: Inequality State Path Constraint
# (Ex 4 from Dynopt Guide)
#
#	min x3(tf)
#	s.t.	X1_dot = X2		       X1(0) = 0
#		X2_dot = -X2+u		       X2(0) = -1
#		X3_dot = X1^2+x2^2+0.005*u^2   X3(0) = 0
#	        X2-8*(t-0.5)^2+0.5 <= 0		
#               tf = 1
#

from coopr.pyomo import *
from coopr.dae import *

m = ConcreteModel()
m.t = DifferentialSet(bounds=(0,1))
m.x1 = Var(m.t)
m.x2 = Var(m.t)
m.x3 = Var(m.t)
m.u = Var(m.t,initialize=0)

def _init_conditions(m, i):
	yield m.x1[0] == 0
	yield m.x2[0] == -1
        yield m.x3[0] == 0
	yield ConstraintList.End
m.init_conditions = ConstraintList(rule=_init_conditions)

def _x1dot(m,i):
    return m.x2[i]
m.x1dot = Differential(dv=m.x1,rule=_x1dot)

def _x2dot(m,i):
    return -m.x2[i]+m.u[i]
m.x2dot = Differential(dv=m.x2,rule=_x2dot)

def _x3dot(m,i):
    return m.x1[i]**2+m.x2[i]**2+0.005*m.u[i]**2
m.x3dot = Differential(dv=m.x3,rule=_x3dot)

def _con(m,i):
    return m.x2[i]-8*(float(i)-0.5)**2+0.5 <= 0
m.con = Constraint(m.t,rule=_con)

def _obj(m):
    return m.x3[1]
m.obj = Objective(rule=_obj)

