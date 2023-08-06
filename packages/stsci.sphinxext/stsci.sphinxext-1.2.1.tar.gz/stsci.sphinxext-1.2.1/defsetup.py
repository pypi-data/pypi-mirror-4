from __future__ import division # confidence high
import os
import shutil

import distutils.extension
pkg = ["stsci", "stsci.sphinxext"]

setupargs = {
    'version' :         '1.2',
    'description' :
        'A set of tools and templates to customize Sphinx for use in STScI projects',

    'long_description' :
'''In short, you use this package by adding 'from stsci_docs.conf
import *' to the top of your conf.py in your Sphinx documentation
source tree.  In long, see the README file.''',

    'author' :          'Michael Droettboom',

    'author_email' :    'mdroe@stsci.edu',

    'url' :             '',

    'scripts' :         [],

    'license' :         'BSD',

    'platforms' :       ["Linux", "Solaris", "Mac OS X", "Win"],

    'package_dir':      { 'stsci' : 'lib/stsci', 'stsci.sphinxext' : 'lib/stsci/sphinxext'  },

    # how to install your data files:
    #   [
    #       ( directory_name_files_go_to, [ file_name_in_source_tree, another_data_file, etc ] )
    #   ]
    'data_files' :      [
                ( 'stsci/sphinxext/stsci_sphinx_theme', [ 'lib/stsci/sphinxext/stsci_sphinx_theme/theme.conf' ] ),
                ( 'stsci/sphinxext/stsci_sphinx_theme/static', [ 'lib/stsci/sphinxext/stsci_sphinx_theme/static/*' ] ),
                ( 'stsci/sphinxext/latex', [ 'lib/stsci/sphinxext/latex/*' ] ),
                ],

    'package_data' :      {
                'stsci.sphinxext': [ 'stsci_sphinx_theme/theme.conf', 'stsci_sphinx_theme/static/*', 'latex/*' ] }
}
