# -*- python -*-
#
#  This file is part of the pymeigo software
#
#  Copyright (c) 2011-2012 - EBI, EMBL
#
#  File author(s): (cokelaer@ebi.ac.uk)
#
#  Distributed under the GPLv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  pymeigo: http://www.ebi.ac.uk/~cokelaer/pymeigo
#
##############################################################################
"""Provide a Python interface to MEIGO (a R package).

::

    >>> pymeigo import essR, rosen_for_r
    >>> data = essR(f=rosen_for_r, x_L=[-1,-1], x_U=[2,2,])


The full documentation of the essR function comes from the R package itself.


The are two sets of parameters. See :func:`set_problem_options` and
:func:`ssm_default`.


"""
__author__ = """\n""".join(['Thomas Cokelaer <cokelaer@ebi.ac.uk'])
__revision__ = "$Rev: 3116 $"

# Use Rnames2attributes decorator to ease the access to R names
from rtools import *

__all__  = ['essR', 'ssm_default', 'set_problem_options', 
'rvnds_hamming']

import os
from rpy2 import robjects
from rpy2.robjects.packages import importr

from rtools import RPackage, biocLite, install_packages

#http://www.ebi.ac.uk/saezrodriguez/cno/downloads/MEIGOR_0.99.3_svn2719.tar.gz
r = RPackage("MEIGOR", require="0.9.3", install=True) # will try bioconductor
if r.package == None:
    # could not be found. Not installed ? Let us download it
    import logging
    logging.warning("MEIGOR not found on your system")
    logging.warning("Installing MEIGOR (R packages) and Rsolnp dependency")
    # install dependencies
    RPackage("Rsolnp", require="1.12", install=True) # will try bioconductor
    # install MEIGOR from source
    install_packages("http://www.ebi.ac.uk/saezrodriguez/cno/downloads/MEIGOR_0.99.3_svn2719.tar.gz")
    r = RPackage("MEIGOR", require="0.9.3")
    if r.package == None:
        # could not install or find the MEIGOR package.
        pass


    
rpack_MEIGOR = r.package



def Rsetdoc(f):
    """Decorator that copy the R doc into the wrapped Python function.

    .. note:: function to be used for developers only as a decorator to
       R function.

    """
    name = f.__name__
    doc = buildDocString("MEIGOR", name)
    if f.__doc__:
        f.__doc__ += doc
    else:
        f.__doc__ = doc
    return f




def set_problem_options(f=None, x_L=[], x_U=[], x_0=None, f_0=None, neq=None, c_L=None,
c_U=None, int_var=None, bin_var=None, vtr=None, **kargs):
    """INPUT PARAMETERS:

    :param f: Name of the file containing the objective  function (String)
    :param x_L: Lower bounds of decision variables (vector)
    :param x_U: Upper bounds of decision variables (vector)
    :param x_0: Initial point(s) (optional; vector or matrix)
    :param f_0: Function values of initial point(s) (optional)

    .. note:: The dimension of f_0 and x_0 may be different. For example, if
        we want to introduce 5 initial points but we only know the values
        for 3 of them, x_0 would have 5 rows whereas f_0 would have only 3
        elements. In this example, it is mandatory that the first 3 
        rows of x_0 correspond  to the values of f_0
      
    Additionally, fill the following fields if your problem has non-linear constraints
     
    :param neq: Number of equality constraints (Integer; do not define it if there are no equality constraints)
    :param c_L: Lower bounds of nonlinear inequality constraints (vector)
    :param c_U: Upper bounds of nonlinear inequality constraints (vector)
    :param int_var: Number of integer variables (Integer)
    :param bin_var: Number of binary variables  (Integer)
    :param vtr: Objective function value to be reached opional)
    """


    p = {}

    if f:
        p['f'] = f
    else:
        raise ArgError("f must be provided.")
    p['x_L'] = robjects.FloatVector(x_L)
    p['x_U'] = robjects.FloatVector(x_U)

    if x_0:
        p['x_0'] = x_0

    if f_0:
        p['f_0'] = f_0

    if neq:
        p['neq'] = neq

    if c_L: p['c_L']= c_L
    if c_U: p['c_U'] = c_U
    if int_var: p['int_var'] = int_var
    if bin_var: p['bin_var'] = bin_var
    if vtr: p['vtr'] = vtr
    return robjects.ListVector(p)

def ssm_default():
    """Return the default parameters required by the SSM algorithm.

     List containing options (if set as opts <- numeric(0) default options
     will be loaded). See the script of default options to know their values
  
     :User options:

       * maxeval = Maximum number of function evaluations  (Default 1000)
       * maxtime = Maximum CPU time in seconds (Default 60)
       * iterprint  = Print each iteration on screen: 0-Deactivated 1-Activated (Default 1)
       * weight     = Weight that multiplies the penalty term added to the objective function in constrained  problems (Default 1e6)
       * log_var    = Indexes of the variables which will be used to generate diverse solutions in different  orders of magnitude (vector)
       * tolc       = Maximum absolute violation of theconstraints  (Default 1e-5)
       * prob_bound = Probability (0-1) of biasing the search towards  the bounds (Default 0.5)
       * inter_save = Saves results of intermediate iterations in eSSR_report.RData Useful for very long runs. (Binary; Default = 0)

     :Global options:

       * dim_refset: Number of elements in Refset (Integer; automatically calculated)
       * ndiverse:  Number of solutions generated by the diversificator (Default 10*nvar)
       * combination: Type of combination of Refset elements (Default 1)
            #. hyper-rectangles
            #. linear combinations

    :Local options:
       *  local_solver: Choose local solver  0: Local search deactivated (Default), "NM", "BFGS", "CG", "LBFGSB", "SA","SOLNP", "DHC", "NLS2SOL"
       * local_tol: Level of tolerance in local search
       * local_iterprint: print each iteration of local solver on screen (Binary; default = 0)
       * local_n1: Number of iterations before applying local search for the 1st time (Default 1)
       * local_n2: Minimum number of iterations in the global phase between 2 local calls (Default 10)
       * local_balance: Balances between quality (=0) and diversity (=1) for choosing initial points for  the local search (default 0.5)
       * local_finish: Applies local search to the best solution found once the optimization if finished (same values as opts.local.solver)
       * local_bestx: When activated (i.e. =1) only applies local search to the best solution found to date,ignoring filters (Default=0)
    """
    return rpack_MEIGOR.ssm_defaults()

def _get_opts(**kargs):
    """scan all ssm_Default values"""
    defaults = ssm_default()
    o = {}
    for x in defaults.names:
        o[x] = kargs.get(x, defaults.rx2(x)) # 1000
    print o
    return robjects.ListVector(o)

@Rsetdoc
@Rnames2attributes
def essR(**kargs):
    problem = set_problem_options(**kargs)
    opts = _get_opts(**kargs)
    """
    problem<-list(f="ex1",x_L=rep(-1,2),x_U=rep(1,2))
    opts<-list(maxeval=500, ndiverse=10, dim_refset=4, local_solver="solnp",
    local_n2=1)
    #========================= END OF PROBLEM SPECIFICATIONS =====================
    Results<-essR(problem,opts);
    """
    return rpack_MEIGOR.essR(problem, opts)

essR.__doc__ = """This is an automatic scan of the R manual. Layout may not be
perfect...Please have a look at :func:`ssm_default` and
:func:`set_problem_options`.\n\n""" + essR.__doc__

def vns_default():
    """vns default parameters

    Assings default values for all the options

    * maxeval = Maximum number of function evaluations (1000)
    * maxtime =  Maximum CPU time (default is 60 seconds)
    * maxdist: Percentage of the problem dimension which will be perturbed in the
        furthest neighborhood (vary between 0-1) (default is 0.5)
    * use_local: Uses local search (1) or not (0)
   
    The following options only apply if use_local is active

    * aggr: Aggressive search. The local search is only applied when the best
        solution has been improved (1=aggressive search    , 0=non-aggressive
        search).
    * local_search_type: Applies a first (=1) or a best (=2) improvement scheme
        for the local search.
    * decomp  Decompose the local search (=1) using only the variables perturbed
        in the global phase.
    """
    return rpack_MEIGOR.vns_defaults()

def _get_vns_opts(**kargs):
    defaults = vns_default()
    o = {}
    for x in defaults.names:
        o[x] = kargs.get(x, defaults.rx2(x)) # 1000
    print o
    return robjects.ListVector(o)


@Rsetdoc
@Rnames2attributes
def rvnds_hamming(**kargs):
    problem = set_problem_options(**kargs)
    opts = _get_vns_opts(**kargs)
    return rpack_MEIGOR.rvnds_hamming(problem, opts)

rvnds_hamming.__doc__ = """This is an automatic scan of the R manual. Layout may not be
perfect...Please have a look at :func:`ssm_default` and
:func:`set_problem_options`.\n\n""" + rvnds_hamming.__doc__

