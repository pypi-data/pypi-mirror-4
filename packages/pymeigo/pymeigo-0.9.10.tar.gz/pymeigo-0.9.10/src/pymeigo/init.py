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


def install():
    pm = rtools.RPackageManager()
    pm.install_packages(["Rsge", "snowfall", "Rsolnp"], repos=None)
    if "MEIGOR" not in pm.installed['Package']:
        pm.install_packages("http://www.cellnopt.org/downloads/MEIGOR_0.99.6_svn3222.tar.gz",
            type="source")



