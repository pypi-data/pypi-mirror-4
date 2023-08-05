Demonstration
=============

This recipe extends on the ``zc.recipe.cmmi`` with the caveat where
cmake is called instead of the ``./configure`` scripts, yet have cmake
generate ``Unix Makefiles`` such that the ``make``/``make install`` that
cmmi calls will proceed as normal.

For the demonstration, instead of download/building the entire API, we
are going to make use of the mock-ups (which is previous setup).
::

    >>> ls(distros)
    -  cellml-api-0.0fake.tgz

    >>> distros_url = start_server(distros)
    >>> archive_url = '%scellml-api-0.0fake.tgz' % distros_url

Let's create our buildout, but modified so that we use our fake archive.
::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = cellml-api
    ...
    ... [cellml-api]
    ... recipe = cellml.recipe.api
    ... api-version = 0.0fake
    ... """)

As our mocked up api version is not listed as an available version, 
buildout will die.
::

    >>> print 'start', system(buildout)
    start...
      Installing.
      Getting section cellml-api.
      Initializing part cellml-api.
    ...
    Traceback (most recent call last):
    ...
    ValueError: api-version `0.0fake` is not a supported version of...
    <BLANKLINE>

Well, since our fake version is obviously not going to be added into the
listing of supported APIs, we can still provide our url and md5sum, as
the original function provided by ``zc.recipe.cmmi`` is still in effect.
Rewrite buildout.cfg with the desired attributes.
::

    >>> try: from hashlib import md5
    ... except ImportError: from md5 import new as md5
    >>> m = md5(open(join(distros, 'cellml-api-0.0fake.tgz')
    ...             ).read()).hexdigest()
    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = cellml-api
    ...
    ... [cellml-api]
    ... recipe = cellml.recipe.api
    ... url = %s
    ... md5sum = %s
    ... """ % (archive_url, m))

    >>> print 'start', system(buildout)
    start...
    ...
    CMake Warning:
      Manually-specified variables were not used by the project:
    <BLANKLINE>
        CHECK_BUILD
        ENABLE_ANNOTOOLS
        ENABLE_CCGS
        ENABLE_CELEDS
        ENABLE_CELEDS_EXPORTER
        ENABLE_CEVAS
        ENABLE_CIS
        ENABLE_CUSES
        ENABLE_EXAMPLES
        ENABLE_GSL_INTEGRATORS
        ENABLE_MALAES
        ENABLE_PYTHON
        ENABLE_RDF
        ENABLE_SPROS
        ENABLE_SRUS
        ENABLE_TELICEMS
        ENABLE_VACSS
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>

