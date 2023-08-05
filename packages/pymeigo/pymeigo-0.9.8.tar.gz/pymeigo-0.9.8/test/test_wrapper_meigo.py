from pymeigo import essR, rosen_for_r, test1_for_r
#from pymeigo import *

def test_rosen():
    essR(f=rosen_for_r, x_L=[-1,-1], x_U=[2,2])

def _test_test1():
    essR(f=test1_for_r, x_L=[-1,-1], x_U=[2,2])
