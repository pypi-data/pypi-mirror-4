# -* python -*-
#
#  This file is part of the CNO software
#
#  Copyright (c) 2011-2012 - EBI
#
#  File author(s): Thomas Cokelaer <cokelaer@ebi.ac.uk>
#
#  Distributed under the GPLv2 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-2.0.html
#
#  CNO website: http://www.ebi.ac.uk/saezrodriguez/software.html
#
##############################################################################
# $Id: meigo.py 3202 2013-01-29 16:06:10Z cokelaer $
"""Provide a class to run MEIGO optimisation (ESS and VNS algorithms)"""

import os
import copy
import time
from os.path import join as pj
import wrapper_meigo


__all__ = ["ESS", "VNS",  "MEIGO"]




class MEIGObase(object):
    """class ESS around :mod:`pymeigo.wrapper_meigo`


    .. plot::
        :include-source:

        from pymeigo import ESS, rosen_for_r
        m = ESS(f=rosen_for_r)
        m.run(x_U=[2,2], x_L=[-1,-1])
        m.plot()

    """
    _valid_algo = ["VNS", "ESS"]
    def __init__(self, algorithm, f):
        """
        :param f: a R version of a python function. See :mod:`~pymeigo.funcs.pyfunc2R`.
        """
        self._algorithm = None
        self._set_algo(algorithm)

        self.func = f
        self.res = None

    def _get_algo(self):
        return self._algorithm
    def _set_algo(self, algo):
        if algo not in MEIGO._valid_algo:
            raise ValueError("algorithm must be one of %s" % str(MEIGO._valid_algo))
        self._algorithm = algo
    algorithm = property(_get_algo, doc="Returns optimisation algorithm")

    def run(self, x_U=[2,2], x_L=[-1,-1], **kargs):
        raise NotImplementedError

    def plot(self):
        """plotting the evolution of the cost function"""
        try:
            import pylab
        except ImportError, e:
            print("You must install pylab to access to this function. pylab was not found on your system")
        try:
            score = self.res.f # for the ESS case
        except:
            score = self.res.func # for the VNS case


        x = self.res.x
        time = self.res.time
        neval = self.res.neval
        fbest = self.res.fbest
        xbest = self.res.xbest
        numeval = self.res.numeval
        try:
            end_crit = self.res.end_crit    

        except:
            pass
        try:
            cpu_time = self.res.cpu_time
        except:pass
        try:refset = self.res.Refset
        except:pass

        pylab.figure(1)
        pylab.xlabel("Evaluation")
        pylab.ylabel("Cost function")
        pylab.semilogy(list(neval), list(score), 'o-')
        pylab.xlabel("Evaluation")
        pylab.grid()


    def __str__(self):
        """Print same message as .

        The difference is that Mean is not stored so it is not shown in this print statement
        """
        if self.res == None:
            txt = "No results stored. Please, call run() method."
            return txt
        else:
            pass # continue


        time = list(self.res.time)
        neval = list(self.res.neval)
        try:
            bestf = list(self.res.f)
        except:
            bestf = list(self.res.func)


        txt = ""
        txt += "Refset size automatically calculated: XX\n" 
        txt += "Number of diverse solutions automatically calculated: XX \n"


        for i, x in enumerate(list(self.res.neval)):
            if i == 0:
                txt += "Initial Pop: "
            else:
                txt += "Iteration %s " % i
            txt += "NFunEvals: %s Bestf: %s CPUTime: %s Mean: %s \n" % (neval[i], bestf[i], time[i], 0)

        print("\n\n")
        try:
            if self.res.end_crit[0] == 1:
                txt += "Maximum number of function evaluations achieved \n"
        except:pass
        txt += "Best solution value %s \n" % self.res.fbest[0]
        txt += "Decision vector %s %s \n" % (self.res.xbest[0], self.res.xbest[1])
        try:
            txt += "CPU time %s \n" % self.res.cpu_time[0]
        except:pass
        txt += "Number of function evaluations %s \n" %self.res.numeval[0]
        return txt


class ESS(MEIGObase):
    """Interface to the ESS algorithm


    ::

        from pymeigo import ESS, rosen_for_r
        m = ESS(f=rosen_for_r)
        m.run(x_U=[2,2], x_L=[-1,-1])
        m.plot()

    .. seealso:: :class:`~pymeigo.meigo.MEIGO`
    """
    def __init__(self, f):
        """.. rubric:: Constructor

        :param str f: the objective function
        """
        super(ESS, self).__init__("ESS", f)

    def run(self, x_U=[2,2], x_L=[-1,-1], **kargs):
        """Runs the optimisation

        :param x_U: upper limit of the parameter
        :param x_U: lower limit of the parameter
        :param bin_var: number of variables of binary type 

        :return: an object containing the results of the optimisation. See
            :class:`~pymeigo.meigo.MEIGO` for details.

        .. seealso:: :func:`~pymeigo.wrapper_meigo.set_problem_options` for
            arguments related to the objective function.

        .. seealso:: :func:`~pymeigo.wrapper_meigo.ssm_default` for arguments
            related to SSM algorithm.

        """
        self.x_U = x_U
        self.x_L = x_L
        self.res =  wrapper_meigo.essR(f=self.func, x_U=x_U, x_L=x_L, **kargs)


class VNS(MEIGObase):
    """Interface to the VNS algorithm


    ::

        from pymeigo import ESS, rosen_for_r
        m = ESS(f=rosen_for_r)
        m.run(x_U=[2,2], x_L=[-1,-1])
        m.plot()

    .. seealso:: :class:`~pymeigo.meigo.MEIGO`
    """
    def __init__(self, f):
        """.. rubric:: Constructor

        :param str f: the objective function
        """
        super(VNS, self).__init__("VNS", f)
 
    def run(self, x_U, x_L, **kargs):
        """Runs the optimisation

        :param x_U: upper limit of the parameter
        :param x_U: lower limit of the parameter
        :param bin_var: number of variables of binary type 

        :return: an object containing the results of the optimisation. See
            :class:`~pymeigo.meigo.MEIGO` for details.

        .. seealso:: :func:`~pymeigo.wrapper_meigo.set_problem_options` for
            arguments related to the objective function.

        .. seealso:: :func:`~pymeigo.wrapper_meigo.ssm_default` for arguments
            related to SSM algorithm.

        """
        self.res =  wrapper_meigo.rvnds_hamming(f=self.func, x_U=x_U, x_L=x_L, **kargs)


class MEIGO(MEIGObase):
    """Interface to several optimisation algorithm

    ::

        from pymeigo import MEIGO, rosen_for_r
        m = MEIGO("ESS", f=rosen_for_r)
        m.run(x_U=[2,2], x_L=[-1,-1])
        m.plot()

    """

    def __init__(self, algorithm, f):
        """.. rubric:: Constructor


        :param str algorithm:  the algorithm in ["ESS", "VNS"]
        :param str f: the objective function
        """
        super(MEIGO, self).__init__(algorithm, f)


    def run(self, x_U, x_L, **kargs):
        """Runs the optimisation

        :param x_U: upper limit of the parameter
        :param x_U: lower limit of the parameter
        :param bin_var: number of variables of binary type 

        :return: an object containing the results of the optimisation. See
            :class:`~pymeigo.meigo.MEIGO` for details.

        .. seealso:: :func:`~pymeigo.wrapper_meigo.set_problem_options` for
            arguments related to the objective function.

        .. seealso:: :func:`~pymeigo.wrapper_meigo.vns_default` for arguments
            related to VNS algorithm.

        .. seealso:: :func:`~pymeigo.wrapper_meigo.ssm_default` for arguments
            related to SSM algorithm.

        """
        self.res = wrapper_meigo.MEIGO(self.algorithm, f=self.func, x_U=x_U, 
            x_L=x_L, **kargs)
