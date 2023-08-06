# -*- python -*-
#
#  This file is part of pymeigo software
#
#  Copyright (c) 2012-2013 - EBI-EMBL
#
#  File author(s): Thomas Cokelaer <cokelaer@ebi.ac.uk>
#
#  Distributed under the GPLv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  website: http://www.ebi.ac.uk/~cokelaer/pymeigo
#
##############################################################################
"""This module provides some function to play with


"""

from rpy2.robjects.vectors import FloatVector
from rpy2.robjects.packages import importr
import rpy2.rinterface as ri
#stats = importr('stats')


__all__ = ["pyfunc2R", "rosen", "example_unconstrained", "rosen_for_r", 
    "example_unconstrained_for_r"]


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

def example_unconstrained(x):
    r"""A unconstrained example. 

    .. math::

        4x^2 - 2.1x^4 + 1/3 * x^6 + xy - 4y^2 + 4y^4

    """
    x1 = x[0]
    x2 = x[1]
    y  = 4*x1*x1-2.1*x1**4 + 1./3.*x1**6+x1*x2-4*x2*x2+4*x2**4;

    return y

#: wrap the function test1 so it can be exposed to R
example_unconstrained_for_r = pyfunc2R(example_unconstrained)



def _example_constrained(x):
    r"""Constrained example

    .. math:: 

        f(x) = -x_1 -x_2

    subject to 
    .. math:: 

        x_2 \leq 2x_1^4 - 8 x_1^3 + 8 x_1^2\\
        
        

    """
    raise NotImplementedError
