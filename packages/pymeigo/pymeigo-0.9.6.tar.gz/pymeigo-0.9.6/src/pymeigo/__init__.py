import pkg_resources
try:
    version = pkg_resources.require("pymeigo")[0].version
except:
    version = "unknown"

import logging
logging.basicConfig(level=logging.ERROR)

logging.info("Importing pymeigo %s." % version)
logging.info("==========================")
logging.info("Checking that R packages can be loaded properly.")


# http://www.ebi.ac.uk/saezrodriguez/cno/downloads/MEIGOR_0.99.3_svn2719.tar.gz

import wrapper_meigo
from wrapper_meigo import *

import funcs
from funcs import *

import meigo
from meigo import *
