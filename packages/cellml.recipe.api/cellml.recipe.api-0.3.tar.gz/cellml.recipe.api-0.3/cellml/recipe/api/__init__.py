# -*- coding: utf-8 -*-
"""Recipe api"""

import zc.recipe.cmmi

_api_info = {
    '1.10': (
        'http://sourceforge.net/projects/cellml-api/files/CellML-API-Nightly/1.10/20110913/src/cellml-api-1.10.tar.bz2/download',
        '37a2cf957e9db43e21c9e43f6ec3b17f',
    ),
    '1.11': (
        'http://sourceforge.net/projects/cellml-api/files/CellML-API-Nightly/1.11/20120418/src/cellml-api-1.11.tar.bz2/download',
        '64d608890cdf1d421dc66b933729556d',
    ),
}
latest = '1.11'

def get_api_info(version=latest):
    info = _api_info.get(version, None)
    if info is None:
        raise ValueError(
            'api-version `%s` is not a supported version of CellML API.' 
            % version
        )
    return info


class Recipe(zc.recipe.cmmi.Recipe):
    """\
    CellML API recipe.

    Largely built on top of `zc.recipe.cmmi`.
    """

    option_passthru_keys = [
        'url',  # user might have their own source tarball
        'md5sum',  # and respective md5sum
        'autogen',  # XXX to be ignored because autogen is not used.
        'patch',
        'patch_options',
        'environment',
        'configure-options',  # this gets processed first
    ]

    option_cmake_map = {
        'check-build': 'off',
        'enable-examples': 'on',
        'enable-annotools': 'on',
        'enable-ccgs': 'on',
        'enable-celeds': 'on',
        'enable-celeds-exporter': 'on',
        'enable-cevas': 'on',
        'enable-cis': 'on',
        'enable-cgrs': 'on',
        'enable-cuses': 'on',
        'enable-gsl-integrators': 'on',
        'enable-malaes': 'on',
        'enable-python': 'on',
        'enable-rdf': 'on',
        'enable-spros': 'on',
        'enable-srus': 'on',
        'enable-telicems': 'on',
        'enable-vacss': 'on',
    }

    def __init__(self, buildout, name, options):
        self.original_options = options

        # build a set of modified options customized for this.
        api_options = {}
        # populate it with values that we need to passthrough

        for k in self.option_passthru_keys:
            value = options.get(k, None)
            if value is not None:
                # let parent deal with anything missing.
                api_options[k] = value

        self.api_version = options.get('api-version', None)
        self.cmake_generator = options.get('cmake-generator', 'Unix Makefiles')

        if api_options.get('url', None) is None:
            # if user did not specified a specific url we assume to
            # check for a version.
            api_options['url'], api_options['md5sum'] = get_api_info(
                self.api_version)

        api_options['source-directory-contains'] = options.get(
            'source-directory-contains', 'CMakeLists.txt')
        api_options['configure-command'] = options.get(
            'configure-command', 'cmake')

        # construct extra options
        extra_options = self.build_options(self.cmake_generator, options)
        api_options['extra_options'] = extra_options

        # continue on with the parent, with our modified options.
        super(Recipe, self).__init__(buildout, name, api_options)

        # Since we did create and pass in a completely new dictionary
        # into super class, the location value needs to be assigned
        # back into here too.
        options['location'] = api_options['location']

    def build_options(self, cmake_generator, options):
        results = []
        results.append("-G '%s'" % cmake_generator)
        for k, v in self.option_cmake_map.iteritems():
            # convert to cmake keys.
            confkey = k.replace('-', '_').upper()
            results.append('-D%s:BOOL=%s' % (confkey, options.get(k, v)))

        # construct the `extra_options` string
        return ' '.join(results)

    def cmmi(self, dest):
        if self.configure_options is None:
            # unless it got assigned earlier
            self.configure_options = \
                '-DCMAKE_INSTALL_PREFIX:PATH=%s ' \
                '-DCMAKE_INSTALL_RPATH:PATH=%s/lib' % (dest, dest)

        return super(Recipe, self).cmmi(dest)
