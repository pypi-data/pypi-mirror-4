from pymeigo import funcs
from rpy2.robjects import FloatVector

def test_func_rosen():
    a = funcs.rosen([1,2.])
    b = funcs.rosen_for_r(FloatVector([1,2]))
    assert a ==  b[0]


def test_example_unconstrained():
    a = funcs.example_unconstrained([1,1])
