from rpy2.robjects.vectors import FloatVector
from rpy2.robjects.packages import importr
import rpy2.rinterface as ri
#stats = importr('stats')


__all__ = ["pyfunc2R", "rosen", "test1", "rosen_for_r", "test1_for_r"]


def pyfunc2R(f):
    """Converts a python function into a R object

    ::

        def f(x,y):
            return x+y

        f4r = pyfunc2R(f)
    """
    fr = ri.rternalize(f)
    return fr

# Rosenbrock Banana function as a cost function
# (as in the R man page for optim())
def rosen(x):
    """Rosenbrock Banana function as a cost function
     (as in the R man page for optim())
    """
    x1 = x[0]
    x2 = x[1]
    return 100 * (x2 - x1 * x1)**2 + (1 - x1)**2

#: wrap the function rosen so it can be exposed to R
rosen_for_r = pyfunc2R(rosen)

def test1(x):
    r"""A simple example. 


    .. math::

        4x^2-2.1x^4 + 1/3 * x^6+xy-4y^2+4y^4

    """
    x1 = x[0]
    x2 = x[1]
    y  = 4*x1*x1-2.1*x1**4 + 1./3.*x1**6+x1*x2-4*x2*x2+4*x2**4;

    return y

#: wrap the function test1 so it can be exposed to R
test1_for_r = pyfunc2R(test1)

