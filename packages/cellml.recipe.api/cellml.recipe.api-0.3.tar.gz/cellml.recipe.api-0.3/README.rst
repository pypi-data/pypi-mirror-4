Overview
========

This is the recipe that will build the CellML API Python bindings with
all options enabled by default.  Currently, there are some limitations,
such as all dependencies required to build the CellML API must be
installed before this recipe can be used, and I don't think this will
work under Windows at the moment.


Supported options
=================

The recipe supports the following options:

api-version
    CellML API version to build.  Valid versions any versions that build
    via CMake and has Python bindings (>1.10), and must be present in
    the list of valid versions.

cmake-generator
    The generator to use.  Only the default option ``Unix Makefiles`` is
    supported, as this recipe is built on top of ``zc.recipe.cmmi`` 
    which will make use of ``make`` and ``make install``.

check-build
    Whether to check build time dependencies.  Default is off because it
    didn't detect GSL libraries even though it was installed for me.
    Same as passing ``-DCHECK_BUILD:BOOL=OFF`` to ``cmake``.

Other supported options:

    - enable-examples
    - enable-annotools
    - enable-ccgs
    - enable-celeds
    - enable-celeds-exporter
    - enable-cevas
    - enable-cis
    - enable-cuses
    - enable-gsl-integrators
    - enable-malaes
    - enable-python
    - enable-rdf
    - enable-spros
    - enable-srus
    - enable-telicems
    - enable-vacss

Please refer to the `CellML API Documentations`_ for what these options
do.

.. _CellML API Documentations: http://cellml-api.sourceforge.net/


Usage
=====

As this egg is published on `pypi`_, this recipe can be used right away
by including a new part inside a ``buildout.cfg``.  The following is an
example configuration:

.. _pypi: http://pypi.python.org/

::

    [buildout]
    parts = 
        ...
        cellml-api
        cellmlpy

    [cellml-api]
    recipe = cellml.recipe.api
    api-version = 1.10   

    [cellmlpy]
    recipe = zc.recipe.egg
    eggs = 
    interpreter = cellmlpy
    scripts = cellmlpy
    extra-paths = ${cellml-api:location}/lib/python

This example ``buildout.cfg`` will build the CellML API v1.10 with all
the supported options enabled, and a script will be generated in
``bin/cellmlpy`` which will allow the bindings to be imported without
setting ``PYTHONPATH`` and other related environmental variables.
Please refer to the examples directory for more detailed instructions
and other example usages of this recipe.


Copyright/License information
=============================

This software is released under the MPL/GPL/LGPL licenses.

Please refer to the file ``COPYING.txt`` for detailed copyright
information, and ``docs`` directory for specific licenses that this
software is released under.
