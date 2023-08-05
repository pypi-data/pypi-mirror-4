#! /usr/bin/python
import numpy as np
import matplotlib.pyplot as plt
import pymt64 


n= 1000000

# initial seed value
seed=1

# initialisation:
# mt is the stage vector of the Mersenne Twister pseudorandom number generator
# in the case of multrithreading, one must have as many mt array as threads
mt = pymt64.init(seed)


# generating a uniform distribution
x = pymt64.uniform(mt,n)
plt.figure(0)
plt.clf()
plt.hist(x,bins=100)


xm= 10.
# generating a Poisson distribution
y = pymt64.poisson(mt,xm,n)
plt.figure(1)
plt.hist(y,bins=100)

# generating two independent Normal distributions
(u,v) = pymt64.normal(mt,n)
plt.figure(2)
plt.clf()
plt.hist(u,bins=100)

plt.show()


