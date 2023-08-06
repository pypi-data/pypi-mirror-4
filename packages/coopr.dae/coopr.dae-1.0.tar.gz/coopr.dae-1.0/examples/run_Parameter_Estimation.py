from coopr.pyomo import *
from coopr.dae import *
from coopr.opt import SolverFactory
from coopr.dae.impliciteuler import Implicit_Euler
from coopr.dae.colloc import Collocation_Discretization
from Parameter_Estimation import model

instance = model.create('data_set2.dat')
instance.t.pprint()
# Discretize model using Implicit Euler method
#discretize = Implicit_Euler()
#disc_instance = discretize.apply(instance,nfe=20)

# Discretize model using Orthogonal Collocation
discretize = Collocation_Discretization(instance)
disc_instance = discretize.apply(nfe=8,ncp=5)

solver='ipopt'
opt=SolverFactory(solver)

results = opt.solve(disc_instance,tee=True)
disc_instance.load(results)

x1 = []
x1_meas = []
t=[]
t_meas=[]

print sorted(disc_instance.t)

for i in sorted(disc_instance.MEAS_t):
    t_meas.append(i)
    x1_meas.append(value(disc_instance.x1_meas[i]))

for i in sorted(disc_instance.t):
    t.append(i)
    x1.append(value(disc_instance.x1[i]))
    
import matplotlib.pyplot as plt

plt.plot(t,x1)
plt.plot(t_meas,x1_meas,'o')
plt.show()
