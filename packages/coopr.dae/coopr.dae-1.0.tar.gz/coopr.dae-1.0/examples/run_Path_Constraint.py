from coopr.pyomo import *
from coopr.dae import *
from coopr.opt import SolverFactory
from coopr.dae.colloc import Collocation_Discretization
from Path_Constraint import m

instance = m.create()

# Discretize model using Orthogonal Collocation
discretize = Collocation_Discretization(instance)
disc_instance=discretize.apply(nfe=7,ncp=6)

disc_instance = discretize.reduce_collocation_points(
    var=instance.u, ncp=1, diffset=instance.t)

solver='ipopt'
opt=SolverFactory(solver)

results = opt.solve(disc_instance, tee=True)
disc_instance.load(results)

#results = opt.solve(disc_instance,tee=True)

x1 = []
x2 = []
u = []
t=[]

for i in sorted(disc_instance.t):
    t.append(i)
    x1.append(value(disc_instance.x1[i]))
    x2.append(value(disc_instance.x2[i]))
    u.append(value(disc_instance.u[i]))

import matplotlib.pyplot as plt
plt.subplot(121)
plt.plot(t,x1)
plt.plot(t,x2,'r')
plt.legend(('x1','x2'))
plt.xlabel('t')
#plt.show()
plt.subplot(122)
plt.plot(t,u)
plt.plot(t,u,'o')
plt.xlabel('t')
plt.ylabel('u')
plt.show()
