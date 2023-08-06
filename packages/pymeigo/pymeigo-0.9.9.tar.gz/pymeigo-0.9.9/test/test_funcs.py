from pymeigo import funcs
from rpy2.robjects import FloatVector

def test_func_rosen():
    a = funcs.rosen([1,2.])
    b = funcs.rosen_for_r(FloatVector([1,2]))
    assert a ==  b[0]


def test_test1():
    a = funcs.test1([1,1])
