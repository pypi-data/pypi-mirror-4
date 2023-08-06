from coopr.pyomo import *
from coopr.dae import *
from coopr.opt import SolverFactory
from coopr.dae.impliciteuler import Implicit_Euler
from coopr.dae.colloc import Collocation_Discretization
from Optimal_Control import model

instance = model.create()

# Discretize model using Implicit Euler method
discretize = Implicit_Euler(instance)
disc_instance = discretize.apply(nfe=20)

# Discretize model using Orthogonal Collocation
#discretize = Collocation_Discretization(instance)
#discretize.apply(nfe=10,ncp=5)
#disc_instance = discretize.reduce_collocation_points(var=instance.u,
#	ncp=2, diffset=instance.t)

solver='ipopt'
opt=SolverFactory(solver)

results = opt.solve(disc_instance,tee=True)
disc_instance.load(results)

x1 = []
x2 = []
u = []
t=[]

print sorted(disc_instance.t)

for i in sorted(disc_instance.t):
    t.append(i)
    x1.append(value(disc_instance.x1[i]))
    x2.append(value(disc_instance.x2[i]))
    u.append(value(disc_instance.u[i]))

import matplotlib.pyplot as plt

plt.plot(t,x1)
plt.plot(t,x2)
plt.show()

plt.plot(t,u)
plt.show()
