from coopr.pyomo import *
from coopr.dae import *
from coopr.opt import SolverFactory
from coopr.dae.colloc import Collocation_Discretization
from distill_DAE import model

instance = model.create('distill.dat')
discretize = Collocation_Discretization(instance)
disc_instance = discretize.apply(nfe=50,ncp=3)

# The objective function in the original pyomo model that was discretized
# by hand iterated over all finite elements and all collocation points.
# Since the objective is not explicitly indexed by a diffset we add the 
# objective function to the model after it has been discretized to ensure
# that we include all the desired points in the diffset when we iterate.
def obj_rule(m):
    return m.alpha*sum((m.y[1,i] - m.y1_ref)**2 for i in m.t if i != 1) + m.rho*sum((m.u1[i] - m.u1_ref)**2 for i in m.t if i!=1)
disc_instance.OBJ = Objective(rule=obj_rule) 

solver='ipopt'
opt=SolverFactory(solver)

results = opt.solve(disc_instance,tee=True)
disc_instance.load(results)


# If you have matplotlib you can use the following code to plot the
# results
# t = [] 
# x5 = [] 
# x20 = []

#for i in instance.S_fe:
#    for j in instance.S_k:
#        if j is not instance.S_k.last():
#            x5.append(value(instance.x[5,i,j]))
#            x20.append(value(instance.x[20,i,j]))

#for i in sorted(disc_instance.t): 
#    if i in instance.t:
#        x5.append(value(disc_instance.x[5,i]))
#        x20.append(value(disc_instance.x[20,i]))
#        t.append(i)

#import matplotlib.pyplot as plt

#plt.plot(t,x5)
#plt.plot(t,x20)
#plt.show()
