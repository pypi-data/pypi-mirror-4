from pymeigo import essR, rosen_for_r, example_unconstrained_for_r
#from pymeigo import *

def test_rosen():
    essR(f=rosen_for_r, x_L=[-1,-1], x_U=[2,2])

def test_example_unconstrained():
    essR(f=example_unconstrained_for_r, x_L=[-1,-1], x_U=[2,2])
