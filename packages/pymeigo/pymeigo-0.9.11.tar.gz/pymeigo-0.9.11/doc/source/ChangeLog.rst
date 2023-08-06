
Release 0.9
------------
* 0.9.11: 
    * Updates in the documentation adding unconstrained example and VNS example.
    * Remove __all__ in the init to allow **from pymeigo import *** to work again
    * rename test1 functions into example_unconstrained
* 0.9.10: 
    * installing Rsolnp package with dependencies
    * simplify the init module
* 0.9.9:
    * add MEIGO class that can run either VNS or ESS algorithms.
    * add an init module to load the R package properly
    * info function in __init__
    * wrapper has new functions wrapped (MEIGO). The R package loading is removed since it is now in init.py module.
* 0.9.8: add VNS class and rename MEIGOR into ESS class
* 0.9.7: fixing depency on rtools >2.8.0, depends on easydev not cnolab.deploy, and install Rsolnp 1.12 package if missing.
* 0.9.6: use new rtools function to automatically install MEIGOR if not already installed.
* 0.9.5: add print statement in MEIGO class + better plot method + example in doc.
* 0.9.4: use rtools instead of cnolab.wrapper
* 0.9.1: fix metadata
* 0.9.0: finalise the first robust package with proper documentation.
 
Previous releases
-------------------
* 0.3.0: cleanup doc, add MEIGO class
* 0.2.0: fixing issue related to R package
* 0.1.0: first draft of pymeigo.
