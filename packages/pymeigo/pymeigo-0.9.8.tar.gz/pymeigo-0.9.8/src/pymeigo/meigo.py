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
# $Id: meigo.py 3116 2013-01-04 16:09:22Z cokelaer $
"""Provide a class to run MEIGO optimisation (ESS and VNS algorithms)"""

import os
import copy
import time
from os.path import join as pj

from rpy2 import robjects

from wrapper_meigo import essR, rvnds_hamming
from pylab import *


__all__ = ["ESS", "VNS"]




class MEIGO(object):
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
        self.algorithm = algorithm

        self.func = f
        self.res = None

    def _get_algo(self):
        return self._algorithm
    def _set_algo(self, algo):
        if algo not in MEIGO._valid_algo:
            raise ValueError("algorithm must be one of %s" % str(MEIGO._valid_algo))
        self._algorithm = algo
    algorithm = property(_get_algo, _set_algo)

    def run(self, x_U=[2,2], x_L=[-1,-1], **kargs):
        """
        :param x_U: upper limit of the parameter
        :param x_U: lower limit of the parameter
        :param bin_var: number of variables of binary type 

        see :func:`~pymeigo.wrapper_meigo.essR` for arguments.

        """
        self.x_U = x_U
        self.x_L = x_L
        self.res =  essR(f=self.func, x_U=x_U, x_L=x_L, **kargs)


    def plot(self):
        """plotting the evolution of the cost function"""

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

        figure(1)
        xlabel("Evaluation")
        ylabel("Cost function")
        semilogy(list(neval), list(score), 'o-')
        xlabel("Evaluation")
        grid()


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


class ESS(MEIGO):
    def __init__(self, f):
        super(ESS, self).__init__("ESS", f)
 
    def run(self, x_U=[2,2], x_L=[-1,-1], **kargs):
        """
        :param x_U: upper limit of the parameter
        :param x_U: lower limit of the parameter
        :param bin_var: number of variables of binary type 

        see :func:`~pymeigo.wrapper_meigo.essR` for arguments.

        """
        self.x_U = x_U
        self.x_L = x_L
        self.res =  essR(f=self.func, x_U=x_U, x_L=x_L, **kargs)


class VNS(MEIGO):
    def __init__(self, f):
        super(VNS, self).__init__("VNS", f)
 
    def run(self, x_U=[2,2], x_L=[-1,-1], **kargs):
        """
        :param x_U: upper limit of the parameter
        :param x_U: lower limit of the parameter
        :param bin_var: number of variables of binary type 

        see :func:`~pymeigo.wrapper_meigo.essR` for arguments.

        """
        self.x_U = x_U
        self.x_L = x_L
        self.res =  rvnds_hamming(f=self.func, x_U=x_U, x_L=x_L, **kargs)


