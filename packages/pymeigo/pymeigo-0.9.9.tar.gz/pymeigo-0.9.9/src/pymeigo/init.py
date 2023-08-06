# -*- python -*-
#
#  This file is part of pymeigo software
#
#  Copyright (c) 2011-2012 - EBI-EMBL
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

import rtools
from rtools import install_packages, RPackage


def load():
    """Load MEIGOR 

    Tries to install dependencies if missing

    """
    dependencies = ["Rsolnp"]
    # install dependencies
    for dep in dependencies:
        # can we find it ?
        status = RPackage(dep)
        if status.package == None:
            # no, so let us install it.
            install_packages(dep)
            status = RPackage(dep)
            if status.package == None:
                raise Exception

    status = RPackage("MEIGOR", require="0.9.4") # will try
    if status.package == None:
        install_packages("http://www.cellnopt.org/downloads/MEIGOR_0.99.4_svn3188.tar.gz")
        status = RPackage("MEIGOR", require="0.9.4") # will try
        if status.package == None:
            raise Exception("could not find or install MEIGOR")
            return False
        else:
            return True



