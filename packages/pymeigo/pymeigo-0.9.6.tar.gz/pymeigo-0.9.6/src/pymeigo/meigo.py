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
# $Id: meigo.py 2806 2012-11-21 15:14:21Z cokelaer $
"""Provide a class to run MEIGO optiisation


"""
import os
import copy
import time
from os.path import join as pj

from rpy2 import robjects

from wrapper_meigo import essR
from pylab import *
__all__ = ["MEIGO"]



class MEIGO(object):
    """class MEIGO around :mod:`pymeigo.wrapper_meigo`


    .. plot::
        :include-source:

        from pymeigo import MEIGO, rosen_for_r
        m = MEIGO(f=rosen_for_r)
        m.run(x_U=[2,2], x_L=[-1,-1])
        m.plot()

    """
    def __init__(self, f):
        """
        :param f: a R version of a python function. See :mod:`~pymeigo.funcs.pyfunc2R`.
        """


        self.func = f
        self.res = None

    def run(self, x_U=[2,2], x_L=[-1,-1], **kargs):
        """


        :param x_U: upper limit of the parameter
        :param x_U: lower limit of the parameter

        see :func:`~pymeigo.wrapper_meigo.essR` for arguments.

        """
        self.x_U = x_U
        self.x_L = x_L
        self.res =  essR(f=self.func, x_U=x_U, x_L=x_L, **kargs)
        

    def plot(self):
        """plotting the evolution of the cost function"""

        score = self.res.f
        x = self.res.x
        time = self.res.time
        neval = self.res.neval
        fbest = self.res.fbest
        xbest = self.res.xbest
        numeval = self.res.numeval
        end_crit = self.res.end_crit
        cpu_time = self.res.cpu_time
        refset = self.res.Refset

        figure(1)
        xlabel("Evaluation")
        ylabel("Cost function")
        semilogy(list(self.res.neval), list(self.res.f), 'o-')
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
        bestf = list(self.res.f)

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
        if self.res.end_crit[0] == 1:
            txt += "Maximum number of function evaluations achieved \n"
        txt += "Best solution value %s \n" % self.res.fbest[0]
        txt += "Decision vector %s %s \n" % (self.res.xbest[0], self.res.xbest[1])
        txt += "CPU time %s \n" % self.res.cpu_time[0]
        txt += "Number of function evaluations %s \n" %self.res.numeval[0]
        return txt
