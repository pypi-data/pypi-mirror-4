Create a sphinx project
=======================

To build the documentation you must create a sphinx project in this directory
with the 'sphinx-quickstart' command, with 'autodoc' extension enabled.
I like the 'viewcode' extension too.


Include the sphinx extensions
=============================

In order to build the ginsfsm documentation with svg graphics of smachine
you must too add the extension 'ginsfsm.sphinxext' to the created conf.py file.

The final result can be:

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'ginsfsm.sphinxext']


Include the generated rst file
==============================

You must include the generated api_xxx.rst in the Contents of index.rst:

.. toctree::
   :maxdepth: 2

   api_xxx

being xxx the name of the created project.


Don't compile sphinx?
=====================

If make html fails with the message:

   "Could not import extension ginsfsm.sphinxext"

check if the next modules are installed:

   * docutils
   * svgwrite
   * PIL
     Better install `pillow`, with pip.
     `pillow` will need libfreetype*dev and libjpeg*dev libs to compile.
