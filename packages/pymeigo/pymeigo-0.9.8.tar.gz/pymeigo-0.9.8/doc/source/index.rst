

#############################
PYMEIGO documentation
#############################

Overview
############

`pymeigo <http://pypi.python.org/pypi/pymeigo>`_  is a python package that provides a python interface to the optimisation tool MEIGOR, which
is a R package available at http://www.iim.csic.es/~gingproc/meigo.html. The original R package provides a scatter search optimisation that is dedicated to the optimisation of R functions. **pymeigo** provides an easy way to use MEIGOR within python so as to optimise python functions as well.



.. _installation:

Installation
##################

Since **pymeigo** is available on `PyPi <http://pypi.python.org/>`_, the following command should install **pymeigo** and its
dependencies automatically::

    easy_install pymeigo


Ideally, you should have installed **MEIGOR** (the R package). Please see `MEIGOR page <http://www.iim.csic.es/~gingproc/meigo.html>`_ for up-to-date versions or
`CellNOpt page <http://www.ebi.ac.uk/saezrodriguez/cno/downloads.html>`_. 

Nevertheless, the first time you use **pymeigo**, it will install the following version automatically if
MEIGOR is not found on your system::

    http://www.ebi.ac.uk/saezrodriguez/cno/downloads/MEIGOR_0.99.3_svn2719.tar.gz; 

If you want to install the R package yourself, under Linux, type something like::

        wget http://www.ebi.ac.uk/saezrodriguez/cno/downloads/MEIGOR_0.99.1_svn2071.tar.gz; 
        R CMD INSTALL MEIGOR_0.99.1_svn2071.tar.gz


Jump to the quickstart section to have a go.

User guide
##################


.. toctree::
    :maxdepth: 2
    :numbered:

    quickstart.rst


References
##################


.. toctree::
    :maxdepth: 2
    :numbered:

    references


Citations
################

If you use essR and publish the results, please cite the following papers: 

#. Egea, J.A., Maria, R., Banga, J.R. (2010) An evolutionary method for complex-process optimization. Computers & Operations Research 37(2): 315-324. 
#. Egea, J.A., Balsa-Canto, E., Garcia, M.S.G., Banga, J.R. (2009) Dynamic optimization of nonlinear processes with an enhanced scatter search method. Industrial & Engineering Chemistry Research 49(9): 4388-4401.
