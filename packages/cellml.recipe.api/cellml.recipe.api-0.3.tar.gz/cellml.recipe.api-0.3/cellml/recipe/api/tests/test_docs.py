# -*- coding: utf-8 -*-
"""
Doctest runner for 'cellml.recipe.api'.
"""
__docformat__ = 'restructuredtext'

import os.path
import tarfile
import StringIO

import unittest
import zc.buildout.tests
import zc.buildout.testing

from zope.testing import doctest, renormalizing

optionflags =  (doctest.ELLIPSIS |
                doctest.NORMALIZE_WHITESPACE |
                doctest.REPORT_ONLY_FIRST_FAILURE)

def setUp(test):
    import zc.recipe.cmmi
    zc.buildout.testing.buildoutSetUp(test)

    # Install the recipe in develop mode
    zc.buildout.testing.install_develop('cellml.recipe.api', test)

    # Install any other recipes that should be available in the tests
    zc.buildout.testing.install_develop('zc.recipe.cmmi', test)

    distros = test.globs['distros'] = test.globs['tmpdir']('distros')
    tarpath = os.path.join(distros, 'cellml-api-0.0fake.tgz')
    tar = tarfile.open(tarpath, 'w:gz')

    cmakelists_txt = cmakelists_txt_template
    info = tarfile.TarInfo('CMakeLists.txt')
    info.size = len(cmakelists_txt)
    info.mode = 0644
    tar.addfile(info, StringIO.StringIO(cmakelists_txt))


def test_suite():
    suite = unittest.TestSuite((
            doctest.DocFileSuite(
                '../README.rst',
                setUp=setUp,
                tearDown=zc.buildout.testing.buildoutTearDown,
                optionflags=optionflags,
                checker=renormalizing.RENormalizing([
                        # If want to clean up the doctest output you
                        # can register additional regexp normalizers
                        # here. The format is a two-tuple with the RE
                        # as the first item and the replacement as the
                        # second item, e.g.
                        # (re.compile('my-[rR]eg[eE]ps'), 'my-regexps')
                        zc.buildout.testing.normalize_path,
                        ]),
                ),
            ))
    return suite

cmakelists_txt_template = """\
CMAKE_MINIMUM_REQUIRED(VERSION 2.8)
PROJECT(HELLO)
INSTALL(TARGETS DESTINATION)
"""

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
